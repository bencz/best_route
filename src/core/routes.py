from typing import Dict, List, Tuple
from collections import defaultdict
import csv
import threading

file_lock = threading.Lock()

def load_routes(file_path: str) -> Dict[str, List[Tuple[str, int]]]:
    routes = defaultdict(list)
    with file_lock:
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                origin, destination, cost = row
                origin = origin.strip().upper()
                destination = destination.strip().upper()
                cost = int(cost)
                routes[origin].append((destination, cost))
                routes[destination].append((origin, cost))  # rotas bidirecionais

    return routes


def append_route_to_file(file_path: str, route: List[str]) -> None:
    with file_lock:
        with open(file_path, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(route)
