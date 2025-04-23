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
        self.timeline: list[tuple[float, float]] = []

    def __repr__(self):
        return f"{self.pid}(arrival={self.arrival}, burst={self.burst}, priority={self.priority})"


def generate_processes(n, max_arrival=4, max_burst=10, max_priority=3, seed=None) -> list:
    """Function for Generating Processes, returns a list of processes
    \nParams: n (number of processes), seed (random.seed)"""
    if seed is not None:
        random.seed(seed)
    processes = []
    arrival_time = 0
    for i in range(n):
        #arrival time of a process is strictly increasing and chosen to be between 1 and max units of time
        arrival_time += random.randint(1, max_arrival)

        #burst time chosen to be between 1 and max (inclusive) units of time
        burst_time = random.randint(1, max_burst)

        #priority is designated from high to low (0 -> max)
        priority = random.randint(1, max_priority)

        processes.append(Process(f"P{i + 1}", arrival=arrival_time, burst=burst_time, priority=priority))
    return processes
