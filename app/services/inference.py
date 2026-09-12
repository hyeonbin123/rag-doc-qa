"""Worker threads for CPU-bound model calls.

Model calls (embeddings, the cross-encoder) are too slow to run on the event loop:
while one runs, every other request the server is handling waits. With six questions
sent at once, a static page request waited up to 0.7 s. They run on a pool of
MODEL_THREADS worker threads instead.

The default of 6 was measured against 1 on the running stack (six concurrent
questions while a static page was requested every 20 ms, four rounds each):
- 1 thread: calls never compete for CPU cores, but queued embeddings waited up to
  2.5 s and one page request still took 242 ms.
- 6 threads: every page request stayed under the 200 ms budget, and each embedding
  took a steady 0.5-0.6 s. Total response times were about the same (mostly
  generation), 10.6 s against 10.0 s on average.
"""

import asyncio
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache, partial
from typing import TypeVar

from app.config import get_settings

T = TypeVar("T")


@lru_cache
def _model_threads() -> ThreadPoolExecutor:
    return ThreadPoolExecutor(
        max_workers=get_settings().model_threads, thread_name_prefix="model"
    )


async def run_model(fn: Callable[..., T], *args) -> T:
    """Run `fn(*args)` on a model thread, queued if all of them are busy."""
    return await asyncio.get_running_loop().run_in_executor(_model_threads(), partial(fn, *args))
