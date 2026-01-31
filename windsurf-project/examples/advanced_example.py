#!/usr/bin/env python3
"""
Advanced example showing agent coordination and dependencies.
"""

import asyncio
import sys
import os

# Add the parent directory to the path so we can import agentic
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentic import Agent, Task, TaskPriority, AgentSystem, Message, MessageType


class CoordinatorAgent(Agent):
    """An agent that coordinates other agents."""
    
    def __init__(self, name: str):
        super().__init__(
            name=name,
            capabilities=["coordination", "planning", "monitoring"]
        )
        self.workflow_steps = []
    
    async def _perform_task(self, task):
        """Perform coordination tasks."""
        if "coordination" in task.required_capabilities:
            await self._coordinate_workflow(task)
            return f"Coordinated workflow: {task.description}"
        
        elif "planning" in task.required_capabilities:
            await self._create_plan(task)
            return f"Created plan for: {task.description}"
        
        elif "monitoring" in task.required_capabilities:
            await self._monitor_progress(task)
            return f"Monitoring progress for: {task.description}"
        
        return await super()._perform_task(task)
    
    async def _coordinate_workflow(self, task):
        """Coordinate a multi-step workflow."""
        await asyncio.sleep(0.5)
        # This would normally send coordination messages to other agents
        print(f"🎯 {self.name}: Coordinating workflow for {task.description}")
    
    async def _create_plan(self, task):
        """Create a plan for task execution."""
        await asyncio.sleep(1.0)
        print(f"📋 {self.name}: Creating plan for {task.description}")
    
    async def _monitor_progress(self, task):
        """Monitor task progress."""
        await asyncio.sleep(0.3)
        print(f"👁️  {self.name}: Monitoring {task.description}")


class DataAgent(Agent):
    """An agent specialized in data operations."""
    
    def __init__(self, name: str):
        super().__init__(
            name=name,
            capabilities=["data_collection", "data_processing", "data_validation"]
        )
    
    async def _perform_task(self, task):
        """Perform data-specific tasks."""
        if "data_collection" in task.required_capabilities:
            await asyncio.sleep(2.0)
            result = f"Collected data for: {task.description}"
            print(f"📊 {self.name}: {result}")
            return result
        
        elif "data_processing" in task.required_capabilities:
            await asyncio.sleep(1.5)
            result = f"Processed data for: {task.description}"
            print(f"⚙️  {self.name}: {result}")
            return result
        
        elif "data_validation" in task.required_capabilities:
            await asyncio.sleep(1.0)
            result = f"Validated data for: {task.description}"
            print(f"✅ {self.name}: {result}")
            return result
        
        return await super()._perform_task(task)


class AnalysisAgent(Agent):
    """An agent specialized in analysis tasks."""
    
    def __init__(self, name: str):
        super().__init__(
            name=name,
            capabilities=["statistical_analysis", "ml_modeling", "visualization"]
        )
    
    async def _perform_task(self, task):
        """Perform analysis-specific tasks."""
        if "statistical_analysis" in task.required_capabilities:
            await asyncio.sleep(2.5)
            result = f"Statistical analysis completed for: {task.description}"
            print(f"📈 {self.name}: {result}")
            return result
        
        elif "ml_modeling" in task.required_capabilities:
            await asyncio.sleep(3.0)
            result = f"ML model trained for: {task.description}"
            print(f"🤖 {self.name}: {result}")
            return result
        
        elif "visualization" in task.required_capabilities:
            await asyncio.sleep(1.5)
            result = f"Visualization created for: {task.description}"
            print(f"📊 {self.name}: {result}")
            return result
        
        return await super()._perform_task(task)


async def demonstrate_workflow():
    """Demonstrate a complex workflow with dependencies."""
    print("🚀 Starting Advanced Workflow Example")
    print("=" * 50)
    
    # Create the agent system
    system = AgentSystem()
    
    # Create specialized agents
    coordinator = CoordinatorAgent("coordinator")
    data_agent = DataAgent("data_agent")
    analysis_agent = AnalysisAgent("analysis_agent")
    
    # Register agents
    system.register_agent(coordinator)
    system.register_agent(data_agent)
    system.register_agent(analysis_agent)
    
    # Start the system
    await system.start()
    print("✅ Agent system started")
    
    try:
        # Create a workflow with dependencies
        print(f"\n📋 Creating workflow with dependencies...")
        
        # Step 1: Plan the analysis
        planning_task = Task(
            description="Plan customer churn analysis",
            required_capabilities=["planning"],
            priority=TaskPriority.HIGH
        )
        
        # Step 2: Collect data (depends on planning)
        collection_task = Task(
            description="Collect customer data",
            required_capabilities=["data_collection"],
            priority=TaskPriority.HIGH,
            dependencies=[planning_task.id]
        )
        
        # Step 3: Process data (depends on collection)
        processing_task = Task(
            description="Process and clean customer data",
            required_capabilities=["data_processing"],
            priority=TaskPriority.HIGH,
            dependencies=[collection_task.id]
        )
        
        # Step 4: Validate data (depends on processing)
        validation_task = Task(
            description="Validate processed data",
            required_capabilities=["data_validation"],
            priority=TaskPriority.MEDIUM,
            dependencies=[processing_task.id]
        )
        
        # Step 5: Statistical analysis (depends on validation)
        analysis_task = Task(
            description="Perform statistical analysis",
            required_capabilities=["statistical_analysis"],
            priority=TaskPriority.HIGH,
            dependencies=[validation_task.id]
        )
        
        # Step 6: ML modeling (depends on analysis)
        modeling_task = Task(
            description="Train churn prediction model",
            required_capabilities=["ml_modeling"],
            priority=TaskPriority.MEDIUM,
            dependencies=[analysis_task.id]
        )
        
        # Step 7: Create visualization (depends on modeling)
        viz_task = Task(
            description="Create analysis visualizations",
            required_capabilities=["visualization"],
            priority=TaskPriority.LOW,
            dependencies=[modeling_task.id]
        )
        
        # Step 8: Monitor and coordinate (runs throughout)
        monitoring_task = Task(
            description="Monitor workflow progress",
            required_capabilities=["monitoring"],
            priority=TaskPriority.MEDIUM
        )
        
        # Submit all tasks
        tasks = [
            planning_task, collection_task, processing_task,
            validation_task, analysis_task, modeling_task,
            viz_task, monitoring_task
        ]
        
        task_ids = []
        for task in tasks:
            task_id = await system.submit_task(task)
            task_ids.append(task_id)
            print(f"  • Submitted: {task.description}")
        
        # Wait for all tasks to complete
        print(f"\n⏳ Waiting for workflow to complete...")
        completed_tasks = []
        
        for task_id in task_ids:
            task = await system.get_task_result(task_id, timeout=30.0)
            if task:
                completed_tasks.append(task)
                status = "✅" if task.status.value == "completed" else "❌"
                print(f"  {status} {task.description}")
                if task.result:
                    print(f"     → {task.result}")
            else:
                print(f"  ⏰ Task {task_id[:8]}... timed out")
        
        # Show final system status
        print(f"\n📊 Final System Status:")
        status = system.get_system_status()
        print(f"  • Total agents: {len(status['agents'])}")
        print(f"  • Completed tasks: {status['tasks']['completed_tasks']}")
        print(f"  • Failed tasks: {status['tasks']['failed_tasks']}")
        
        # Show agent performance
        print(f"\n🏆 Agent Performance:")
        for agent_name, agent_status in status['agents'].items():
            metrics = agent_status['metrics']
            print(f"  • {agent_name}:")
            print(f"    - Tasks completed: {metrics['tasks_completed']}")
            print(f"    - Tasks failed: {metrics['tasks_failed']}")
            if metrics['last_activity']:
                print(f"    - Last activity: {metrics['last_activity']}")
    
    finally:
        await system.stop()
        print(f"\n🛑 Agent system stopped")
    
    print("\n🎉 Advanced workflow completed!")


if __name__ == "__main__":
    asyncio.run(demonstrate_workflow())
