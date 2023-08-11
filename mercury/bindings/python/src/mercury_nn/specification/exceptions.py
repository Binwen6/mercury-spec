from dataclasses import dataclass


@dataclass
class BenchmarkUnsupportedImplementationException(Exception):
    """An exception raised when requesting to run a benchmark on an implementation which the benchmark does not support.
    """

    implementation: str


@dataclass
class ModelUnsupportedImplementationException(Exception):
    """An exception raised when requesting to run a benchmark on an implementation which the model extension does not provide.
    """

    implementation: str


@dataclass
class UnknownBenchmarkException(Exception):
    """An exception raised when requesting to run an unknown benchmark.
    """

    benchmark: str