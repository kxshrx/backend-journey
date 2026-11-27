import asyncio
import time


async def fetch(name: str, seconds: float) -> str:
    await asyncio.sleep(seconds)           # pretend: waiting for a database
    return f"{name} done"


async def sequential() -> list[str]:
    return [await fetch("a", 1), await fetch("b", 1), await fetch("c", 1)]


async def concurrent() -> list[str]:
    return await asyncio.gather(fetch("a", 1), fetch("b", 1), fetch("c", 1))


for fn in (sequential, concurrent):
    start = time.perf_counter()
    result = asyncio.run(fn())
    print(fn.__name__, result, f"{time.perf_counter() - start:.1f}s")
