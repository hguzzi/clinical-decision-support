from typing import Any, Optional
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import uuid


class MessageType(Enum):
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    STATUS_UPDATE = "status_update"
    COORDINATION = "coordination"
    ERROR = "error"
    INFO = "info"


@dataclass
class Message:
    sender: str
    recipient: str
    message_type: MessageType
    content: Any
    
    # Metadata
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    reply_to: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert message to dictionary representation."""
        return {
            "id": self.id,
            "sender": self.sender,
            "recipient": self.recipient,
            "message_type": self.message_type.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "reply_to": self.reply_to,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        """Create message from dictionary representation."""
        message = cls(
            sender=data["sender"],
            recipient=data["recipient"],
            message_type=MessageType(data["message_type"]),
            content=data["content"]
        )
        
        message.id = data["id"]
        message.timestamp = datetime.fromisoformat(data["timestamp"])
        message.reply_to = data.get("reply_to")
        message.metadata = data.get("metadata", {})
        
        return message
