import asyncio
from typing import Dict, List, Set, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

from .task import Task, TaskStatus
from .message import Message, MessageType


class AgentStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


@dataclass
class AgentCapability:
    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentMetrics:
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_execution_time: float = 0.0
    last_activity: Optional[datetime] = None


class Agent:
    def __init__(
        self,
        name: str,
        capabilities: List[str] = None,
        max_concurrent_tasks: int = 1,
        message_handler: Optional[Callable[[Message], None]] = None
    ):
        self.name = name
        self.capabilities: List[AgentCapability] = []
        self.max_concurrent_tasks = max_concurrent_tasks
        self.status = AgentStatus.IDLE
        self.current_tasks: Dict[str, Task] = {}
        self.completed_tasks: List[Task] = []
        self.message_handler = message_handler
        self.metrics = AgentMetrics()
        self._task_queue = asyncio.Queue()
        self._running = False
        
        if capabilities:
            for cap in capabilities:
                self.add_capability(cap)
    
    def add_capability(self, capability_name: str, description: str = "", **kwargs):
        capability = AgentCapability(
            name=capability_name,
            description=description,
            parameters=kwargs
        )
        self.capabilities.append(capability)
    
    def has_capability(self, capability_name: str) -> bool:
        return any(cap.name == capability_name for cap in self.capabilities)
    
    def get_capability_names(self) -> Set[str]:
        return {cap.name for cap in self.capabilities}
    
    async def start(self):
        """Start the agent's main execution loop."""
        if self._running:
            return
        
        self._running = True
        self.status = AgentStatus.IDLE
        
        asyncio.create_task(self._process_tasks())
    
    async def stop(self):
        """Stop the agent."""
        self._running = False
        self.status = AgentStatus.OFFLINE
    
    async def assign_task(self, task: Task) -> bool:
        """Assign a task to this agent."""
        if not self._can_handle_task(task):
            return False
        
        if len(self.current_tasks) >= self.max_concurrent_tasks:
            await self._task_queue.put(task)
            return True
        
        await self._execute_task(task)
        return True
    
    def _can_handle_task(self, task: Task) -> bool:
        """Check if this agent can handle the given task."""
        if self.status == AgentStatus.OFFLINE:
            return False
        
        required_caps = set(task.required_capabilities)
        available_caps = self.get_capability_names()
        
        return required_caps.issubset(available_caps)
    
    async def _execute_task(self, task: Task):
        """Execute a single task."""
        task_id = task.id
        self.current_tasks[task_id] = task
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        
        self.status = AgentStatus.BUSY
        self.metrics.last_activity = datetime.now()
        
        try:
            result = await self._perform_task(task)
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            
            self.metrics.tasks_completed += 1
            self.completed_tasks.append(task)
            
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()
            
            self.metrics.tasks_failed += 1
            self.status = AgentStatus.ERROR
            
        finally:
            self.current_tasks.pop(task_id, None)
            if len(self.current_tasks) == 0 and not self._task_queue.empty():
                self.status = AgentStatus.IDLE
    
    async def _perform_task(self, task: Task) -> Any:
        """Override this method to implement specific task execution logic."""
        await asyncio.sleep(0.1)  # Simulate work
        return f"Task '{task.description}' completed by {self.name}"
    
    async def _process_tasks(self):
        """Main task processing loop."""
        while self._running:
            try:
                if len(self.current_tasks) < self.max_concurrent_tasks:
                    try:
                        task = await asyncio.wait_for(
                            self._task_queue.get(), timeout=0.1
                        )
                        asyncio.create_task(self._execute_task(task))
                    except asyncio.TimeoutError:
                        pass
                
                await asyncio.sleep(0.01)
                
            except Exception as e:
                print(f"Error in agent {self.name}: {e}")
                self.status = AgentStatus.ERROR
    
    async def send_message(self, recipient: str, message_type: MessageType, content: Any):
        """Send a message to another agent."""
        message = Message(
            sender=self.name,
            recipient=recipient,
            message_type=message_type,
            content=content
        )
        
        if self.message_handler:
            self.message_handler(message)
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the agent."""
        return {
            "name": self.name,
            "status": self.status.value,
            "capabilities": [cap.name for cap in self.capabilities],
            "current_tasks": len(self.current_tasks),
            "queued_tasks": self._task_queue.qsize(),
            "completed_tasks": len(self.completed_tasks),
            "metrics": {
                "tasks_completed": self.metrics.tasks_completed,
                "tasks_failed": self.metrics.tasks_failed,
                "total_execution_time": self.metrics.total_execution_time,
                "last_activity": self.metrics.last_activity.isoformat() if self.metrics.last_activity else None
            }
        }
