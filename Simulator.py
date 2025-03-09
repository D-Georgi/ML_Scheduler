import simpy
import copy
import process_generation
from process_generation import generate_processes


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
#Demonstration
#Demonstration
#Demonstration

# FCFS Scheduler
def scheduler_fcfs(env, ready_queue, completed, total):
    while len(completed) < total:
        if not ready_queue:
            yield env.timeout(1)
            continue
        # FCFS: take the first process in ready queue.
        proc = ready_queue.pop(0)
        if proc.start is None:
            proc.start = env.now
            proc.response = proc.start - proc.arrival
        print(f"Time {env.now}: Process {proc.pid} starts execution for {proc.burst} time units (FCFS)")
        yield env.timeout(proc.burst)
        proc.completion = env.now
        proc.turnaround = proc.completion - proc.arrival
        proc.waiting = proc.start - proc.arrival
        completed.append(proc)

# SJF (Non-preemptive) Scheduler
def scheduler_sjf(env, ready_queue, completed, total):
    while len(completed) < total:
        if not ready_queue:
            yield env.timeout(1)
            continue
        # Select the process with the smallest burst time.
        proc = min(ready_queue, key=lambda p: p.burst)
        ready_queue.remove(proc)
        if proc.start is None:
            proc.start = env.now
            proc.response = proc.start - proc.arrival
        print(f"Time {env.now}: Process {proc.pid} starts execution for {proc.burst} time units (SJF)")
        yield env.timeout(proc.burst)
        proc.completion = env.now
        proc.turnaround = proc.completion - proc.arrival
        proc.waiting = proc.start - proc.arrival
        completed.append(proc)

# SRTF (Preemptive SJF) Scheduler
def scheduler_srtf(env, ready_queue, completed, total):
    current_proc = None
    while len(completed) < total:
        if not ready_queue and current_proc is None:
            yield env.timeout(1)
            continue
        # Combine current running process (if any) with ready_queue candidates.
        candidates = ready_queue.copy()
        if current_proc:
            candidates.append(current_proc)
        # Select process with the smallest remaining time.
        proc = min(candidates, key=lambda p: p.remaining)
        if proc != current_proc:
            # Preempt if necessary.
            current_proc = proc
            if current_proc in ready_queue:
                ready_queue.remove(current_proc)
            if current_proc.start is None:
                current_proc.start = env.now
                current_proc.response = current_proc.start - current_proc.arrival
            print(f"Time {env.now}: Process {current_proc.pid} is now running (SRTF)")
        # Run for one time unit.
        yield env.timeout(1)
        current_proc.remaining -= 1
        # Check if process finished.
        if current_proc.remaining == 0:
            current_proc.completion = env.now
            current_proc.turnaround = current_proc.completion - current_proc.arrival
            current_proc.waiting = current_proc.turnaround - current_proc.burst
            print(f"Time {env.now}: Process {current_proc.pid} finishes (SRTF)")
            completed.append(current_proc)
            current_proc = None

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

# Round Robin Scheduler
def scheduler_rr(env, ready_queue, completed, total, time_quantum):
    while len(completed) < total:
        if not ready_queue:
            yield env.timeout(1)
            continue
        proc = ready_queue.pop(0)
        if proc.start is None:
            proc.start = env.now
            proc.response = proc.start - proc.arrival
        exec_time = min(time_quantum, proc.remaining)
        print(f"Time {env.now}: Process {proc.pid} runs for {exec_time} time units (RR)")
        yield env.timeout(exec_time)
        proc.remaining -= exec_time
        if proc.remaining == 0:
            proc.completion = env.now
            proc.turnaround = proc.completion - proc.arrival
            proc.waiting = proc.turnaround - proc.burst
            print(f"Time {env.now}: Process {proc.pid} finishes (RR)")
            completed.append(proc)
        else:
            # Re-queue the process if it's not finished.
            ready_queue.append(proc)

# -------------------------------
# Simulation Functions
# -------------------------------
def run_simulation(process_list, scheduler_func, **scheduler_kwargs):
    total = len(process_list)
    env = simpy.Environment()
    ready_queue = []
    completed = []
    # Spawn arrival processes for each process.
    for p in process_list:
        env.process(arrival(env, p, ready_queue))
    # Spawn the scheduler process.
    env.process(scheduler_func(env, ready_queue, completed, total, **scheduler_kwargs))
    env.run()
    return completed

# Wrapper functions for each scheduling algorithm.
def simulate_fcfs(process_list):
    return run_simulation(copy.deepcopy(process_list), scheduler_fcfs)

def simulate_sjf(process_list):
    return run_simulation(copy.deepcopy(process_list), scheduler_sjf)

def simulate_srtf(process_list):
    return run_simulation(copy.deepcopy(process_list), scheduler_srtf)

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
sample_processes = generate_processes(10, seed=5500)

# Run simulations for each scheduling algorithm.
results_fcfs   = simulate_fcfs(sample_processes)
results_sjf    = simulate_sjf(sample_processes)
results_srtf   = simulate_srtf(sample_processes)
results_prio   = simulate_priority(sample_processes)
results_rr     = simulate_rr(sample_processes, time_quantum=3)

# Print the results.
print_results("First Come First Serve (FCFS)", results_fcfs)
print_results("Shortest Job First (SJF)", results_sjf)
print_results("Shortest Remaining Time First (SRTF)", results_srtf)
print_results("Priority Scheduling", results_prio)
print_results("Round Robin (Time Quantum = 3)", results_rr)
