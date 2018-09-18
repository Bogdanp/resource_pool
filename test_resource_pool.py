import pytest
import time

from concurrent.futures import ThreadPoolExecutor, TimeoutError
from resource_pool import LazyPool, Pool, PoolTimeout, PoolFull


@pytest.mark.parametrize("pool_class", [Pool, LazyPool])
def test_can_reserve_elements_from_a_pool(pool_class):
    # Given that I have a resource pool
    pool = pool_class(lambda: {"test": 42}, pool_size=32)

    # When I try to reserve an element
    with pool.reserve() as d:
        pool_size = len(pool)

        # Then I should get back a resource
        assert d == {"test": 42}

    # When I exit the reserve block
    # Then the resource should get put back
    assert len(pool) == pool_size + 1


@pytest.mark.parametrize("pool_class", [Pool, LazyPool])
def test_resources_get_put_back_on_error(pool_class):
    # Given that I have a resource pool
    pool = pool_class(lambda: {"test": 42}, pool_size=32)

    # When I try to reserve an element
    try:
        with pool.reserve():
            pool_size = len(pool)

            # And an unhandled exception occurs within the block
            raise Exception()
    except Exception:
        pass

    # Then my resource should be returned to the pool
    assert len(pool) == pool_size + 1


@pytest.mark.parametrize("pool_class", [Pool, LazyPool])
def test_get_can_timeout(pool_class):
    # Given that I have a resource pool of one element
    pool = pool_class(lambda: {}, pool_size=1)

    # When I take that element out
    pool.get()

    # And try to get another one
    # Then a PoolTimeout should be raised
    with pytest.raises(PoolTimeout):
        pool.get(timeout=0.1)


@pytest.mark.parametrize("pool_class", [Pool, LazyPool])
def test_pools_can_be_full(pool_class):
    # Given that I have a resource pool of one element
    pool = pool_class(lambda: {}, pool_size=1)

    # And I've reserved and released one element so as to make sure the lazy pool instantiates it
    with pool.reserve():
        pass

    # When I try to put an element back even though it is full
    # Then a PoolFull should be raised
    with pytest.raises(PoolFull):
        pool.put({})


def test_can_reserve_elements_from_a_lazy_pool():
    # Given that I have a lazy resource pool with a factory that counts its number of instances
    instances = 0

    def factory():
        nonlocal instances
        instances += 1
        return {"test": 42}

    pool = LazyPool(factory, pool_size=8)

    # When I try to reserve an element
    with pool.reserve() as d:
        # Then I should get back a resource
        assert d == {"test": 42}

        # And the instance count should be 1
        assert instances == 1

        # And the current pool size should be one less
        assert len(pool) == instances - 1

    # When I exit the reserve block
    # Then the resource should get put back
    assert len(pool) == 1

    # When I try to reserve another element
    with pool.reserve() as d:
        # Then I should get back a resource
        assert d == {"test": 42}

        # And the instance count should still be 1
        assert instances == 1

        # And the current pool size should be one less
        assert len(pool) == instances - 1


def test_lazy_pools_can_preload_resources():
    # Given that I have a lazy resource pool with a factory that counts its number of instances
    instances = 0

    def factory():
        nonlocal instances
        instances += 1
        return {"test": 42}

    pool = LazyPool(factory, pool_size=8, min_instances=2)

    # When I try to reserve an element
    with pool.reserve() as d:
        # Then I should get back a resource
        assert d == {"test": 42}

        # And the instance count should be 2
        assert instances == 2

        # And the current pool size should be one less
        assert len(pool) == instances - 1


def test_lazy_pools_can_block():
    # Given that I have a lazy resource pool with a factory that counts its number of instances
    instances = 0

    def factory():
        nonlocal instances
        instances += 1
        return {"test": 42}

    pool = LazyPool(factory, pool_size=4)

    # When I try to reserve 32 resources concurrently
    with ThreadPoolExecutor(max_workers=32) as e:
        reserved = 0

        def background_job():
            nonlocal reserved
            with pool.reserve(timeout=10):
                reserved += 1
                time.sleep(0.1)

        tasks = [e.submit(background_job) for _ in range(32)]
        for task in tasks:
            task.result()

    # Then the number of reserved instances should be 32
    assert reserved == 32

    # And the number of instances should be 4
    assert instances == 4


def test_lazy_pools_can_discard_resources():
    # Given that I have a lazy resource pool with a factory that counts its number of instances
    instances = 0

    def factory():
        nonlocal instances
        instances += 1
        return {"test": 42}

    pool = LazyPool(factory, pool_size=1)

    with ThreadPoolExecutor(max_workers=8) as e:
        # When I try to reserve an element
        # Then I should get back a resource
        d1 = pool.get()

        # And the instance count should be 1
        assert instances == 1

        # When I try to get another resource from the pool
        future = e.submit(lambda: pool.get(timeout=10))

        # Then the future should be blocked indefinitely
        with pytest.raises(TimeoutError):
            future.result(timeout=0.2)

        # When I discard that resource
        pool.discard(d1)

        # Then the future should be unblocked
        d2 = future.result()
        assert d2
        assert d2 == d1
        assert d2 is not d1
