from fastapi.testclient import TestClient

from student_service.student_data import STUDENT_DATA_PATH, load_student_data
from student_service.student_data_server import app


client = TestClient(app)


def test_student_data_loads_from_json_file():
    assert STUDENT_DATA_PATH.name == "student.json"
    assert STUDENT_DATA_PATH.exists()

    student_data = load_student_data()

    assert student_data["profile"]["student_id"] == "STU-101"
    assert student_data["courses"]
    assert student_data["upcoming_exams"]
    assert student_data["recent_scores"]


def test_student_data_service_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "student-data-service",
    }


def test_student_data_service_index():
    response = client.get("/")

    assert response.status_code == 200

    body = response.json()
    assert body["service"] == "student-data-service"
    assert body["student_id"] == "STU-101"
    assert "GET /student/scores" in body["endpoints"]


def test_student_summary_contains_single_student_data():
    response = client.get("/student")

    assert response.status_code == 200

    body = response.json()
    assert body["student_id"] == "STU-101"
    assert body["name"] == "Aarav Sharma"
    assert body["grade"] == "8"
    assert body["courses"]
    assert body["upcoming_exams"]
    assert body["recent_scores"]


def test_student_courses_endpoint():
    response = client.get("/student/courses")

    assert response.status_code == 200

    body = response.json()
    assert body["student_id"] == "STU-101"
    assert {
        "subject": "Mathematics",
        "teacher": "Ms. Rao",
        "current_chapter": "Linear Equations",
        "schedule": "Mon/Wed/Fri",
    } in body["courses"]


def test_student_exams_endpoint():
    response = client.get("/student/exams")

    assert response.status_code == 200

    body = response.json()
    assert body["student_id"] == "STU-101"
    assert {
        "subject": "Mathematics",
        "date": "2026-06-28",
        "topic": "Linear Equations",
        "exam_type": "Unit Test",
    } in body["upcoming_exams"]


def test_student_scores_endpoint():
    response = client.get("/student/scores")

    assert response.status_code == 200

    body = response.json()
    assert body["student_id"] == "STU-101"
    assert {
        "subject": "Mathematics",
        "assessment": "Class Test 3",
        "score": 72,
        "max_score": 100,
        "teacher_remark": "Needs more practice with word problems.",
    } in body["recent_scores"]
