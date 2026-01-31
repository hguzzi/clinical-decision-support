#!/usr/bin/env python3
"""
Basic example of the agentic system in action.
"""

import asyncio
import sys
import os

# Add the parent directory to the path so we can import agentic
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentic import Agent, Task, TaskPriority, AgentSystem


class ResearchAgent(Agent):
    """A specialized agent for research tasks."""
    
    def __init__(self, name: str):
        super().__init__(
            name=name,
            capabilities=["web_search", "data_analysis", "report_generation"]
        )
    
    async def _perform_task(self, task):
        """Perform research-specific tasks."""
        if "web_search" in task.required_capabilities:
            await asyncio.sleep(1.0)  # Simulate web search
            return f"Web search results for: {task.description}"
        
        elif "data_analysis" in task.required_capabilities:
            await asyncio.sleep(2.0)  # Simulate data analysis
            return f"Analysis of: {task.description}"
        
        elif "report_generation" in task.required_capabilities:
            await asyncio.sleep(1.5)  # Simulate report writing
            return f"Report on: {task.description}"
        
        return await super()._perform_task(task)


class ProcessingAgent(Agent):
    """A specialized agent for data processing tasks."""
    
    def __init__(self, name: str):
        super().__init__(
            name=name,
            capabilities=["data_processing", "file_operations", "calculation"]
        )
    
    async def _perform_task(self, task):
        """Perform processing-specific tasks."""
        if "data_processing" in task.required_capabilities:
            await asyncio.sleep(1.5)  # Simulate data processing
            return f"Processed data for: {task.description}"
        
        elif "file_operations" in task.required_capabilities:
            await asyncio.sleep(0.5)  # Simulate file operations
            return f"File operation completed: {task.description}"
        
        elif "calculation" in task.required_capabilities:
            await asyncio.sleep(0.8)  # Simulate calculations
            return f"Calculation result for: {task.description}"
        
        return await super()._perform_task(task)


async def main():
    """Run the basic example."""
    print("🚀 Starting Agentic System Example")
    print("=" * 50)
    
    # Create the agent system
    system = AgentSystem()
    
    # Create specialized agents
    researcher = ResearchAgent("research_agent_1")
    processor = ProcessingAgent("processing_agent_1")
    
    # Register agents with the system
    system.register_agent(researcher)
    system.register_agent(processor)
    
    # Start the system
    await system.start()
    print("✅ Agent system started")
    
    try:
        # Create some tasks
        tasks = [
            Task(
                description="Research latest AI trends",
                required_capabilities=["web_search"],
                priority=TaskPriority.HIGH
            ),
            Task(
                description="Analyze market data",
                required_capabilities=["data_analysis"],
                priority=TaskPriority.MEDIUM
            ),
            Task(
                description="Process customer records",
                required_capabilities=["data_processing"],
                priority=TaskPriority.MEDIUM
            ),
            Task(
                description="Generate quarterly report",
                required_capabilities=["report_generation"],
                priority=TaskPriority.LOW
            ),
            Task(
                description="Calculate financial metrics",
                required_capabilities=["calculation"],
                priority=TaskPriority.HIGH
            )
        ]
        
        # Submit tasks to the system
        print(f"\n📋 Submitting {len(tasks)} tasks...")
        task_ids = []
        for task in tasks:
            task_id = await system.submit_task(task)
            task_ids.append(task_id)
            print(f"  • Submitted: {task.description} (ID: {task_id[:8]}...)")
        
        # Wait for tasks to complete
        print(f"\n⏳ Waiting for tasks to complete...")
        completed_tasks = []
        
        for task_id in task_ids:
            task = await system.get_task_result(task_id, timeout=10.0)
            if task:
                completed_tasks.append(task)
                status = "✅" if task.status.value == "completed" else "❌"
                print(f"  {status} {task.description}")
                if task.result:
                    print(f"     Result: {task.result}")
            else:
                print(f"  ⏰ Task {task_id[:8]}... timed out")
        
        # Show system status
        print(f"\n📊 System Status:")
        status = system.get_system_status()
        print(f"  • Total agents: {len(status['agents'])}")
        print(f"  • Completed tasks: {status['tasks']['completed_tasks']}")
        print(f"  • Failed tasks: {status['tasks']['failed_tasks']}")
        
        # Show agent details
        print(f"\n🤖 Agent Details:")
        for agent_name, agent_status in status['agents'].items():
            print(f"  • {agent_name}:")
            print(f"    - Status: {agent_status['status']}")
            print(f"    - Tasks completed: {agent_status['metrics']['tasks_completed']}")
            print(f"    - Capabilities: {', '.join(agent_status['capabilities'])}")
    
    finally:
        # Stop the system
        await system.stop()
        print(f"\n🛑 Agent system stopped")
    
    print("\n🎉 Example completed!")


if __name__ == "__main__":
    asyncio.run(main())
