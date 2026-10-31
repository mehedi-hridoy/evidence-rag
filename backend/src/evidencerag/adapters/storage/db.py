from psycopg import AsyncConnection
from psycopg.rows import TupleRow
from psycopg_pool import AsyncConnectionPool

Pool = AsyncConnectionPool[AsyncConnection[TupleRow]]


def create_pool(url: str) -> Pool:
    return AsyncConnectionPool(conninfo=url, min_size=1, max_size=10, open=False)


async def ping(pool: Pool, timeout_s: float) -> None:
    async with pool.connection(timeout=timeout_s) as conn:
        await conn.execute("SELECT 1")
