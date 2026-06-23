STUDENT_PROFILE = {
    "student_id": "STU-101",
    "name": "Aarav Sharma",
    "grade": "8",
    "school": "Demo Public School",
    "academic_year": "2026",
}

STUDENT_COURSES = [
    {
        "subject": "Mathematics",
        "teacher": "Ms. Rao",
        "current_chapter": "Linear Equations",
        "schedule": "Mon/Wed/Fri",
    },
    {
        "subject": "Science",
        "teacher": "Mr. Iyer",
        "current_chapter": "Force and Pressure",
        "schedule": "Tue/Thu",
    },
    {
        "subject": "English",
        "teacher": "Ms. Thomas",
        "current_chapter": "Essay Writing",
        "schedule": "Mon/Thu",
    },
]

UPCOMING_EXAMS = [
    {
        "subject": "Mathematics",
        "date": "2026-06-28",
        "topic": "Linear Equations",
        "exam_type": "Unit Test",
    },
    {
        "subject": "Science",
        "date": "2026-07-02",
        "topic": "Force and Pressure",
        "exam_type": "Class Test",
    },
]

RECENT_SCORES = [
    {
        "subject": "Mathematics",
        "assessment": "Class Test 3",
        "score": 72,
        "max_score": 100,
        "teacher_remark": "Needs more practice with word problems.",
    },
    {
        "subject": "Science",
        "assessment": "Worksheet 5",
        "score": 18,
        "max_score": 25,
        "teacher_remark": "Good conceptual understanding, revise definitions.",
    },
    {
        "subject": "English",
        "assessment": "Essay Draft",
        "score": 15,
        "max_score": 20,
        "teacher_remark": "Improve structure and conclusion.",
    },
]


def get_student_profile() -> dict:
    return STUDENT_PROFILE


def get_student_courses() -> list:
    return STUDENT_COURSES


def get_upcoming_exams() -> list:
    return UPCOMING_EXAMS


def get_recent_scores() -> list:
    return RECENT_SCORES


def get_student_summary() -> dict:
    return {
        **STUDENT_PROFILE,
        "courses": STUDENT_COURSES,
        "upcoming_exams": UPCOMING_EXAMS,
        "recent_scores": RECENT_SCORES,
    }
