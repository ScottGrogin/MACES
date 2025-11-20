from flask import Flask, render_template, request, jsonify, session
from oracledb import Error
from pydantic import ValidationError
import requests
from models import (
    AttendanceGet,
    AttendanceRecord,
    AttendanceSubmission,
    LoginInfo,
    Player,
)
from site_db_operations import (
    get_records_for_park_day,
    get_records_with_id_for_park_day,
    log_attendance,
    update_attendance,
)
from pork import add_attendance, get_classes, get_player_info, is_park_officer, login
from settings import MACES_SECRET_KEY
import sys
import logging

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="logs.txt",
)


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception

app = Flask(__name__)
logging.getLogger("werkzeug").disabled = True

app.secret_key = MACES_SECRET_KEY


def _response_message(message: str):
    return {"message": message}


@app.route("/")
def home():
    return render_template("index.html", title="M.A.C.E.S")


@app.route("/login", methods=["POST"])
def proxy_login():
    data = request.get_json()
    login_info = LoginInfo(**data)
    try:
        res = login(login_info.username, login_info.password)
    except TypeError:
        return (
            jsonify(_response_message("Unexpected response from ork, try again")),
            503,
        )
    except ValueError:
        return jsonify(_response_message("Invalid username or password")), 401
    except requests.exceptions.ConnectionError:
        return jsonify(_response_message("Error connecting to ork")), 503
    session["token"] = res["token"]
    session["user_id"] = res["userId"]
    return jsonify(_response_message("login success")), 200


@app.route("/is_park_officer", methods=["GET"])
def park_officer():
    if not session.get("token"):
        return jsonify({"error": "Unauthorized"}), 401
    player_info = get_player_info(token=session["token"], user_id=session["user_id"])
    player = Player(**player_info["Player"])
    _is_park_officer = is_park_officer(
        park_id=player.ParkId,
        player_id=player.MundaneId,
    )
    return jsonify({"isOfficer": _is_park_officer, "parkId": player.ParkId}), 200


@app.route("/get_classes", methods=["GET"])
def get_playable_classes():
    if not session.get("token"):
        return jsonify({"error": "Unauthorized"}), 401
    try:
        classes = get_classes()
    except TypeError:
        return (
            jsonify(_response_message("Unexpected response from ork, try again")),
            503,
        )
    except ValueError:
        return jsonify(_response_message("Invalid username or password")), 401
    except requests.exceptions.ConnectionError:
        return jsonify(_response_message("Error connecting to ork")), 503
    return jsonify(classes), 200


@app.route("/submit_attendance", methods=["POST"])
def submit_attendance():
    if not session.get("token"):
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json()
    attendance = AttendanceSubmission(**data)
    attendance_records = get_records_with_id_for_park_day(
        attendance.date.isoformat(), attendance.host_park_id
    )
    try:
        errored_records = _attendance_submit(attendance_records, attendance.credit_data)
    except ValueError as e:
        return (jsonify(_response_message(str(e)))), 400
    if len(errored_records) > 0:
        return (jsonify({"errored_records": errored_records})), 207
    return jsonify(_response_message("attendance submitted")), 200


def _attendance_submit(attendance_records, credit_data):
    errored_records = []
    unsubmitted_records = [
        record for record in attendance_records if not record[1]["submitted"]
    ]
    for record in unsubmitted_records:
        data = {
            "token": session["token"],
            "date": record[1]["date"],
            "player_id": record[1]["player"]["MundaneId"],
            "player_kingdom_id": record[1]["player"]["KingdomId"],
            "class_id": record[1]["class_id"],
            "num_credits": _calculate_credits(record[1], credit_data),
            "host_park": record[1]["host_park_id"],
        }
        add_attendance(**data)
        record[1]["submitted"] = True
        update_attendance(record[0], record[1])

    return errored_records


def _calculate_credits(attendance_record, credit_data) -> int:
    is_player_in_person = attendance_record["attending_in_person"]
    is_player_local = (
        attendance_record["player"]["ParkId"] == attendance_record["host_park_id"]
    )

    lut = {
        (True, True): "inPersonLocal",
        (True, False): "inPersonOutPark",
        (False, True): "onlineLocal",
        (False, False): "onlineOutPark",
    }
    key = lut.get((is_player_in_person, is_player_local))
    return credit_data[key]


@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    if not session.get("token"):
        return jsonify({"error": "Unauthorized"}), 401
    lut = {"GET": _attendance_get, "POST": _attendance_post}
    return lut[request.method]()


def _attendance_get():
    try:
        query = AttendanceGet(**request.args)
    except ValidationError as e:
        return jsonify(e.errors()), 400
    try:
        records = get_records_for_park_day(query.date.isoformat(), query.host_park_id)
    except Error as e:
        return jsonify(e.errors()), 400
    return jsonify(records), 200


def _attendance_post():
    data = request.get_json()
    player_info = get_player_info(session["token"], session["user_id"])["Player"]
    data["player"] = player_info
    try:
        attendance = AttendanceRecord(**data)
    except ValidationError as e:
        return jsonify(e.errors()), 400
    records = get_records_for_park_day(
        attendance.date.isoformat(), attendance.host_park_id
    )
    for record in records:
        if record["player"]["MundaneId"] == session["user_id"]:
            return (
                jsonify(
                    _response_message(
                        "You have already submitted attendance for this event"
                    ),
                ),
                400,
            )
    try:
        log_attendance(attendance)
    except Error as e:
        return jsonify(e.errors()), 400

    return jsonify(_response_message("Attendance recorded successfully")), 201


if __name__ == "__main__":
    app.run()
