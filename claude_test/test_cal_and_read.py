"""Smoke test for cal + stable-read + watch (empty-pan verification).

Drives PrecisionScaleController through the three new behaviours:
1. calibrate_internal_very_unstable() — ambient set to very unstable
   plus internal calibration. Pan must be empty.
2. read_stable_weight() — one stable read.
3. stream_stable_weights() — yield each new stable value (exact dedup)
   for a bounded observation window so we can confirm an empty pan
   produces ~0 g and no further updates after the first yield.

Usage::

    python claude_test/test_cal_and_read.py [--port /dev/ttyACM0]
        [--watch-seconds 10] [--skip-cal]

The default observation window is short on purpose; for an extended
watch use the `entris_ii.cli.measure watch` CLI which runs until
Ctrl-C.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from entris_ii import PrecisionScaleController  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", default=None)
    parser.add_argument(
        "--watch-seconds",
        type=float,
        default=10.0,
        help="Bounded observation window for the stream check.",
    )
    parser.add_argument(
        "--skip-cal",
        action="store_true",
        help="Skip the calibration step (use when already calibrated).",
    )
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
        stream=sys.stderr,
    )

    port = args.port or PrecisionScaleController.find_port()
    if port is None:
        print("error: no Sartorius device detected", file=sys.stderr)
        return 2

    print(f"port: {port}")
    failures: list[str] = []

    with PrecisionScaleController(port=port) as scale:
        # 1. Calibration. Pan must be empty.
        if not args.skip_cal:
            print("[1/3] calibrate_internal_very_unstable()…")
            post_cal = scale.calibrate_internal_very_unstable()
            print(
                f"      post-cal: value={post_cal.value:+.4f} "
                f"unit={post_cal.unit!r} raw={post_cal.raw!r}"
            )
            if abs(post_cal.value) > 0.01:
                failures.append(
                    f"post-cal value {post_cal.value} is not within "
                    f"+/-0.01 of zero — pan may not be empty"
                )
        else:
            print("[1/3] calibrate step skipped (--skip-cal)")

        # 2. Single stable read.
        print("[2/3] read_stable_weight()…")
        single = scale.read_stable_weight()
        print(
            f"      value={single.value:+.4f} unit={single.unit!r} "
            f"raw={single.raw!r}"
        )
        if abs(single.value) > 0.01:
            failures.append(
                f"single read value {single.value} is not within "
                f"+/-0.01 of zero — pan may not be empty"
            )

        # 3. Stream behaviour on an empty pan. We pull exactly one
        #    yield from stream_stable_weights() to verify the API
        #    (the initial zero), then close the generator and use
        #    direct read_stable_weight() polling for the rest of the
        #    window to confirm the value never changes. This avoids
        #    having to abort a blocking next() call when the empty
        #    pan never produces a second yield.
        print(
            f"[3/3] stream first-yield + steady-value check for "
            f"{args.watch_seconds:.1f}s…"
        )
        start = time.monotonic()
        stream = scale.stream_stable_weights(timeout=5.0, interval=0.2)
        try:
            first = next(stream)
        finally:
            stream.close()
        elapsed = time.monotonic() - start
        print(
            f"      stream first yield @ +{elapsed:5.2f}s: "
            f"value={first.value:+.4f} unit={first.unit!r} "
            f"raw={first.raw!r}"
        )
        if abs(first.value) > 0.01:
            failures.append(
                f"stream first yield {first.value} is not within "
                f"+/-0.01 of zero — pan may not be empty"
            )

        unique_values: set[float] = {first.value}
        sample_count = 1
        deadline = start + args.watch_seconds
        while time.monotonic() < deadline:
            time.sleep(0.5)
            reading = scale.read_stable_weight(timeout=2.0)
            sample_count += 1
            if reading.value not in unique_values:
                unique_values.add(reading.value)
                elapsed = time.monotonic() - start
                print(
                    f"      change @ +{elapsed:5.2f}s: "
                    f"value={reading.value:+.4f} {reading.unit}"
                )
        print(
            f"      sampled {sample_count} stable reads, "
            f"unique values: {sorted(unique_values)}"
        )
        if len(unique_values) > 1:
            failures.append(
                f"steady-value check saw {len(unique_values)} distinct "
                f"values on an empty pan; expected exactly 1"
            )

    print()
    if failures:
        print("VERIFICATION FAILED:")
        for line in failures:
            print(f"  - {line}")
        return 1
    print("VERIFICATION PASSED — empty pan, single zero, no further updates.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
