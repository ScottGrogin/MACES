import requests
from settings import APP_IDENTIFIER, ORK_BASE_URL


HEADERS = {"Content-Type": "application/json"}


def build_url(endpoint: str, params: dict) -> str:
    payload = ["request=", f"call={endpoint}"]
    for k, v in params.items():
        payload.append(f"request[{k}]={v}")
    return ORK_BASE_URL + "?" + "&".join(payload)


def request(endpoint: str, params: dict = None):
    """Perform a GET request without a shared session."""
    if params is None:
        params = {}
    params[APP_IDENTIFIER] = ""
    url = build_url(endpoint, params)
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    try:
        return response.json()
    except ValueError:
        return response.text


def login(username: str, password: str):
    params = {"UserName": username, "Password": password}
    content = request("Authorization/Authorize", params)
    if type(content) != dict:
        raise TypeError("Unexpected response from ork, try again.")
    if content.get("Status", {}).get("Error") != "Success":
        raise ValueError("Could not log in, double check your credentials.")
    return {"token": content["Token"], "userId": content["UserId"]}


def get_classes():
    params = {"Active": 1}
    content = request("Attendance/GetClasses", params)
    if type(content) != dict:
        raise TypeError("Unexpected response from ork, try again.")
    if content.get("Status", {}).get("Error") != "Success":
        raise ValueError("Could not log in, double check your credentials.")
    classes = content["Classes"]
    return [{"class_id": c["ClassId"], "class_name": c["Name"]} for c in classes]


def get_player_info(token: str, user_id: int):
    params = {"Token": token, "MundaneId": user_id}
    return request("Player/GetPlayer", params)


def add_attendance(
    token: str,
    date: str,
    player_id: int,
    player_kingdom_id: int,
    class_id: int,
    num_credits: int,
    host_park: int,
):
    params = {
        "Token": token,
        "ClassId": class_id,
        "MundaneId": player_id,
        "Date": date,
        "Credits": num_credits,
        "ParkId": host_park,
        "KingdomId": player_kingdom_id,
        "EventCalendarDetailId": 0,
    }
    content = request("Attendance/AddAttendance", params)
    if content.get("Error") != "Success":
        raise ValueError(f"Could not enter credits. {content.get('Error')}")
    return content


def get_park_officers(park_id: int):
    params = {"ParkId": park_id}
    content = request("Park/GetOfficers", params)
    if content.get("Status", {}).get("Error") != "Success":
        raise ValueError("Could not find park officers.")
    return content


def is_park_officer(park_id: int, player_id: int) -> bool:
    officers = get_park_officers(park_id).get("Officers", [])
    officer_ids = [o["MundaneId"] for o in officers]
    return player_id in officer_ids
