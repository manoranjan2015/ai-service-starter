import json
from functools import lru_cache
from pathlib import Path
from typing import Dict


STUDENT_DATA_PATH = Path(__file__).resolve().parent / "data" / "student.json"


@lru_cache(maxsize=1)
def load_student_data() -> Dict:
    return json.loads(STUDENT_DATA_PATH.read_text(encoding="utf-8"))


def get_student_profile() -> dict:
    return load_student_data()["profile"]


def get_student_courses() -> list:
    return load_student_data()["courses"]


def get_upcoming_exams() -> list:
    return load_student_data()["upcoming_exams"]


def get_recent_scores() -> list:
    return load_student_data()["recent_scores"]


def get_student_summary() -> dict:
    student_data = load_student_data()

    return {
        **student_data["profile"],
        "courses": student_data["courses"],
        "upcoming_exams": student_data["upcoming_exams"],
        "recent_scores": student_data["recent_scores"],
    }
