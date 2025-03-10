
import simpy
from typing import List, Optional

class RoundRobinScheduler:
    """
    Round Robin (RR) Scheduler.
    This scheduler assigns a fixed time quantum to each process in a cyclic order.
    """
    def __init__(self, env: simpy.Environment, ready_queue: List, completed: List, total: int, time_quantum: int,
                 name: str = "Round Robin Scheduler", description: Optional[str] = None) -> None:
        """
        Initializes the Round Robin scheduler.
        
        :param env: The simulation environment.
        :param ready_queue: List of processes ready to execute.
        :param completed: List to store completed processes.
        :param total: Total number of processes.
        :param time_quantum: Time slice for each process.
        :param name: Name of the scheduler (default is "Round Robin Scheduler").
        :param description: Optional description of the scheduler.
        """
        self.env = env
        self.ready_queue = ready_queue
        self.completed = completed
        self.total = total
        self.time_quantum = time_quantum
        self.process = env.process(self.schedule_process())
        self.name = name
        self.description = description or "A scheduler using Round Robin (RR) policy."

    def schedule_process(self) -> None:
        """
        Executes process scheduling logic for Round Robin(RR) Scheduler.
        """
        while len(self.completed) < self.total:
            if not self.ready_queue:
                yield self.env.timeout(1)
                continue
            
            proc = self.ready_queue.pop(0)
            
            if proc.start is None:
                proc.start = self.env.now
                proc.response = proc.start - proc.arrival
            
            exec_time = min(self.time_quantum, proc.remaining)
            print(f"Time {self.env.now}: Process {proc.pid} runs for {exec_time} time units (RR)")
            yield self.env.timeout(exec_time)
            proc.remaining -= exec_time
            
            if proc.remaining == 0:
                proc.completion = self.env.now
                proc.turnaround = proc.completion - proc.arrival
                proc.waiting = proc.turnaround - proc.burst
                print(f"Time {self.env.now}: Process {proc.pid} finishes (RR)")
                self.completed.append(proc)
            else:
                # Re-queue the process if it's not finished.
                self.ready_queue.append(proc)


