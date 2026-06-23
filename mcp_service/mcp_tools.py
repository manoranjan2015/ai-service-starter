from typing import Dict

from mcp_service.student_client import fetch_student_service_json


def get_student_profile_tool() -> Dict:
    student = fetch_student_service_json("/student")

    if "error" in student:
        return student

    return {
        "student_id": student["student_id"],
        "name": student["name"],
        "grade": student["grade"],
        "school": student["school"],
        "academic_year": student["academic_year"],
    }


def get_student_courses_tool() -> Dict:
    return fetch_student_service_json("/student/courses")


def get_upcoming_exams_tool() -> Dict:
    return fetch_student_service_json("/student/exams")


def get_recent_scores_tool() -> Dict:
    return fetch_student_service_json("/student/scores")
