import random

# -------------------------------
# Process Class Definition
# -------------------------------
class Process:
    def __init__(self, pid, arrival, burst, priority=0):
        self.pid = pid            # Process ID
        self.arrival = arrival    # Arrival time
        self.burst = burst        # Total burst time
        self.remaining = burst    # Remaining time (for preemptive algorithms)
        self.priority = priority  # Priority (lower number = higher priority)
        self.start = None         # Time when process first gets CPU
        self.completion = None    # Time when process finishes
        self.response = None      # Response time (start - arrival)
        self.waiting = 0          # Total waiting time
        self.turnaround = 0       # Turnaround time (completion - arrival)

    def __repr__(self):
        return f"{self.pid}(arrival={self.arrival}, burst={self.burst}, priority={self.priority})"


def generate_processes(n, seed=None) -> list:
    """Function for Generating Processes, returns a list of processes
    \nParams: n (number of processes), seed (random.seed)"""
    if seed is not None:
        random.seed(seed)
    processes = []
    arrival_time = 0
    for i in range(n):
        arrival_time += random.randint(1, 4)
        burst_time = random.randint(3, 10)
        priority = random.randint(1, 3)
        processes.append(Process(f"P{i + 1}", arrival=arrival_time, burst=burst_time, priority=priority))
    return processes