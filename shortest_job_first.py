


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

