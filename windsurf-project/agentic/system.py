import asyncio
from typing import Dict, List, Optional, Set, Callable
from datetime import datetime

from .agent import Agent, AgentStatus
from .task import Task, TaskStatus, TaskPriority
from .message import Message, MessageType
from .communication import MessageBus, MessageRouter


class TaskScheduler:
    def __init__(self):
        self._task_queue: List[Task] = []
        self._running_tasks: Dict[str, Task] = {}
        self._completed_tasks: Dict[str, Task] = {}
        self._failed_tasks: Dict[str, Task] = {}
    
    def add_task(self, task: Task):
        """Add a task to the scheduler."""
        self._task_queue.append(task)
        self._sort_queue()
    
    def get_next_task(self, agent_capabilities: Set[str]) -> Optional[Task]:
        """Get the next task that can be handled by an agent."""
        completed_task_ids = set(self._completed_tasks.keys())
        
        for i, task in enumerate(self._task_queue):
            if (task.status == TaskStatus.PENDING and 
                task.can_start(list(completed_task_ids)) and
                set(task.required_capabilities).issubset(agent_capabilities)):
                
                self._task_queue.pop(i)
                return task
        
        return None
    
    def _sort_queue(self):
        """Sort task queue by priority and creation time."""
        self._task_queue.sort(
            key=lambda t: (t.priority.value, t.created_at),
            reverse=True
        )
    
    def update_task_status(self, task: Task):
        """Update the status of a task."""
        if task.status == TaskStatus.RUNNING:
            self._running_tasks[task.id] = task
        elif task.status == TaskStatus.COMPLETED:
            self._running_tasks.pop(task.id, None)
            self._completed_tasks[task.id] = task
        elif task.status == TaskStatus.FAILED:
            self._running_tasks.pop(task.id, None)
            self._failed_tasks[task.id] = task
    
    def get_task_stats(self) -> Dict:
        """Get scheduler statistics."""
        return {
            "pending_tasks": len([t for t in self._task_queue if t.status == TaskStatus.PENDING]),
            "running_tasks": len(self._running_tasks),
            "completed_tasks": len(self._completed_tasks),
            "failed_tasks": len(self._failed_tasks)
        }


class AgentSystem:
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.message_bus = MessageBus()
        self.message_router = MessageRouter(self.message_bus)
        self.task_scheduler = TaskScheduler()
        self._running = False
        self._coordination_interval = 1.0  # seconds
    
    async def start(self):
        """Start the agent system."""
        if self._running:
            return
        
        self._running = True
        await self.message_bus.start()
        
        # Start all agents
        for agent in self.agents.values():
            await agent.start()
            # Subscribe agent to message bus
            self.message_bus.subscribe(agent.name, self._handle_agent_message)
        
        # Start coordination loop
        asyncio.create_task(self._coordination_loop())
    
    async def stop(self):
        """Stop the agent system."""
        self._running = False
        
        # Stop all agents
        for agent in self.agents.values():
            await agent.stop()
        
        await self.message_bus.stop()
    
    def register_agent(self, agent: Agent):
        """Register an agent with the system."""
        self.agents[agent.name] = agent
        agent.message_handler = self._handle_agent_message
    
    def unregister_agent(self, agent_name: str):
        """Unregister an agent from the system."""
        if agent_name in self.agents:
            del self.agents[agent_name]
    
    async def submit_task(self, task: Task) -> str:
        """Submit a task to the system."""
        self.task_scheduler.add_task(task)
        return task.id
    
    async def get_task_result(self, task_id: str, timeout: float = 30.0) -> Optional[Task]:
        """Wait for a task to complete and return its result."""
        start_time = datetime.now()
        
        while (datetime.now() - start_time).total_seconds() < timeout:
            if task_id in self.task_scheduler._completed_tasks:
                return self.task_scheduler._completed_tasks[task_id]
            elif task_id in self.task_scheduler._failed_tasks:
                return self.task_scheduler._failed_tasks[task_id]
            
            await asyncio.sleep(0.1)
        
        return None
    
    async def _coordination_loop(self):
        """Main coordination loop for task assignment."""
        while self._running:
            try:
                await self._assign_pending_tasks()
                await self._check_task_timeouts()
                await asyncio.sleep(self._coordination_interval)
            except Exception as e:
                print(f"Error in coordination loop: {e}")
    
    async def _assign_pending_tasks(self):
        """Assign pending tasks to available agents."""
        available_agents = [
            agent for agent in self.agents.values()
            if agent.status == AgentStatus.IDLE
        ]
        
        for agent in available_agents:
            task = self.task_scheduler.get_next_task(agent.get_capability_names())
            if task:
                task.assigned_agent = agent.name
                success = await agent.assign_task(task)
                if success:
                    self.task_scheduler.update_task_status(task)
                else:
                    # Put task back in queue
                    self.task_scheduler.add_task(task)
    
    async def _check_task_timeouts(self):
        """Check for tasks that have exceeded their timeout."""
        for task in list(self.task_scheduler._running_tasks.values()):
            if task.is_expired():
                task.status = TaskStatus.FAILED
                task.error = "Task timeout exceeded"
                self.task_scheduler.update_task_status(task)
    
    async def _handle_agent_message(self, message: Message):
        """Handle messages from agents."""
        if message.message_type == MessageType.TASK_RESPONSE:
            # Task completed notification
            task_info = message.content
            if "task_id" in task_info:
                task_id = task_info["task_id"]
                # Find and update the task
                for task in list(self.task_scheduler._running_tasks.values()):
                    if task.id == task_id:
                        task.status = TaskStatus.COMPLETED if task_info.get("success") else TaskStatus.FAILED
                        task.result = task_info.get("result")
                        task.error = task_info.get("error")
                        self.task_scheduler.update_task_status(task)
                        break
        
        elif message.message_type == MessageType.STATUS_UPDATE:
            # Agent status update
            pass
        
        # Route message through message bus
        await self.message_bus.send_message(message)
    
    def get_system_status(self) -> Dict:
        """Get overall system status."""
        agent_stats = {}
        for name, agent in self.agents.items():
            agent_stats[name] = agent.get_status()
        
        return {
            "agents": agent_stats,
            "tasks": self.task_scheduler.get_task_stats(),
            "message_bus": self.message_bus.get_stats(),
            "running": self._running
        }
    
    def find_agents_by_capability(self, capability: str) -> List[str]:
        """Find agents that have a specific capability."""
        return [
            name for name, agent in self.agents.items()
            if agent.has_capability(capability)
        ]
    
    async def broadcast_message(self, sender: str, message_type: MessageType, content: Any):
        """Broadcast a message to all agents."""
        for agent_name in self.agents:
            if agent_name != sender:
                message = Message(
                    sender=sender,
                    recipient=agent_name,
                    message_type=message_type,
                    content=content
                )
                await self.message_bus.send_message(message)
