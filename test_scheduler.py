from process_generation import generate_processes
from first_come_first_serve import FirstComeFirstServeScheduler
import simpy

# Generate just 3 processes for testing
processes = generate_processes(3, seed=42)

print("Generated Processes:")
for p in processes:
    print(f"Process {p.pid}: Arrival={p.arrival}, Burst={p.burst}, Priority={p.priority}")

print("\nRunning FCFS Simulation:")
env = simpy.Environment()
ready_queue = []
completed = []

# Arrival process
def arrival(env, proc, ready_queue):
    yield env.timeout(proc.arrival - env.now)
    ready_queue.append(proc)
    print(f"Time {env.now}: Process {proc.pid} arrives.")

# Spawn arrival processes
for p in processes:
    env.process(arrival(env, p, ready_queue))

# Create and run scheduler
scheduler = FirstComeFirstServeScheduler(env, ready_queue, completed, len(processes))
env.run()

print("\nResults:")
print("PID\tArrival\tBurst\tStart\tCompletion\tWaiting\tTurnaround")
for p in completed:
    print(f"{p.pid}\t{p.arrival}\t{p.burst}\t{p.start}\t{p.completion}\t\t{p.waiting}\t{p.turnaround}")

# Calculate averages
avg_turnaround = sum(p.turnaround for p in completed) / len(completed)
avg_waiting = sum(p.waiting for p in completed) / len(completed)

print(f"\nAverage Turnaround Time: {avg_turnaround:.2f}")
print(f"Average Waiting Time: {avg_waiting:.2f}") 
