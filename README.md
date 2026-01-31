# clinical-decision-support
Clinical Decision Support System (CDSS) 

# Agentic System

A flexible multi-agent coordination system built in Python that enables distributed task execution and intelligent agent collaboration.

## Features

- **Agent Architecture**: Modular agent design with capabilities and roles
- **Task Management**: Distributed task execution with dependencies and priorities
- **Communication**: Message passing between agents with routing and broadcasting
- **Coordination**: Automatic task assignment and load balancing
- **Extensible**: Easy to add new agent types and capabilities
- **Async Support**: Built on asyncio for concurrent execution

## Quick Start

```python
import asyncio
from agentic import Agent, Task, AgentSystem

async def main():
    # Create the agent system
    system = AgentSystem()
    
    # Create an agent
    agent = Agent(
        name="researcher",
        capabilities=["web_search", "data_analysis"]
    )
    
    # Register agent
    system.register_agent(agent)
    await system.start()
    
    # Create and submit a task
    task = Task(
        description="Research latest AI trends",
        required_capabilities=["web_search"]
    )
    
    task_id = await system.submit_task(task)
    
    # Wait for completion
    result = await system.get_task_result(task_id)
    print(f"Result: {result.result}")
    
    await system.stop()

asyncio.run(main())
```

## Installation

```bash
pip install -r requirements.txt
```

## Architecture

### Core Components

- **Agent**: Base class for autonomous agents with capabilities
- **Task**: Work units with requirements, priorities, and dependencies
- **AgentSystem**: Orchestrates agents and manages task distribution
- **MessageBus**: Handles inter-agent communication
- **TaskScheduler**: Manages task queues and assignment

### Agent Capabilities

Agents declare their capabilities, which the system uses for task assignment:

```python
agent = Agent(
    name="data_processor",
    capabilities=["data_processing", "file_operations", "analysis"]
)
```

### Task Dependencies

Create complex workflows with task dependencies:

```python
# Task 2 depends on Task 1
task1 = Task("Collect data", ["data_collection"])
task2 = Task("Process data", ["data_processing"], dependencies=[task1.id])
```

## Examples

### Basic Usage

```bash
python examples/basic_example.py
```

Demonstrates:
- Creating specialized agents
- Submitting multiple tasks
- Automatic task assignment
- System monitoring

### Advanced Workflow

```bash
python examples/advanced_example.py
```

Demonstrates:
- Task dependencies
- Agent coordination
- Complex workflows
- Real-time monitoring

## Development

### Setup Development Environment

```bash
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
black agentic/ tests/ examples/
```

### Type Checking

```bash
mypy agentic/
```

## API Reference

### Agent Class

```python
class Agent:
    def __init__(self, name: str, capabilities: List[str], max_concurrent_tasks: int = 1)
    async def start(self) -> None
    async def stop(self) -> None
    async def assign_task(self, task: Task) -> bool
    def has_capability(self, capability: str) -> bool
    def get_status(self) -> Dict[str, Any]
```

### Task Class

```python
class Task:
    def __init__(self, description: str, required_capabilities: List[str], 
                 priority: TaskPriority = TaskPriority.MEDIUM)
    def can_start(self, completed_tasks: List[str]) -> bool
    def is_expired(self) -> bool
```

### AgentSystem Class

```python
class AgentSystem:
    def __init__(self)
    async def start(self) -> None
    async def stop(self) -> None
    def register_agent(self, agent: Agent) -> None
    async def submit_task(self, task: Task) -> str
    async def get_task_result(self, task_id: str, timeout: float = 30.0) -> Optional[Task]
    def get_system_status(self) -> Dict[str, Any]
```

## Custom Agents

Create specialized agents by extending the base Agent class:

```python
class CustomAgent(Agent):
    def __init__(self, name: str):
        super().__init__(name, capabilities=["custom_capability"])
    
    async def _perform_task(self, task):
        # Implement your custom logic here
        result = await your_custom_logic(task)
        return result
```

## Message System

Agents can communicate through the message system:

```python
await agent.send_message(
    recipient="other_agent",
    message_type=MessageType.COORDINATION,
    content={"action": "request_help", "task_id": task.id}
)
```

## Monitoring

Get real-time system status:

```python
status = system.get_system_status()
print(f"Active agents: {len(status['agents'])}")
print(f"Completed tasks: {status['tasks']['completed_tasks']}")
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

MIT License - see LICENSE file for details.


# Clinical Decision Support System - Installation Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Detailed Installation](#detailed-installation)
4. [Configuration](#configuration)
5. [Docker Setup](#docker-setup)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)
8. [Upgrading](#upgrading)

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git
- System dependencies:
  ```bash
  # Ubuntu/Debian
  sudo apt-get update && sudo apt-get install -y python3-dev python3-venv
  
  # CentOS/RHEL
  sudo yum install -y python3-devel
  
  # macOS
  brew install python
  ```

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/hguzzi/clinical-decision-support.git
   cd clinical-decision-support
   ```

2. Set up a virtual environment:
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. Run the system:
   ```bash
   python -m clinical_agents.cli
   ```

