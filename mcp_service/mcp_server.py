import os
from typing import Dict

from mcp_service.mcp_tools import (
    get_recent_scores_tool,
    get_student_courses_tool,
    get_student_profile_tool,
    get_upcoming_exams_tool,
)


def create_mcp_server():
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("AI Student Study Tracker MCP")

    @mcp.tool()
    def get_student_profile() -> Dict:
        """Return profile data for the configured student."""
        return get_student_profile_tool()

    @mcp.tool()
    def get_student_courses() -> Dict:
        """Return current courses, teachers, chapters, and schedules for the configured student."""
        return get_student_courses_tool()

    @mcp.tool()
    def get_upcoming_exams() -> Dict:
        """Return upcoming exams for the configured student."""
        return get_upcoming_exams_tool()

    @mcp.tool()
    def get_recent_scores() -> Dict:
        """Return recent assessment scores and teacher remarks for the configured student."""
        return get_recent_scores_tool()

    return mcp


def main():
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    create_mcp_server().run(transport=transport)


if __name__ == "__main__":
    main()
