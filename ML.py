import simpy
import random
from process_generation import generate_processes

# -------------------------------
# ML Scheduler Agent with Q-Learning
# -------------------------------
class MLSchedulerAgent:
    def __init__(self, alpha=0.1, gamma=0.99, epsilon=0.2,
                 epsilon_decay=0.995, min_epsilon=0.01):
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon
        self.Q = {}

    def get_state(self, ready_queue, current_time):
        rems = tuple(sorted(p.remaining for p in ready_queue))
        qlen = len(rems)
        avg_rem = sum(rems)/qlen if qlen else 0
        return (rems, qlen, int(avg_rem))

    def choose_action(self, state):
        if not state[0]:
            return None
        if random.random() < self.epsilon:
            return random.randrange(len(state[0]))
        q_vals = [self.Q.get((state, a), 0.0) for a in range(len(state[0]))]
        max_q = max(q_vals)
        best = [i for i,q in enumerate(q_vals) if q==max_q]
        return random.choice(best)

    def learn(self, state, action, reward, next_state):
        old = self.Q.get((state, action), 0.0)
        if next_state[0]:
            future = max(self.Q.get((next_state, a), 0.0) for a in range(len(next_state[0])))
        else:
            future = 0.0
        self.Q[(state, action)] = old + self.alpha*(reward + self.gamma*future - old)

    def train(self, episodes=500, num_procs=5):
        for ep in range(episodes):
            procs = generate_processes(num_procs, seed=ep)
            _ = run_simulation_ml(procs, scheduler_ml, self)
            self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)
        print("Training completed.")

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
            yield env.timeout(1)
            continue

        state = agent.get_state(ready_queue, env.now)
        action = agent.choose_action(state)
        if action is None:
            yield env.timeout(1)
            continue

        # map to the k-th shortest remaining job
        sorted_procs = sorted(ready_queue, key=lambda p: p.remaining)
        proc = sorted_procs[action]
        ready_queue.remove(proc)

        if proc.start is None:
            proc.start = env.now
            proc.response = proc.start - proc.arrival

        # run one time unit
        yield env.timeout(1)
        proc.remaining -= 1

        # reward = - waiting queue length per time step
        reward = -len(ready_queue)
        if proc.remaining == 0:
            proc.completion = env.now
            proc.turnaround = proc.completion - proc.arrival
            proc.waiting = proc.turnaround - proc.burst
            reward += 10  # bonus for finishing
            completed.append(proc)
        else:
            ready_queue.append(proc)

        next_state = agent.get_state(ready_queue, env.now)
        agent.learn(state, action, reward, next_state)

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
