

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

