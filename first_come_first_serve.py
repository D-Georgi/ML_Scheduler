
import simpy
from typing import List, Optional

class FirstComeFirstServeScheduler:
    """
    First Come First Serve (FCFS) Scheduler.
    This scheduler selects the process that arrives first.
    """
    def __init__(self, env: simpy.Environment, ready_queue: List, completed: List, total: int,
                 name: str = "First Come First Serve Scheduler", description: Optional[str] = None) -> None:
        """
        Initializes the FCFS scheduler.
        
        :param env: The simulation environment.
        :param ready_queue: List of processes ready to execute.
        :param completed: List to store completed processes.
        :param total: Total number of processes.
        :param name: Name of the scheduler (default is "First Come First Serve Scheduler").
        :param description: Optional description of the scheduler.
        """
        self.env = env
        self.ready_queue = ready_queue
        self.completed = completed
        self.total = total
        self.process = env.process(self.schedule_process())
        self.name = name
        self.description = description or "A scheduler using First Come First Serve (FCFS) policy."

    def schedule_process(self) -> None:
        """
        Executes process scheduling logic for First Come First Serve(FCFS) Scheduler.
        """
        while len(self.completed) < self.total:
            if not self.ready_queue:
                yield self.env.timeout(1)
                continue
            
            proc = self.ready_queue.pop(0)
            
            if proc.start is None:
                proc.start = self.env.now
                proc.response = proc.start - proc.arrival
            
            print(f"Time {self.env.now}: Process {proc.pid} starts execution for {proc.burst} time units (FCFS)")
            yield self.env.timeout(proc.burst)
            
            proc.completion = self.env.now
            proc.turnaround = proc.completion - proc.arrival
            proc.waiting = proc.start - proc.arrival
            self.completed.append(proc)

