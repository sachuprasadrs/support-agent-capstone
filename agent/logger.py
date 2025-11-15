import json
import time
import os

TRACE_FILE = os.getenv("TRACE_FILE", "traces.jl")


def log_event(event: dict):
    event["timestamp"] = time.time()
    with open(TRACE_FILE, "a") as f:
        f.write(json.dumps(event) + "\n")
