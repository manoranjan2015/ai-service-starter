from typing import Dict, List

ConversationMessage = Dict[str, str]
MAX_MESSAGES_PER_CONVERSATION = 20

conversations: Dict[str, List[ConversationMessage]] = {}


def get_conversation(conversation_id: str) -> List[ConversationMessage]:
    return conversations.get(conversation_id, [])


def add_message(conversation_id: str, role: str, content: str) -> None:
    if conversation_id not in conversations:
        conversations[conversation_id] = []

    conversations[conversation_id].append({
        "role": role,
        "content": content
    })
    conversations[conversation_id] = conversations[conversation_id][-MAX_MESSAGES_PER_CONVERSATION:]


def clear_conversation(conversation_id: str) -> bool:
    if conversation_id in conversations:
        del conversations[conversation_id]
        return True

    return False