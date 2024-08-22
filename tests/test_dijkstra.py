import unittest
import asyncio
from src.core.dijkstra import find_best_route

class TestDijkstraAlgorithm(unittest.TestCase):

    def setUp(self):
        self.routes = {
            'GRU': [('BRC', 10), ('CDG', 75), ('SCL', 20), ('ORL', 56)],
            'BRC': [('SCL', 5)],
            'SCL': [('ORL', 20)],
            'ORL': [('CDG', 5)],
            'CDG': [],
            'XYZ': [('ABC', 15)],  # Disconnected node
            'ABC': [('XYZ', 15)],  # Disconnected node
        }

    def test_direct_route(self):
        best_route, best_cost = asyncio.run(find_best_route(self.routes, 'GRU', 'CDG'))
        self.assertEqual(best_cost, 40)  # The lowest cost should be 40
        self.assertEqual(best_route[-1], 'CDG')  # Ensure it ends at the correct destination

    def test_route_with_scales(self):
        best_route, best_cost = asyncio.run(find_best_route(self.routes, 'GRU', 'CDG'))
        self.assertEqual(best_cost, 40)
        self.assertEqual(best_route, ['GRU', 'BRC', 'SCL', 'ORL', 'CDG'])

    def test_no_route_possible(self):
        best_route, best_cost = asyncio.run(find_best_route(self.routes, 'GRU', 'XYZ'))
        self.assertIsNone(best_route)
        self.assertEqual(best_cost, float('inf'))

    def test_increasing_cost(self):
        new_routes = self.routes.copy()
        new_routes['GRU'].append(('EWR', 100))  # More expensive direct route
        new_routes['ORL'].append(('EWR', 50))  # Cheaper route with stops
        best_route, best_cost = asyncio.run(find_best_route(new_routes, 'GRU', 'EWR'))
        self.assertEqual(best_cost, 85)  # Expected cost is now 85
        self.assertEqual(best_route, ['GRU', 'BRC', 'SCL', 'ORL', 'EWR'])  # The full route found

    def test_disconnected_graph(self):
        best_route, best_cost = asyncio.run(find_best_route(self.routes, 'XYZ', 'ABC'))
        self.assertEqual(best_route, ['XYZ', 'ABC'])
        self.assertEqual(best_cost, 15)

if __name__ == '__main__':
    unittest.main()
