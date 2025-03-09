import simpy
import random
from process_generation import generate_processes

# -------------------------------
# Arrival Process
# -------------------------------
def arrival(env, proc, ready_queue):
    """Wait until process arrival and then add it to the ready queue."""
    yield env.timeout(proc.arrival - env.now)
    ready_queue.append(proc)
    print(f"Time {env.now}: Process {proc.pid} arrives.")

# --- Agent Skeleton ---
class MLSchedulerAgent:
    def __init__(self, time_quantum=3):
        self.time_quantum = time_quantum
        # In a real implementation, you might initialize a Q-table or a neural network here.

    def get_state(self, ready_queue, current_time):
        # Create a simple state representation.
        # For instance, you could return a list of remaining burst times.
        return [p.remaining for p in ready_queue]

    def choose_action(self, state):
        # For now, choose an action randomly.
        # In a learning agent, this would be where you select based on your policy (e.g., epsilon-greedy).
        if not state:
            return None
        return random.randint(0, len(state) - 1)

    def learn(self, state, action, reward, next_state):
        # Update your model/policy here.
        pass


# --- ML-Based Scheduler Process using SimPy ---
def scheduler_ml(env, ready_queue, completed, total, agent):
    while len(completed) < total:
        if not ready_queue:
            yield env.timeout(1)
            continue

        # Get the current state representation from the ready queue.
        state = agent.get_state(ready_queue, env.now)
        # Agent decides which process to schedule.
        action = agent.choose_action(state)
        if action is None:
            yield env.timeout(1)
            continue

        proc = ready_queue.pop(action)
        if proc.start is None:
            proc.start = env.now
            proc.response = proc.start - proc.arrival

        # Decide execution time. Here, we use a fixed time quantum,
        # but the agent could also learn to decide a dynamic exec_time.
        exec_time = min(agent.time_quantum, proc.remaining)
        print(f"Time {env.now}: ML Agent schedules Process {proc.pid} for {exec_time} time units")
        yield env.timeout(exec_time)
        proc.remaining -= exec_time

        # Compute a simple reward (e.g., negative for long waiting times)
        reward = -exec_time  # This is a placeholder. Design a reward function based on your goals.
        next_state = agent.get_state(ready_queue, env.now)
        agent.learn(state, action, reward, next_state)

        if proc.remaining > 0:
            # If not finished, re-add the process to the ready queue.
            ready_queue.append(proc)
        else:
            proc.completion = env.now
            proc.turnaround = proc.completion - proc.arrival
            proc.waiting = proc.turnaround - proc.burst
            print(f"Time {env.now}: Process {proc.pid} finishes (ML Scheduler)")
            completed.append(proc)


# --- Simulation Wrapper (similar to previous examples) ---
def run_simulation_ml(process_list, scheduler_func, agent):
    total = len(process_list)
    env = simpy.Environment()
    ready_queue = []
    completed = []
    # Spawn arrival processes for each process.
    for p in process_list:
        env.process(arrival(env, p, ready_queue))
    # Spawn the ML-based scheduler process.
    env.process(scheduler_func(env, ready_queue, completed, total, agent))
    env.run()
    return completed


# Example usage:
if __name__ == "__main__":
    # Define your Process class and arrival process as in previous examples.
    sample_processes = generate_processes(4, seed=42)

    # Create an ML agent instance.
    agent = MLSchedulerAgent(time_quantum=3)
    results_ml = run_simulation_ml(sample_processes, scheduler_ml, agent)

    # Print results.
    print("\n--- ML-Based Scheduler Results ---")
    for p in sorted(results_ml, key=lambda p: p.pid):
        print(
            f"{p.pid}: Arrival={p.arrival}, Burst={p.burst}, Start={p.start}, Completion={p.completion}, Waiting={p.waiting}, Turnaround={p.turnaround}, Response={p.response}")
