import unittest
import json
import os
from aiohttp.test_utils import AioHTTPTestCase, TestClient, TestServer
from src.api import create_app

class TestAPIEndpoints(AioHTTPTestCase):

    async def get_application(self):
        self.test_file = 'test_routes.csv'

        # Create a test routes file
        with open(self.test_file, 'w') as f:
            f.write("GRU,BRC,10\n")
            f.write("BRC,SCL,5\n")
            f.write("GRU,CDG,75\n")
            f.write("GRU,SCL,20\n")
            f.write("GRU,ORL,56\n")
            f.write("ORL,CDG,5\n")
            f.write("SCL,ORL,20\n")

        app = create_app(self.test_file)
        return app

    def tearDown(self):
        os.remove(self.test_file)

    async def test_health_check(self):
        server = TestServer(self.app)
        client = TestClient(server)

        await server.start_server()
        response = await client.get('/health')
        assert response.status == 200
        json_response = await response.json()
        assert json_response == {"status": "healthy"}
        await client.close()
        await server.close()

    async def test_best_route_found(self):
        server = TestServer(self.app)
        client = TestClient(server)

        await server.start_server()
        response = await client.get('/best-route?from=GRU&to=CDG')
        assert response.status == 200
        json_response = await response.json()
        assert json_response == {
            "route": "GRU - BRC - SCL - ORL - CDG",
            "price": 40
        }
        await client.close()
        await server.close()

    async def test_best_route_not_found(self):
        server = TestServer(self.app)
        client = TestClient(server)

        await server.start_server()
        response = await client.get('/best-route?from=GRU&to=XYZ')
        assert response.status == 404
        json_response = await response.json()
        assert json_response == {"error": "Route not found"}
        await client.close()
        await server.close()

    async def test_register_route(self):
        server = TestServer(self.app)
        client = TestClient(server)

        await server.start_server()
        new_route = {
            "from": "GRU",
            "to": "EWR",
            "price": 30
        }
        response = await client.post('/register-route', data=json.dumps(new_route), headers={"Content-Type": "application/json"})
        assert response.status == 201
        json_response = await response.json()
        assert json_response == {"message": "Route successfully registered"}

        # Check if the new route is correctly used
        response = await client.get('/best-route?from=GRU&to=EWR')
        assert response.status == 200
        json_response = await response.json()
        assert json_response["route"] == "GRU - EWR"
        assert json_response["price"] == 30
        await client.close()
        await server.close()

    async def test_add_new_routes_and_find_best_route(self):
        server = TestServer(self.app)
        client = TestClient(server)

        await server.start_server()
        new_route = {
            "from": "GRU",
            "to": "EWR",
            "price": 30
        }
        response = await client.post('/register-route', data=json.dumps(new_route), headers={"Content-Type": "application/json"})
        assert response.status == 201
        json_response = await response.json()
        assert json_response == {"message": "Route successfully registered"}

        # Check if the new route is correctly used
        response = await client.get('/best-route?from=GRU&to=EWR')
        assert response.status == 200
        json_response = await response.json()
        assert json_response["route"] == "GRU - EWR"
        assert json_response["price"] == 30

        # Add another route and check the best route with stops
        another_route = {
            "from": "EWR",
            "to": "JFK",
            "price": 10
        }
        response = await client.post('/register-route', data=json.dumps(another_route), headers={"Content-Type": "application/json"})
        assert response.status == 201
        json_response = await response.json()
        assert json_response == {"message": "Route successfully registered"}

        # Check if the new route is correctly used
        response = await client.get('/best-route?from=GRU&to=JFK')
        assert response.status == 200
        json_response = await response.json()
        assert json_response["route"] == "GRU - EWR - JFK"
        assert json_response["price"] == 40
        await client.close()
        await server.close()

if __name__ == '__main__':
    unittest.main()
