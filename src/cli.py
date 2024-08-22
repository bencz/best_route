import asyncio
from difflib import get_close_matches
from src.core.routes import load_routes
from src.core.dijkstra import find_best_route
from threading import Thread, Event

def input_loop(routes, stop_event):
    print("Type \'exit\' to end your CLI session")
    while not stop_event.is_set():
        try:
            route_input = input("Please enter the route (format FROM-TO): ").strip().upper()
            if stop_event.is_set():
                break
            if route_input.lower() == 'exit':
                stop_event.set()
                break

            try:
                start, end = route_input.split('-')
            except ValueError:
                print("Invalid route format. Use the format FROM-TO.")
                continue

            if start not in routes:
                print(f"Origin '{start}' not found.")
                suggestions = get_close_matches(start, routes.keys())
                if suggestions:
                    print(f"Did you mean: {', '.join(suggestions)}?")
                continue

            if end not in routes:
                print(f"Destination '{end}' not found.")
                suggestions = get_close_matches(end, routes.keys())
                if suggestions:
                    print(f"Did you mean: {', '.join(suggestions)}?")
                continue

            asyncio.run(find_and_print_route(routes, start, end))
        except KeyboardInterrupt:
            print("Received exit signal, shutting down...")
            stop_event.set()
            break

async def find_and_print_route(routes, start, end):
    best_route, best_cost = await find_best_route(routes, start, end)
    if best_route:
        print(f"Best route: {' - '.join(best_route)} > ${best_cost}")
    else:
        print("Route not found.")

async def run_cli(file_path: str, stop_event: Event) -> None:
    routes = load_routes(file_path)

    input_thread = Thread(target=input_loop, args=(routes, stop_event))
    input_thread.start()

    try:
        while not stop_event.is_set():
            await asyncio.sleep(0.01)
    except asyncio.CancelledError:
        pass
    finally:
        stop_event.set()
        input_thread.join()
        print("CLI shutting down...")
