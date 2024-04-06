import time


class Timer:
    start: float

    def __enter__(self):
        self.start = time.perf_counter()

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"Time: {time.perf_counter() - self.start}s")
