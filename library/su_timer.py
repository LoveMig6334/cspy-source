from __future__ import annotations

import functools
import time
from typing import Callable, Optional

_DIVISORS = {
    "ps": 0.001,
    "ns": 1,
    "us": 1_000,
    "µs": 1_000,
    "ms": 1_000_000,
    "s": 1_000_000_000,
}

_AUTO_SCALE = (
    (1, "ps", 0.001),
    (1_000, "ns", 1),
    (1_000_000, "µs", 1_000),
    (1_000_000_000, "ms", 1_000_000),
    (float("inf"), "s", 1_000_000_000),
)


def format_duration(
    elapsed_ns: float, precision: int = 3, unit: Optional[str] = None
) -> str:
    if unit is not None:
        key = unit.lower() if unit.lower() in _DIVISORS else unit
        if key not in _DIVISORS:
            raise ValueError(f"Unknown unit {unit!r}. Use one of: ns, us, ms, s.")
        label = "µs" if key in ("us", "µs") else key
        return f"{elapsed_ns / _DIVISORS[key]:.{precision}f} {label}"

    if elapsed_ns <= 0:
        return "<1 ns"

    for upper_bound, label, divisor in _AUTO_SCALE:
        if elapsed_ns < upper_bound:
            return f"{elapsed_ns / divisor:.{precision}f} {label}"
    # Fallback (unreachable because the last bound is +inf).
    return f"{elapsed_ns / 1_000_000_000:.{precision}f} s"


def su_timer(
    _func: Optional[Callable] = None,
    *,
    unit: Optional[str] = None,
    precision: int = 3,
    runs: int = 1,
    name: Optional[str] = None,
    logger: Optional[Callable[[str], None]] = None,
):
    emit = logger or print

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            label = name or func.__name__
            n = max(1, runs)
            total_ns = 0
            best_ns: Optional[int] = None
            result = None

            for _ in range(n):
                start = time.perf_counter_ns()
                result = func(*args, **kwargs)
                elapsed = time.perf_counter_ns() - start
                total_ns += elapsed
                if best_ns is None or elapsed < best_ns:
                    best_ns = elapsed

            if n == 1:
                emit(
                    f"[su_timer] {label}() took "
                    f"{format_duration(total_ns, precision, unit)}"
                )
            else:
                avg_ns = total_ns / n
                emit(
                    f"[su_timer] {label}() x{n}  ->  "
                    f"avg {format_duration(avg_ns, precision, unit)}, "
                    f"best {format_duration(best_ns, precision, unit)}, "
                    f"total {format_duration(total_ns, precision, unit)}"
                )
            return result

        return wrapper

    # @su_timer  (no parentheses)  ->  _func is the function itself.
    if _func is not None and callable(_func):
        return decorator(_func)
    # @su_timer(...)  ->  return the real decorator.
    return decorator


if __name__ == "__main__":
    import math

    # 1) Bare usage - unit auto-scales to whatever fits.
    @su_timer
    def fast_loop():
        return sum(i * i for i in range(1_000))

    # 2) A slower function lands in ms automatically.
    @su_timer
    def slow_loop():
        return sum(math.sqrt(i) for i in range(2_000_000))

    # 3) Force a unit and precision.
    @su_timer(unit="ms", precision=4)
    def forced_ms():
        time.sleep(0.05)

    # 4) Micro-benchmark: run 1000 times, report avg / best.
    @su_timer(runs=1000, name="tiny_op")
    def tiny():
        return 2**16

    fast_loop()
    slow_loop()
    forced_ms()
    tiny()
