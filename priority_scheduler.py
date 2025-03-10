
from typing import List, Optional
import simpy


class PriorityScheduler:
    """
    Priority Scheduler (Non-preemptive).
    This scheduler selects the process with the highest priority (lower number = higher priority).
    """
    def __init__(self, env: simpy.Environment, ready_queue: List, completed: List, total: int,
                 name: str = "Priority Scheduler", description: Optional[str] = None) -> None:
        self.env = env
        self.ready_queue = ready_queue
        self.completed = completed
        self.total = total
        self.process = env.process(self.schedule_process())
        self.name = name
        self.description = description or "A scheduler using Priority scheduling policy."

    def schedule_process(self) -> None:
        """
        Executes process scheduling logic for Priorit(Non-preemptive) Scheduler.
        """
        while len(self.completed) < self.total:
            if not self.ready_queue:
                yield self.env.timeout(1)
                continue
            proc = min(self.ready_queue, key=lambda p: p.priority)
            self.ready_queue.remove(proc)
            if proc.start is None:
                proc.start = self.env.now
                proc.response = proc.start - proc.arrival
            print(f"Time {self.env.now}: Process {proc.pid} starts execution for {proc.burst} time units (Priority)")
            yield self.env.timeout(proc.burst)
            proc.completion = self.env.now
            proc.turnaround = proc.completion - proc.arrival
            proc.waiting = proc.start - proc.arrival
            self.completed.append(proc)
