import typing

from contextlib import contextmanager
from queue import Queue, Empty, Full
from typing import Generic, Optional

__all__ = ["PoolError", "PoolTimeout", "PoolFull", "Pool", "__version__"]
__version__ = "0.1.0"

ResourceT = typing.TypeVar("ResourceT")
ResourceFactory = typing.Callable[[], ResourceT]


class PoolError(Exception):
    """Base class for Pool errors.
    """


class PoolTimeout(PoolError):
    """Raised when getting a resource times out.
    """


class PoolFull(PoolError):
    """Raised when putting a resource when the pool is full.
    """


class Pool(Generic[ResourceT]):
    """A generic resource pool.

    Parameters:
      factory: The factory function that is used to create resources.
      pool_size: The max number of resources in the pool at any time.
    """

    def __init__(self, factory: ResourceFactory, *, pool_size: int) -> None:
        self._pool = Queue(pool_size)
        self._pool_size = pool_size

        for _ in range(pool_size):
            self.put(factory())

    @contextmanager
    def reserve(self, timeout: Optional[float] = None):
        """
        """
        resource = self.get(timeout=timeout)
        yield resource
        self.put(resource)

    def get(self, *, timeout: Optional[float] = None):
        """Get a resource from the pool.

        It's the getter's responsibility to put the resource back once
        they're done using it.

        Raises:
          Timeout: If a timeout is given and it expires.

        Parameters:
          timeout: An optional timeout representing how long to wait
            for the resource.
        """
        try:
            return self._pool.get(timeout=timeout)
        except Empty:
            raise PoolTimeout()

    def put(self, resource: ResourceT) -> None:
        """Put a resource back.

        Raises:
          PoolFull: If the resource pool is full.
        """
        try:
            return self._pool.put_nowait(resource)
        except Full:
            raise PoolFull()

    def __len__(self) -> int:
        """Get the number of resources currently in the pool.
        """
        return self._pool.qsize()
