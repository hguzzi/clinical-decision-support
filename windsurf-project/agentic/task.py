from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import uuid


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Task:
    description: str
    required_capabilities: List[str] = field(default_factory=list)
    priority: TaskPriority = TaskPriority.MEDIUM
    parameters: Dict[str, Any] = field(default_factory=dict)
    timeout: Optional[float] = None
    
    # Runtime fields
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    
    def can_start(self, completed_tasks: List[str]) -> bool:
        """Check if this task can start based on dependencies."""
        return all(dep_id in completed_tasks for dep_id in self.dependencies)
    
    def is_expired(self) -> bool:
        """Check if the task has exceeded its timeout."""
        if not self.timeout or not self.started_at:
            return False
        
        elapsed = (datetime.now() - self.started_at).total_seconds()
        return elapsed > self.timeout
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary representation."""
        return {
            "id": self.id,
            "description": self.description,
            "required_capabilities": self.required_capabilities,
            "priority": self.priority.value,
            "parameters": self.parameters,
            "timeout": self.timeout,
            "status": self.status.value,
            "assigned_agent": self.assigned_agent,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error,
            "dependencies": self.dependencies
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Create task from dictionary representation."""
        task = cls(
            description=data["description"],
            required_capabilities=data.get("required_capabilities", []),
            priority=TaskPriority(data.get("priority", TaskPriority.MEDIUM.value)),
            parameters=data.get("parameters", {}),
            timeout=data.get("timeout")
        )
        
        task.id = data["id"]
        task.status = TaskStatus(data.get("status", TaskStatus.PENDING.value))
        task.assigned_agent = data.get("assigned_agent")
        task.created_at = datetime.fromisoformat(data["created_at"])
        
        if data.get("started_at"):
            task.started_at = datetime.fromisoformat(data["started_at"])
        if data.get("completed_at"):
            task.completed_at = datetime.fromisoformat(data["completed_at"])
        
        task.result = data.get("result")
        task.error = data.get("error")
        task.dependencies = data.get("dependencies", [])
        
        return task
