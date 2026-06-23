from fastapi import FastAPI

from student_service.student_data import (
    get_recent_scores,
    get_student_courses,
    get_student_profile,
    get_student_summary,
    get_upcoming_exams,
)


app = FastAPI(
    title="Student Data Service",
    description="Single-student structured data service for the AI Student Study Tracker demo.",
    version="0.1.0",
)


@app.get("/")
def service_index():
    return {
        "service": "student-data-service",
        "student_id": get_student_profile()["student_id"],
        "endpoints": [
            "GET /student",
            "GET /student/courses",
            "GET /student/exams",
            "GET /student/scores",
        ],
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "student-data-service",
    }


@app.get("/student")
def student():
    return get_student_summary()


@app.get("/student/courses")
def student_courses():
    return {
        "student_id": get_student_profile()["student_id"],
        "courses": get_student_courses(),
    }


@app.get("/student/exams")
def student_exams():
    return {
        "student_id": get_student_profile()["student_id"],
        "upcoming_exams": get_upcoming_exams(),
    }


@app.get("/student/scores")
def student_scores():
    return {
        "student_id": get_student_profile()["student_id"],
        "recent_scores": get_recent_scores(),
    }
