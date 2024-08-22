import unittest
from unittest.mock import patch
from threading import Event
from src.cli import run_cli, input_loop
import asyncio

class TestCLI(unittest.TestCase):

    @patch('builtins.input', side_effect=['GRU-CDG', 'exit'])
    @patch('src.cli.find_and_print_route', return_value=asyncio.Future())
    def test_input_loop(self, mock_find_and_print_route, mock_input):
        routes = {
            'GRU': [('CDG', 40)],
            'CDG': []
        }
        stop_event = Event()
        mock_find_and_print_route.return_value.set_result(None)
        input_loop(routes, stop_event)
        mock_find_and_print_route.assert_called_with(routes, 'GRU', 'CDG')
        self.assertTrue(stop_event.is_set())

    @patch('builtins.input', side_effect=['GRU-CDG', 'exit'])
    @patch('src.cli.input_loop', side_effect=input_loop)
    def test_run_cli(self, mock_input_loop, mock_input):
        file_path = 'test_routes.csv'
        stop_event = Event()

        # Mocking load_routes to return a simple routes dictionary
        with patch('src.cli.load_routes', return_value={'GRU': [('CDG', 40)], 'CDG': []}):
            asyncio.run(run_cli(file_path, stop_event))

        self.assertTrue(mock_input_loop.called)

if __name__ == '__main__':
    unittest.main()
