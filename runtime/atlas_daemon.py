"""Atlas OS v0.2 autonomous runtime daemon.

This module is launchd-compatible and keeps the event-driven decision loop
running in the background. It does not trade, modify portfolio files, or bypass
CDE.
"""

from __future__ import annotations

import argparse
import signal
import sys
from pathlib import Path

try:
    from runtime.decision_loop import DecisionLoop, DecisionLoopConfig
    from runtime.logging import log_execution, utc_now_iso
except ModuleNotFoundError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from runtime.decision_loop import DecisionLoop, DecisionLoopConfig
    from runtime.logging import log_execution, utc_now_iso


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Atlas OS autonomous runtime daemon")
    parser.add_argument("--interval", type=int, default=60)
    parser.add_argument("--heartbeat-interval", type=int, default=300)
    parser.add_argument("--max-events", type=int, default=5)
    parser.add_argument("--log-path", default=None)
    parser.add_argument("--db-path", default=None)
    parser.add_argument("--inbox-dir", default=None)
    parser.add_argument("--llm-model", default="gpt-5.5")
    parser.add_argument("--once", action="store_true", help="run one daemon cycle and exit")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    loop = DecisionLoop(
        DecisionLoopConfig(
            sleep_interval_seconds=args.interval,
            heartbeat_interval_seconds=args.heartbeat_interval,
            max_events_per_cycle=args.max_events,
            log_path=args.log_path,
            db_path=args.db_path,
            inbox_dir=args.inbox_dir,
            llm_model=args.llm_model,
        )
    )

    def stop(*_signal_args: object) -> None:
        log_execution(
            {
                "timestamp": utc_now_iso(),
                "trigger_type": "atlas_daemon_stop",
                "status": "stopping",
            },
            log_path=args.log_path,
        )
        loop.stop()

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    log_execution(
        {
            "timestamp": utc_now_iso(),
            "trigger_type": "atlas_daemon_start",
            "status": "running",
        },
        log_path=args.log_path,
    )
    if args.once:
        print(loop.run_once())
        return
    loop.run_forever()


if __name__ == "__main__":
    main()
