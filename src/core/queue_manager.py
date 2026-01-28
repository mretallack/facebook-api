"""Simple async queue manager with rate limiting"""
import asyncio
import time
from typing import Dict, Callable, Any, Optional
from dataclasses import dataclass
from enum import Enum


class Priority(Enum):
    LOW = 3
    NORMAL = 2
    HIGH = 1


@dataclass
class Task:
    id: str
    func: Callable
    args: tuple
    kwargs: dict
    priority: Priority
    account_id: str
    created_at: float
    status: str = "pending"


class QueueManager:
    """Async task queue with rate limiting"""
    
    def __init__(self):
        self.queues: Dict[Priority, asyncio.Queue] = {
            Priority.HIGH: asyncio.Queue(),
            Priority.NORMAL: asyncio.Queue(),
            Priority.LOW: asyncio.Queue()
        }
        self.tasks: Dict[str, Task] = {}
        self.running = False
        self.worker_task: Optional[asyncio.Task] = None
        
        # Rate limiting per account
        self.rate_limits: Dict[str, list] = {}
        self.max_per_minute = 20
    
    async def enqueue(self, task_id: str, func: Callable, args: tuple = (), 
                     kwargs: dict = None, priority: Priority = Priority.NORMAL,
                     account_id: str = "default") -> str:
        """Add task to queue"""
        kwargs = kwargs or {}
        
        task = Task(
            id=task_id,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            account_id=account_id,
            created_at=time.time()
        )
        
        self.tasks[task_id] = task
        await self.queues[priority].put(task)
        
        return task_id
    
    async def start(self):
        """Start processing queue"""
        if self.running:
            return
        
        self.running = True
        self.worker_task = asyncio.create_task(self._worker())
    
    async def stop(self):
        """Stop processing queue"""
        self.running = False
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
    
    async def _worker(self):
        """Process tasks from queue"""
        while self.running:
            task = await self._get_next_task()
            
            if not task:
                await asyncio.sleep(0.1)
                continue
            
            # Check rate limit
            if not await self._check_rate_limit(task.account_id):
                # Re-queue task
                await self.queues[task.priority].put(task)
                await asyncio.sleep(1)
                continue
            
            # Execute task
            try:
                task.status = "running"
                result = await task.func(*task.args, **task.kwargs)
                task.status = "completed"
                
                # Record execution for rate limiting
                self._record_execution(task.account_id)
                
            except Exception as e:
                task.status = "failed"
                print(f"Task {task.id} failed: {e}")
    
    async def _get_next_task(self) -> Optional[Task]:
        """Get next task by priority"""
        for priority in [Priority.HIGH, Priority.NORMAL, Priority.LOW]:
            try:
                task = self.queues[priority].get_nowait()
                return task
            except asyncio.QueueEmpty:
                continue
        return None
    
    async def _check_rate_limit(self, account_id: str) -> bool:
        """Check if account is within rate limit"""
        if account_id not in self.rate_limits:
            return True
        
        now = time.time()
        # Remove executions older than 1 minute
        self.rate_limits[account_id] = [
            t for t in self.rate_limits[account_id]
            if now - t < 60
        ]
        
        return len(self.rate_limits[account_id]) < self.max_per_minute
    
    def _record_execution(self, account_id: str):
        """Record task execution for rate limiting"""
        if account_id not in self.rate_limits:
            self.rate_limits[account_id] = []
        
        self.rate_limits[account_id].append(time.time())
    
    def get_status(self, task_id: str) -> Optional[str]:
        """Get task status"""
        task = self.tasks.get(task_id)
        return task.status if task else None
    
    def stats(self) -> Dict:
        """Get queue statistics"""
        return {
            'total_tasks': len(self.tasks),
            'pending': sum(1 for t in self.tasks.values() if t.status == "pending"),
            'running': sum(1 for t in self.tasks.values() if t.status == "running"),
            'completed': sum(1 for t in self.tasks.values() if t.status == "completed"),
            'failed': sum(1 for t in self.tasks.values() if t.status == "failed"),
            'queue_sizes': {
                'high': self.queues[Priority.HIGH].qsize(),
                'normal': self.queues[Priority.NORMAL].qsize(),
                'low': self.queues[Priority.LOW].qsize()
            }
        }


# Global queue instance
queue = QueueManager()
