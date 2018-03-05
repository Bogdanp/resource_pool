# resource-pool

A generic thread-safe resource pool implementation for Python.

## Installation

    pipenv install resource_pool


## Usage

``` python
from resource_pool import Pool

pool = Pool(factory=lambda: 42, pool_size=30)
with pool.reserve(timeout=10) as n:
    print(n)
```


## License

resource_pool is licensed under Apache 2.0.  Please see
[LICENSE][license] for licensing details.

[license]: https://github.com/Bogdanp/resource_pool/blob/master/LICENSE
