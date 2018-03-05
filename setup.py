import os

from setuptools import setup


def rel(*xs):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), *xs)


with open(rel("resource_pool.py"), "r") as f:
    version_marker = "__version__ = "
    for line in f:
        if line.startswith(version_marker):
            _, version = line.split(version_marker)
            version = version.strip().strip('"')
            break
    else:
        raise RuntimeError("Version marker not found.")


setup(
    name="resource_pool",
    version=version,
    description="A generic resource pool implementation.",
    long_description="Visit https://github.com/Bogdanp/resource_pool for more information.",
    packages=[],
    py_modules=["resource_pool"],
    install_requires=[],
    python_requires=">=3.5",
    include_package_data=True,
)
