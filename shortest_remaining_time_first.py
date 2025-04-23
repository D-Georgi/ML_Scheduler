

from __future__ import annotations
from typing import List, Optional
import simpy

# SRTF (Preemptive SJF) Scheduler
class ShortestRemainingTimeFirstScheduler:
    """ Class for Shortest Remaining Time First (SRTF) Scheduler. 
    This scheduler selects the process with the smallest remaining execution time and
      preempts the currently running process if necessary. """

    def __init__(self, env:simpy.Environment, ready_queue: List, completed: List, total: int, 
                 name: str="SRTF Scheduler", description: Optional[str] = None) -> None:
        """
        Initializes the Shortest Run Time First (SRTF) scheduler.
        
        :param env: The simulation environment.
        :param ready_queue: List of processes ready to execute.
        :param completed: List to store completed processes.
        :param total: Total number of processes.
        """
        self.name = name
        self.description = description or " This is Shortest Run Time First Scheduler(SRTF). "
        self.env = env
        self.ready_queue = ready_queue
        self.completed = completed
        self.total = total
        self.current_proc = None
        self.process = env.process(self.schedule_process())


    def schedule_process(self) -> None:
         """ Executes class logic for Shortest Run Time First SRTF Scheduler. """

         while len(self.completed) < self.total:
            if not self.ready_queue and self.current_proc is None:
                yield self.env.timeout(1)
                continue
            # Combine current running process (if any) with ready_queue candidates.
            candidates = self.ready_queue.copy()
            if self.current_proc:
                candidates.append(self.current_proc)

            proc = min(candidates, key=lambda p: p.remaining)
            if proc != self.current_proc:
                if self.current_proc is not None:
                    self.ready_queue.append(self.current_proc)

                start = self.env.now
                self.current_proc = proc
                self.current_proc.timeline.append((start, 0))

                if self.current_proc in self.ready_queue:
                    self.ready_queue.remove(self.current_proc)

                if self.current_proc.start is None:
                    self.current_proc.start = self.env.now
                    self.current_proc.response = self.current_proc.start - self.current_proc.arrival
                    print(f"Time {self.env.now}: Process {self.current_proc.pid} is now running (Shortest Run Time First)..")

            # Run for one time unit.
            yield self.env.timeout(1)
            seg_start, seg_len = self.current_proc.timeline[-1]
            self.current_proc.timeline[-1] = (seg_start, seg_len + 1)
            self.current_proc.remaining -= 1

            # Check if process finished.
            if self.current_proc.remaining == 0:
                self.current_proc.completion = self.env.now
                self.current_proc.turnaround = self.current_proc.completion - self.current_proc.arrival
                self.current_proc.waiting = self.current_proc.turnaround - self.current_proc.burst
                print(f"Time {self.env.now}: Process {self.current_proc.pid} finished (Shortest Run Time First)..")
                self.completed.append(self.current_proc)
                self.current_proc = None

