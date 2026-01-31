import asyncio
import pytest
from datetime import datetime

from agentic import Agent, Task, TaskStatus, AgentStatus


class TestAgent(Agent):
    def __init__(self, name: str):
        super().__init__(name, capabilities=["test_capability"])
    
    async def _perform_task(self, task):
        await asyncio.sleep(0.1)
        return f"Test result for {task.description}"


@pytest.mark.asyncio
async def test_agent_creation():
    """Test agent creation and basic properties."""
    agent = TestAgent("test_agent")
    
    assert agent.name == "test_agent"
    assert agent.status == AgentStatus.IDLE
    assert len(agent.capabilities) == 1
    assert agent.has_capability("test_capability")
    assert not agent.has_capability("nonexistent_capability")


@pytest.mark.asyncio
async def test_agent_task_execution():
    """Test agent task execution."""
    agent = TestAgent("test_agent")
    await agent.start()
    
    task = Task(
        description="Test task",
        required_capabilities=["test_capability"]
    )
    
    success = await agent.assign_task(task)
    assert success
    
    # Wait for task to complete
    await asyncio.sleep(0.2)
    
    assert task.status == TaskStatus.COMPLETED
    assert task.result == "Test result for Test task"
    assert agent.metrics.tasks_completed == 1
    
    await agent.stop()


@pytest.mark.asyncio
async def test_agent_capability_check():
    """Test agent capability checking."""
    agent = Agent("test_agent", ["capability1", "capability2"])
    
    assert agent.has_capability("capability1")
    assert agent.has_capability("capability2")
    assert not agent.has_capability("capability3")
    
    agent.add_capability("capability3", "Test capability")
    assert agent.has_capability("capability3")


@pytest.mark.asyncio
async def test_agent_concurrent_tasks():
    """Test agent handling multiple concurrent tasks."""
    agent = TestAgent("test_agent")
    agent.max_concurrent_tasks = 2
    await agent.start()
    
    tasks = [
        Task(f"Task {i}", ["test_capability"])
        for i in range(3)
    ]
    
    # Assign first two tasks
    success1 = await agent.assign_task(tasks[0])
    success2 = await agent.assign_task(tasks[1])
    success3 = await agent.assign_task(tasks[2])  # Should be queued
    
    assert success1
    assert success2
    assert success3  # Should be accepted but queued
    
    # Wait for completion
    await asyncio.sleep(0.5)
    
    assert all(task.status == TaskStatus.COMPLETED for task in tasks)
    assert agent.metrics.tasks_completed == 3
    
    await agent.stop()


@pytest.mark.asyncio
async def test_agent_task_rejection():
    """Test agent rejecting tasks it can't handle."""
    agent = TestAgent("test_agent")
    await agent.start()
    
    task = Task(
        description="Unsupported task",
        required_capabilities=["unsupported_capability"]
    )
    
    success = await agent.assign_task(task)
    assert not success
    assert task.status == TaskStatus.PENDING
    
    await agent.stop()


@pytest.mark.asyncio
async def test_agent_status_updates():
    """Test agent status updates during task execution."""
    agent = TestAgent("test_agent")
    await agent.start()
    
    assert agent.status == AgentStatus.IDLE
    
    task = Task("Test task", ["test_capability"])
    await agent.assign_task(task)
    
    # Should be busy during execution
    assert agent.status == AgentStatus.BUSY
    
    # Wait for completion
    await asyncio.sleep(0.2)
    
    # Should return to idle
    assert agent.status == AgentStatus.IDLE
    
    await agent.stop()


def test_agent_get_status():
    """Test agent status reporting."""
    agent = TestAgent("test_agent")
    
    status = agent.get_status()
    
    assert status["name"] == "test_agent"
    assert status["status"] == AgentStatus.IDLE.value
    assert "test_capability" in status["capabilities"]
    assert status["current_tasks"] == 0
    assert status["completed_tasks"] == 0
    assert "metrics" in status
