import pytest

from resource_pool import Pool, PoolTimeout, PoolFull


def test_can_reserve_elements_from_a_pool():
    # Given that I have a resource pool
    pool = Pool(lambda: {"test": 42}, pool_size=32)

    # When I try to reserve an element
    with pool.reserve() as d:
        # Then I should get back a resource
        assert d == {"test": 42}

        # And the current pool size should be one less
        assert len(pool) == 31

    # When I exit the reserve block
    # Then the resource should get put back
    assert len(pool) == 32


def test_get_can_timeout():
    # Given that I have a resource pool of one element
    pool = Pool(lambda: {}, pool_size=1)

    # When I take that element out
    pool.get()

    # And try to get another one
    # Then a PoolTimeout should be raised
    with pytest.raises(PoolTimeout):
        pool.get(timeout=0.1)


def test_pools_can_be_full():
    # Given that I have a resource pool of one element
    pool = Pool(lambda: {}, pool_size=1)

    # When I try to put an element back even though it is full
    # Then a PoolFull should be raised
    with pytest.raises(PoolFull):
        pool.put({})
