import time


class _Elapsed:
    def __init__(self):
        self.t = 0.0

    def __float__(self):
        return self.t

    def __coerce__(self, other):
        if isinstance(other, (float, int)):
            return float(self.t), float(other)
        return None

    def __str__(self):
        return f"{self.t:.2f} s"


class timing:
    """
    Use as follows:
    with timing() as t:
        do something
    print(f"Operation took {t}")
    total += t
    """

    def __enter__(self):
        self._ret = _Elapsed()
        self.start = time.time()
        return self._ret

    def __exit__(self, exc_type, exc_value, traceback):
        self._ret.t = time.time() - self.start
