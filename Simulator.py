#!/bin/python3

# Import libraries
import simpy
import copy
from process_generation import generate_processes

# Imports from project
from first_come_first_serve import FirstComeFirstServeScheduler
from round_robin_scheduler import RoundRobinScheduler
from shortest_remaining_time_first import ShortestRemainingTimeFirstScheduler
from shortest_job_first import ShortestJobFirstScheduler
from priority_scheduler import PriorityScheduler


# -------------------------------
# Simulation Functions
# -------------------------------
def run_simulation(process_list, scheduler_class, **scheduler_kwargs):

    # -------------------------------
    # Arrival Process
    # -------------------------------
    def arrival(env, proc, ready_queue):
        """Wait until process arrival and then add it to the ready queue."""
        yield env.timeout(proc.arrival - env.now)
        ready_queue.append(proc)
        print(f"Time {env.now}: Process {proc.pid} arrives.")

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
    return run_simulation(copy.deepcopy(process_list), FirstComeFirstServeScheduler)

def simulate_sjf(process_list):
    return run_simulation(copy.deepcopy(process_list), ShortestJobFirstScheduler)

def simulate_srtf(process_list):
    return run_simulation(copy.deepcopy(process_list), ShortestRemainingTimeFirstScheduler)

def simulate_priority(process_list):
    return run_simulation(copy.deepcopy(process_list), PriorityScheduler)

def simulate_rr(process_list, time_quantum):
    return run_simulation(copy.deepcopy(process_list), RoundRobinScheduler, time_quantum=time_quantum)

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
sample_processes = generate_processes(100, seed=42)

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
