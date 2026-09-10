import time
from contextlib import contextmanager


class Stopwatch:
    def __init__(self) -> None:
        self.elapsed_ms: int = 0

    @contextmanager
    def measure(self):
        start = time.perf_counter()
        try:
            yield self
        finally:
            self.elapsed_ms = int((time.perf_counter() - start) * 1000)
