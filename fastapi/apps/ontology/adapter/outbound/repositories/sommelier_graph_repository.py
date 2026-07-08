from __future__ import annotations

from neo4j import AsyncGraphDatabase

from ontology.app.ports.output.sommelier_graph_port import SommelierPort


class SommelierRepository(SommelierPort):
    def __init__(self, uri: str, user: str, password: str) -> None:
        self._driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    async def run_cypher(self, cypher: str, params: dict) -> list[dict]:
        async with self._driver.session() as session:
            result = await session.run(cypher, params)
            return await result.data()

    async def close(self) -> None:
        await self._driver.close()
