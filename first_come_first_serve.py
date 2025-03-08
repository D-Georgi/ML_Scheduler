

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

