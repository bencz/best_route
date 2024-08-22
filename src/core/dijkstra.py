import heapq
from typing import Dict, List, Tuple, Any


async def find_best_route(routes: Dict[str, List[Tuple[str, int]]],
                          start: str,
                          end: str) -> tuple[Any, Any] | tuple[None, float]:
    queue = [(0, start, [])]
    visited = set()

    while queue:
        (cost, node, path) = heapq.heappop(queue)

        if node in visited:
            continue

        path = path + [node]
        visited.add(node)

        if node == end:
            return path, cost

        for next_node, travel_cost in routes.get(node, []):
            if next_node not in visited:
                heapq.heappush(queue, (cost + travel_cost, next_node, path))

    return None, float('inf')
