from aiohttp import web
from typing import Dict, Any
from src.core.routes import load_routes, append_route_to_file
from src.core.dijkstra import find_best_route


def create_app(file_path: str) -> web.Application:
    routes = load_routes(file_path)
    app = web.Application()

    async def best_route(request: web.Request) -> web.Response:
        start = request.query.get('from', '').strip().upper()
        end = request.query.get('to', '').strip().upper()

        if not start or not end:
            return web.json_response({"error": "Parameters 'from' and 'to' are required"}, status=400)

        best_route, best_cost = await find_best_route(routes, start, end)
        if best_route and best_route[-1] == end:  # Confirm that the route ends at the correct destination
            return web.json_response({"route": " - ".join(best_route), "price": best_cost})
        else:
            return web.json_response({"error": "Route not found"}, status=404)

    async def register_route(request: web.Request) -> web.Response:
        data: Dict[str, Any] = await request.json()

        if not all(key in data for key in ('from', 'to', 'price')):
            return web.json_response({"error": "Fields 'from', 'to', and 'price' are required"}, status=400)

        from_city = data['from'].strip().upper()
        to_city = data['to'].strip().upper()
        price = int(data['price'])

        if from_city in routes:
            for destination, existing_price in routes[from_city]:
                if destination == to_city:
                    return web.json_response(
                        {"error": f"Route from {from_city} to {to_city} already exists with price {existing_price}"},
                        status=409
                    )

        new_route = [from_city, to_city, str(price)]
        append_route_to_file(file_path, new_route)
        routes.update(load_routes(file_path))

        return web.json_response({"message": "Route successfully registered"}, status=201)

    async def health_check(request: web.Request) -> web.Response:
        return web.json_response({"status": "healthy"})

    app.router.add_get('/best-route', best_route)
    app.router.add_post('/register-route', register_route)
    app.router.add_get('/health', health_check)

    return app
