import asyncio
from typing import Dict, List, Callable, Optional, Set
from collections import defaultdict
from datetime import datetime, timedelta

from .message import Message, MessageType


class MessageBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._message_history: List[Message] = []
        self._max_history = 1000
        self._message_queue = asyncio.Queue()
        self._running = False
        self._stats = {
            "messages_sent": 0,
            "messages_delivered": 0,
            "messages_failed": 0
        }
    
    async def start(self):
        """Start the message bus processing loop."""
        if self._running:
            return
        
        self._running = True
        asyncio.create_task(self._process_messages())
    
    async def stop(self):
        """Stop the message bus."""
        self._running = False
    
    def subscribe(self, agent_name: str, handler: Callable[[Message], None]):
        """Subscribe an agent to receive messages."""
        self._subscribers[agent_name].append(handler)
    
    def unsubscribe(self, agent_name: str, handler: Callable[[Message], None]):
        """Unsubscribe an agent from receiving messages."""
        if agent_name in self._subscribers:
            try:
                self._subscribers[agent_name].remove(handler)
            except ValueError:
                pass
    
    async def send_message(self, message: Message):
        """Send a message through the bus."""
        self._stats["messages_sent"] += 1
        await self._message_queue.put(message)
    
    async def _process_messages(self):
        """Process messages from the queue."""
        while self._running:
            try:
                message = await asyncio.wait_for(
                    self._message_queue.get(), timeout=0.1
                )
                await self._deliver_message(message)
            except asyncio.TimeoutError:
                pass
            except Exception as e:
                print(f"Error processing message: {e}")
                self._stats["messages_failed"] += 1
    
    async def _deliver_message(self, message: Message):
        """Deliver a message to its recipient."""
        try:
            # Add to history
            self._message_history.append(message)
            if len(self._message_history) > self._max_history:
                self._message_history.pop(0)
            
            # Deliver to recipient
            if message.recipient in self._subscribers:
                for handler in self._subscribers[message.recipient]:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(message)
                        else:
                            handler(message)
                        self._stats["messages_delivered"] += 1
                    except Exception as e:
                        print(f"Error delivering message to {message.recipient}: {e}")
                        self._stats["messages_failed"] += 1
            else:
                print(f"No subscribers found for {message.recipient}")
                self._stats["messages_failed"] += 1
                
        except Exception as e:
            print(f"Error delivering message: {e}")
            self._stats["messages_failed"] += 1
    
    def get_messages_for_agent(self, agent_name: str, since: Optional[datetime] = None) -> List[Message]:
        """Get messages for a specific agent."""
        messages = [msg for msg in self._message_history if msg.recipient == agent_name]
        
        if since:
            messages = [msg for msg in messages if msg.timestamp >= since]
        
        return messages
    
    def get_stats(self) -> Dict:
        """Get message bus statistics."""
        return {
            **self._stats,
            "queue_size": self._message_queue.qsize(),
            "history_size": len(self._message_history),
            "subscribers": {name: len(handlers) for name, handlers in self._subscribers.items()}
        }


class MessageRouter:
    def __init__(self, message_bus: MessageBus):
        self.message_bus = message_bus
        self._routing_rules: List[Callable] = []
    
    def add_routing_rule(self, rule: Callable[[Message], Optional[str]]):
        """Add a routing rule that returns the target agent name."""
        self._routing_rules.append(rule)
    
    async def route_message(self, message: Message) -> bool:
        """Route a message based on routing rules."""
        # Apply routing rules to determine recipient
        for rule in self._routing_rules:
            try:
                target = rule(message)
                if target:
                    message.recipient = target
                    await self.message_bus.send_message(message)
                    return True
            except Exception as e:
                print(f"Error applying routing rule: {e}")
        
        # If no rule matches, try to deliver to original recipient
        await self.message_bus.send_message(message)
        return True
    
    def broadcast(self, sender: str, message_type: MessageType, content: Any, exclude: Optional[Set[str]] = None):
        """Broadcast a message to all subscribers except specified ones."""
        exclude = exclude or set()
        # This would need to be implemented based on the message bus's subscriber list
        pass
