from database import insert_json_data, find_rows_by_json_fields, update_json_data
from settings import ATTENDANCE_TABLE_NAME
from models import AttendanceRecord


def log_attendance(attendance: AttendanceRecord):
    insert_json_data(ATTENDANCE_TABLE_NAME, attendance.model_dump())


def get_records_with_id_for_park_day(date: str, park_id):
    filters = {"$.date": date, "$.host_park_id": park_id}
    rows = find_rows_by_json_fields(ATTENDANCE_TABLE_NAME, filters)
    return rows


def get_records_for_park_day(date: str, park_id):
    rows = get_records_with_id_for_park_day(date, park_id)
    return [row[1] for row in rows]


def update_attendance(record_id, record):
    success = update_json_data(ATTENDANCE_TABLE_NAME, record_id, record)
    return success
