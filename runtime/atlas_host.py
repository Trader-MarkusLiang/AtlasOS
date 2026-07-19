"""macOS-friendly lightweight runtime host for Atlas OS.

DEPRECATED (Runtime v1.6, 2026-07-19): the single supported daemon entry is
`runtime.atlas_runtime_daemon`. This module remains only so historical
validation scripts keep importing; new work must not use it.

Start with:

    python3 -m runtime.atlas_host --interval 60

The host runs scheduled runtime cycles without executing trades, modifying
portfolio files, or bypassing CDE.
"""

from __future__ import annotations

import argparse
import signal
import time
from dataclasses import dataclass, field
from typing import Dict, Optional

try:
    from runtime.logging import utc_now_iso
    from runtime.scheduler import daily_run, event_trigger, intraday_run
except ModuleNotFoundError:  # pragma: no cover
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from runtime.logging import utc_now_iso
    from runtime.scheduler import daily_run, event_trigger, intraday_run


@dataclass
class HostConfig:
    sleep_interval_seconds: int = 60
    daily_interval_seconds: int = 24 * 60 * 60
    intraday_interval_seconds: int = 60 * 60
    log_path: Optional[str] = None
    db_path: Optional[str] = None
    llm_model: str = "gpt-5.5"


@dataclass
class AtlasHost:
    config: HostConfig = field(default_factory=HostConfig)
    _running: bool = False
    _last_daily: float = 0
    _last_intraday: float = 0

    def run_once(self) -> Dict[str, object]:
        """Run due scheduled jobs once and return a compact status."""

        now = time.time()
        executed = []
        if now - self._last_daily >= self.config.daily_interval_seconds:
            executed.append(
                daily_run(
                    log_path=self.config.log_path,
                    db_path=self.config.db_path,
                    llm_model=self.config.llm_model,
                )
            )
            self._last_daily = now
        if now - self._last_intraday >= self.config.intraday_interval_seconds:
            executed.append(
                intraday_run(
                    log_path=self.config.log_path,
                    db_path=self.config.db_path,
                    llm_model=self.config.llm_model,
                )
            )
            self._last_intraday = now
        return {
            "timestamp": utc_now_iso(),
            "executed_count": len(executed),
            "executed": executed,
        }

    def trigger_event(self, event_type: str) -> Dict[str, object]:
        """Trigger a supported event route."""

        return event_trigger(
            event_type,
            log_path=self.config.log_path,
            db_path=self.config.db_path,
            llm_model=self.config.llm_model,
        )

    def run_forever(self, max_cycles: Optional[int] = None) -> None:
        """Run daemon-style until interrupted or max_cycles is reached."""

        self._running = True
        cycles = 0
        while self._running:
            self.run_once()
            cycles += 1
            if max_cycles is not None and cycles >= max_cycles:
                break
            time.sleep(self.config.sleep_interval_seconds)

    def stop(self, *_args: object) -> None:
        self._running = False


def main() -> None:
    parser = argparse.ArgumentParser(description="Atlas OS lightweight runtime host")
    parser.add_argument("--interval", type=int, default=60, help="host loop sleep interval")
    parser.add_argument("--daily-interval", type=int, default=24 * 60 * 60)
    parser.add_argument("--intraday-interval", type=int, default=60 * 60)
    parser.add_argument("--log-path", default=None)
    parser.add_argument("--db-path", default=None)
    parser.add_argument("--llm-model", default="gpt-5.5")
    parser.add_argument("--once", action="store_true", help="run one host cycle and exit")
    args = parser.parse_args()

    host = AtlasHost(
        HostConfig(
            sleep_interval_seconds=args.interval,
            daily_interval_seconds=args.daily_interval,
            intraday_interval_seconds=args.intraday_interval,
            log_path=args.log_path,
            db_path=args.db_path,
            llm_model=args.llm_model,
        )
    )
    signal.signal(signal.SIGINT, host.stop)
    signal.signal(signal.SIGTERM, host.stop)
    if args.once:
        print(host.run_once())
        return
    host.run_forever()


if __name__ == "__main__":
    main()
