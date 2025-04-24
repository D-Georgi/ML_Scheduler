#!/bin/python3

# Import libraries
import simpy
import copy
import matplotlib.pyplot as plt
import numpy as np
import sys
from matplotlib import colors as mcolors
from typing import Final

# Imports for ML scheduling
from ML import MLSchedulerAgent, train_agent, run_simulation_ml, scheduler_ml

# Imports from project
from process_generation import generate_processes
from first_come_first_serve import FirstComeFirstServeScheduler
from round_robin_scheduler import RoundRobinScheduler
from shortest_remaining_time_first import ShortestRemainingTimeFirstScheduler
from shortest_job_first import ShortestJobFirstScheduler
from priority_scheduler import PriorityScheduler

# Set number of processes to generate and evaluate scheduling algorithm
NUMBER_OF_PROCESSES_GENERATED : Final = 100

# Force output to be unbuffered
sys.stdout.reconfigure(line_buffering=True)

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

# Wrapper for ML-based scheduler
def simulate_ml(process_list, agent):
    return run_simulation_ml(copy.deepcopy(process_list), scheduler_ml, agent)

# -------------------------------
# Utility to Print Results
# -------------------------------
def print_results(algorithm_name, processes):
    print(f"\n--- {algorithm_name} ---")
    print("PID\tArrival\tBurst\tStart\tCompletion\tWaiting\tTurnaround\tResponse")
    for p in sorted(processes, key=lambda p: p.pid):
        print(f"{p.pid}\t{p.arrival}\t{p.burst}\t{p.start}\t{p.completion}\t\t{p.waiting}\t{p.turnaround}\t\t{p.response}")

def calculate_metrics(processes):
    """Calculate average turnaround time and average wait time for a list of processes."""
    total_turnaround = sum(p.turnaround for p in processes)
    total_wait = sum(p.waiting for p in processes)
    avg_turnaround = total_turnaround / len(processes)
    avg_wait = total_wait / len(processes)
    return avg_turnaround, avg_wait

# -------------------------------
# Visualization
# -------------------------------
def visualize_metrics(results_dict):
    """Create bar charts for average turnaround time and average wait time."""
    algorithms = list(results_dict.keys())
    avg_turnaround_times = [results_dict[alg]['turnaround'] for alg in algorithms]
    avg_wait_times = [results_dict[alg]['wait'] for alg in algorithms]

    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Plot average turnaround time
    ax1.bar(algorithms, avg_turnaround_times)
    ax1.set_title('Average Turnaround Time')
    ax1.set_ylabel('Time Units')
    ax1.tick_params(axis='x', rotation=45)

    # Plot average wait time
    ax2.bar(algorithms, avg_wait_times)
    ax2.set_title('Average Wait Time')
    ax2.set_ylabel('Time Units')
    ax2.tick_params(axis='x', rotation=45)

    plt.tight_layout()
    plt.savefig('scheduling_metrics.png')
    plt.show()

def visualize_gantt(results_dict):
    """
    results_dict: { 'FCFS': [proc1,proc2...], 'SJF': [...], ... }
    each proc.timeline is a list of (start, duration) tuples.
    """
    n = len(results_dict)
    fig, axes = plt.subplots(n, 1, figsize=(12, 2*n), sharex=True)
    if n == 1: axes = [axes]
    tableau_colors = list(mcolors.TABLEAU_COLORS.values())  # Get Tableau colors

    for ax, (alg, procs) in zip(axes, results_dict.items()):
        # map each PID to a y-row
        #pid_to_row = {p.pid: i for i,p in enumerate(sorted(procs, key=lambda x:int(x.pid[1:])))}
        pid_list = sorted(set(p.pid for p in procs), key=lambda x: int(x[1:]))
        pid_to_row = {pid: i for i, pid in enumerate(pid_list)}
        pid_to_color = {pid: tableau_colors[i % len(tableau_colors)] for i, pid in enumerate(pid_list)}
        for p in procs:
            row = pid_to_row[p.pid]
            color = pid_to_color[p.pid]
            for (start, length) in p.timeline:
                ax.broken_barh([(start, length)], (row*10, 9), facecolor=color)
        ax.set_yticks([row*10+4 for row in pid_to_row.values()])
        ax.set_yticklabels(list(pid_to_row.keys()))
        ax.set_ylabel(alg)
    axes[-1].set_xlabel("Time")
    plt.tight_layout()
    plt.savefig('gantt_chart.png')
    plt.show()

# -------------------------------
# Sample Process List and Simulations
# -------------------------------
print("\n" + "="*50)
print("Starting CPU Scheduler Simulation")
print("="*50 + "\n")

# Generate a smaller number of processes for clearer demonstration
sample_processes = generate_processes(NUMBER_OF_PROCESSES_GENERATED, seed=42)

print("Generated Processes:")
print("-"*30)
for p in sample_processes:
    print(f"Process {p.pid}: Arrival={p.arrival}, Burst={p.burst}, Priority={p.priority}")

print("\n" + "="*50)
print("Running Simulations")
print("="*50 + "\n")

# Run simulations for each scheduling algorithm.
print("Running FCFS...")
results_fcfs = simulate_fcfs(sample_processes)
print("\nRunning SJF...")
results_sjf = simulate_sjf(sample_processes)
print("\nRunning SRTF...")
results_srtf = simulate_srtf(sample_processes)
print("\nRunning Priority...")
results_prio = simulate_priority(sample_processes)
print("\nRunning Round Robin...")
results_rr = simulate_rr(sample_processes, time_quantum=3)

# Initialize and train ML Scheduler Agent
print("\nRunning ML-based Scheduler Training...")
agent = MLSchedulerAgent(alpha=0.1, gamma=0.9, epsilon=0.2)
train_agent(agent, episodes=200, num_procs=len(sample_processes))

# Run ML-based scheduler
print("\nRunning ML-Based Scheduler...")
results_ml = simulate_ml(sample_processes, agent)

# Calculate metrics for each algorithm
metrics = {
    'FCFS': calculate_metrics(results_fcfs),
    'SJF': calculate_metrics(results_sjf),
    'SRTF': calculate_metrics(results_srtf),
    'Priority': calculate_metrics(results_prio),
    'Round Robin': calculate_metrics(results_rr),
    'ML-Based': calculate_metrics(results_ml)
}

# Convert metrics to dictionary format for visualization
results_dict = {alg: {'turnaround': val[0], 'wait': val[1]} for alg, val in metrics.items()}

timelines = {
    'FCFS'          : results_fcfs,
    'SJF'           : results_sjf,
    'SRTF'          : results_srtf,
    'Priority'      : results_prio,
    'Round Robin'   : results_rr,
    'ML-Based'      : results_ml,
}

visualize_gantt(timelines)

print("\n" + "="*50)
print("Detailed Results")
print("="*50 + "\n")

# Print detailed results
print_results("First Come First Serve (FCFS)", results_fcfs)
print_results("Shortest Job First (SJF)", results_sjf)
print_results("Shortest Remaining Time First (SRTF)", results_srtf)
print_results("Priority Scheduling", results_prio)
print_results("Round Robin (Time Quantum = 3)", results_rr)
print_results("ML-Based Scheduler", results_ml)

print("\n" + "="*50)
print(f"Average Metrics (Num of processes evaluated: {NUMBER_OF_PROCESSES_GENERATED})")
print("="*50 + "\n")
# Ensure output format in terminal is perfectly aligned for columns and their respective data
print(f"{'Algorithm':<15} {'Avg Turnaround':>15} {'Avg Wait':>15}")
print("-" * 50)
for alg, (turnaround, wait) in metrics.items():
    print(f"{alg:<15}\t{turnaround:>8.2f}\t\t{wait:>8.2f}")

print("\n" + "="*50)
print("Generating Visualization")
print("="*50 + "\n")

# Visualize the metrics
visualize_metrics(results_dict)
print("\nVisualization has been saved as 'scheduling_metrics.png'")
