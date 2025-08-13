import asyncio
import functools


# https://github.com/pallets/click/issues/2033
def make_sync(func):
    """A decorator to run an async function as a sync function."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper
