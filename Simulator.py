#!/bin/python3

# Import libraries
import simpy
import copy

# Imports from project
from first_come_first_serve import scheduler_fcfs
from round_robin_scheduler import scheduler_rr
from shortest_remaining_time_first import ShortestRemainingTimeFirstScheduler
from shortest_job_first import scheduler_sjf

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

# -------------------------------
# Arrival Process
# -------------------------------
def arrival(env, proc, ready_queue):
    """Wait until process arrival and then add it to the ready queue."""
    yield env.timeout(proc.arrival - env.now)
    ready_queue.append(proc)
    print(f"Time {env.now}: Process {proc.pid} arrives.")

# -------------------------------
# Scheduler Functions
# -------------------------------



# Priority Scheduler (Non-preemptive; lower number = higher priority)
def scheduler_priority(env, ready_queue, completed, total):
    while len(completed) < total:
        if not ready_queue:
            yield env.timeout(1)
            continue
        # Select process with the highest priority.
        proc = min(ready_queue, key=lambda p: p.priority)
        ready_queue.remove(proc)
        if proc.start is None:
            proc.start = env.now
            proc.response = proc.start - proc.arrival
        print(f"Time {env.now}: Process {proc.pid} starts execution for {proc.burst} time units (Priority)")
        yield env.timeout(proc.burst)
        proc.completion = env.now
        proc.turnaround = proc.completion - proc.arrival
        proc.waiting = proc.start - proc.arrival
        completed.append(proc)


# -------------------------------
# Simulation Functions
# -------------------------------
def run_simulation(process_list, scheduler_class, **scheduler_kwargs):
    total = len(process_list)
    env = simpy.Environment()
    ready_queue = []
    completed = []
    # Spawn arrival processes for each process.
    for p in process_list:
        env.process(arrival(env, p, ready_queue))
    # Spawn the scheduler process.
    scheduler_class(env, ready_queue, completed, total, **scheduler_kwargs)
    env.run()
    return completed

# Wrapper functions for each scheduling algorithm.
def simulate_fcfs(process_list):
    return run_simulation(copy.deepcopy(process_list), scheduler_fcfs)

def simulate_sjf(process_list):
    return run_simulation(copy.deepcopy(process_list), scheduler_sjf)

def simulate_srtf(process_list):
    return run_simulation(copy.deepcopy(process_list), ShortestRemainingTimeFirstScheduler)

def simulate_priority(process_list):
    return run_simulation(copy.deepcopy(process_list), scheduler_priority)

def simulate_rr(process_list, time_quantum):
    return run_simulation(copy.deepcopy(process_list), scheduler_rr, time_quantum=time_quantum)

# -------------------------------
# Utility to Print Results
# -------------------------------
def print_results(algorithm_name, processes):
    print(f"\n--- {algorithm_name} ---")
    print("PID\tArrival\tBurst\tStart\tCompletion\tWaiting\tTurnaround\tResponse")
    for p in sorted(processes, key=lambda p: p.pid):
        print(f"{p.pid}\t{p.arrival}\t{p.burst}\t{p.start}\t{p.completion}\t\t{p.waiting}\t{p.turnaround}\t\t{p.response}")

# -------------------------------
# Sample Process List and Simulations
# -------------------------------
sample_processes = [
    Process("P1", arrival=0, burst=8, priority=2),
    Process("P2", arrival=1, burst=4, priority=1),
    Process("P3", arrival=2, burst=9, priority=3),
    Process("P4", arrival=3, burst=5, priority=2)
]

# Run simulations for each scheduling algorithm.
#results_fcfs   = simulate_fcfs(sample_processes)
#results_sjf    = simulate_sjf(sample_processes)
results_srtf   = simulate_srtf(sample_processes)
#results_prio   = simulate_priority(sample_processes)
#results_rr     = simulate_rr(sample_processes, time_quantum=3)

# Print the results.
#print_results("First Come First Serve (FCFS)", results_fcfs)
#print_results("Shortest Job First (SJF)", results_sjf)
print_results("Shortest Remaining Time First (SRTF)", results_srtf)
#print_results("Priority Scheduling", results_prio)
#print_results("Round Robin (Time Quantum = 3)", results_rr)
