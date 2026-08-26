"""Reproducible local policy-decision benchmark; prints raw results only."""

from __future__ import annotations

import argparse
import statistics
import time

from pais_governance.core.policy_engine import PolicyEngine, create_default_policies


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=10_000)
    args = parser.parse_args()
    engine = PolicyEngine(create_default_policies())
    request = {
        "trigger": "agent_tool_call",
        "agent_id": "benchmark",
        "tool": "database",
        "operation": "read",
        "environment": "staging",
    }
    timings = []
    for _ in range(args.iterations):
        started = time.perf_counter_ns()
        engine.evaluate(request)
        timings.append((time.perf_counter_ns() - started) / 1_000)
    timings.sort()
    p95 = timings[int(len(timings) * 0.95) - 1]
    print(
        {
            "iterations": args.iterations,
            "unit": "microseconds",
            "median": round(statistics.median(timings), 3),
            "p95": round(p95, 3),
        }
    )


if __name__ == "__main__":
    main()
