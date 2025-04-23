import simpy
import random
from process_generation import generate_processes

# -------------------------------
# ML Scheduler Agent with Q-Learning
# -------------------------------
class MLSchedulerAgent:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.alpha = alpha            # learning rate
        self.gamma = gamma            # discount factor
        self.epsilon = epsilon        # exploration rate
        self.Q = {}                   # Q-table: {(state, action): value}

    def get_state(self, ready_queue, current_time):
        # State: tuple of sorted remaining burst times in ready queue
        return tuple(sorted(p.remaining for p in ready_queue))

    def choose_action(self, state):
        # Epsilon-greedy action selection
        if not state:
            return None
        if random.random() < self.epsilon:
            return random.randrange(len(state))
        # Select action with highest Q-value
        q_vals = [self.Q.get((state, a), 0.0) for a in range(len(state))]
        max_q = max(q_vals)
        best_actions = [i for i, q in enumerate(q_vals) if q == max_q]
        return random.choice(best_actions)

    def learn(self, state, action, reward, next_state):
        # Q-learning update
        old_q = self.Q.get((state, action), 0.0)
        # Estimate optimal future value
        if next_state:
            future_qs = [self.Q.get((next_state, a), 0.0) for a in range(len(next_state))]
            best_future = max(future_qs)
        else:
            best_future = 0.0
        # Update rule
        self.Q[(state, action)] = old_q + self.alpha * (reward + self.gamma * best_future - old_q)

# -------------------------------
# Arrival Process
# -------------------------------
def arrival(env, proc, ready_queue):
    yield env.timeout(proc.arrival - env.now)
    ready_queue.append(proc)
    print(f"Time {env.now}: Process {proc.pid} arrives.")

# -------------------------------
# ML-Based Scheduler Process using SimPy
# -------------------------------
def scheduler_ml(env, ready_queue, completed, total, agent):
    while len(completed) < total:
        if not ready_queue:
            # No ready process, advance time
            yield env.timeout(1)
            continue

        state = agent.get_state(ready_queue, env.now)
        action = agent.choose_action(state)
        if action is None:
            yield env.timeout(1)
            continue

        proc = ready_queue.pop(action)
        if proc.start is None:
            proc.start = env.now
            proc.response = proc.start - proc.arrival

        # Execute for one time unit (could be modified)
        exec_time = 1
        print(f"Time {env.now}: ML Agent schedules Process {proc.pid} for {exec_time} time unit")
        yield env.timeout(exec_time)
        proc.remaining -= exec_time

        # Reward: negative remaining time to encourage shorter jobs
        reward = -proc.remaining
        next_state = agent.get_state(ready_queue, env.now)
        agent.learn(state, action, reward, next_state)

        if proc.remaining > 0:
            ready_queue.append(proc)
        else:
            proc.completion = env.now
            proc.turnaround = proc.completion - proc.arrival
            proc.waiting = proc.turnaround - proc.burst
            print(f"Time {env.now}: Process {proc.pid} finishes (ML Scheduler)")
            completed.append(proc)

# -------------------------------
# Simulation Wrapper
# -------------------------------
def run_simulation_ml(process_list, scheduler_func, agent):
    total = len(process_list)
    env = simpy.Environment()
    ready_queue = []
    completed = []

    # Spawn arrival events
    for p in process_list:
        env.process(arrival(env, p, ready_queue))
    # Spawn scheduler
    env.process(scheduler_func(env, ready_queue, completed, total, agent))
    env.run()
    return completed

# -------------------------------
# Training Loop for Agent
# -------------------------------
def train_agent(agent, episodes=100, num_procs=5):
    for ep in range(episodes):
        procs = generate_processes(num_procs, seed=ep)
        _ = run_simulation_ml(procs, scheduler_ml, agent)
    print("Training completed.")

# -------------------------------
# Example Usage
# -------------------------------
if __name__ == "__main__":
    # Initialize agent
    agent = MLSchedulerAgent(alpha=0.1, gamma=0.9, epsilon=0.2)

    # Train agent
    train_agent(agent, episodes=200, num_procs=5)

    # Test on new set of processes
    sample_processes = generate_processes(100, seed=42)
    results_ml = run_simulation_ml(sample_processes, scheduler_ml, agent)

    print("\n--- ML-Based Scheduler Results ---")
    for p in sorted(results_ml, key=lambda x: x.pid):
        print(
            f"{p.pid}: Arrival={p.arrival}, Burst={p.burst}, Start={p.start}, "
            f"Completion={p.completion}, Waiting={p.waiting}, Turnaround={p.turnaround}, Response={p.response}"
        )
