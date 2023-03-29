import asyncio
import inspect

async def poll(fn=lambda: True, time_interval: int = 1000, timeout: int = 10000) -> None:
    async def poll_coroutine() -> None:
        while True:
            res = fn()
            result = None
            if inspect.iscoroutine(res):
                result = await res
            else:
                result = res

            if result is True:
                break
            await asyncio.sleep(time_interval / 1000)

    try:
        await asyncio.wait_for(poll_coroutine(), timeout / 1000)
    except asyncio.TimeoutError as e:
        raise TimeoutError("Polling timed out") from e