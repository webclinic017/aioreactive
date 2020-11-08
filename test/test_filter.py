import asyncio
from typing import Any, Generator

import pytest
from aioreactive import AsyncAwaitableObserver, asyncrx, run
from aioreactive.testing import VirtualTimeEventLoop
from expression.core import pipe


class MyException(Exception):
    pass


@pytest.yield_fixture()  # type:ignore
def event_loop() -> Generator[Any, Any, Any]:
    loop = VirtualTimeEventLoop()
    yield loop
    loop.close()


@pytest.mark.asyncio
async def test_filter_happy() -> None:
    xs = asyncrx.from_iterable([1, 2, 3])
    result = []

    async def asend(value: int) -> None:
        result.append(value)

    async def predicate(value: int) -> bool:
        print("sleeping")
        await asyncio.sleep(0.1)
        return value > 1

    ys = pipe(xs, asyncrx.filter_async(predicate))
    value = await run(ys, AsyncAwaitableObserver(asend))
    assert value == 3
    assert result == [2, 3]


@pytest.mark.asyncio
async def test_filter_predicate_throws() -> None:
    xs = asyncrx.from_iterable([1, 2, 3])
    err = MyException("err")
    result = []

    async def asend(value: int) -> None:
        result.append(value)

    async def predicate(value: int) -> bool:
        await asyncio.sleep(0.1)
        raise err

    ys = pipe(xs, asyncrx.filter_async(predicate))

    with pytest.raises(MyException):
        await run(ys, AsyncAwaitableObserver(asend))

    assert result == []
