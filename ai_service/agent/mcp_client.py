from typing import Callable, Dict

from mcp_service.mcp_tools import (
    get_recent_scores_tool,
    get_student_courses_tool,
    get_student_profile_tool,
    get_upcoming_exams_tool,
)


MCPTool = Callable[[], Dict]


STUDENT_MCP_TOOLS: Dict[str, MCPTool] = {
    "get_student_profile": get_student_profile_tool,
    "get_student_courses": get_student_courses_tool,
    "get_upcoming_exams": get_upcoming_exams_tool,
    "get_recent_scores": get_recent_scores_tool,
}


def call_mcp_tool(tool_name: str) -> Dict:
    tool = STUDENT_MCP_TOOLS.get(tool_name)

    if tool is None:
        return {
            "error": "unsupported_mcp_tool",
            "tool": tool_name,
            "available_tools": sorted(STUDENT_MCP_TOOLS),
        }

    return tool()


def get_student_profile() -> Dict:
    return call_mcp_tool("get_student_profile")


def get_student_courses() -> Dict:
    return call_mcp_tool("get_student_courses")


def get_upcoming_exams() -> Dict:
    return call_mcp_tool("get_upcoming_exams")


def get_recent_scores() -> Dict:
    return call_mcp_tool("get_recent_scores")
