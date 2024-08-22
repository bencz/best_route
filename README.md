
# Best Route Finder

Welcome to the Best Route Finder project! This is a simple application designed to help you find the cheapest route between airports, even if it means taking multiple flights. You can interact with the app either through a command-line interface (CLI) or via HTTP endpoints.

## Getting Started

### Prerequisites

- **Python 3.12+**
- **Docker** (optional, if you prefer running the app in a container)

### Setting Up Locally

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/bencz/best_route
   cd best_route
   ```

2. **Create and Activate a Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use `.venv\Scripts\Activate`
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:
   ```bash
   python app.py [<route_file.csv>] [--cli] [--web]
   ```

   **Argumentos**
   
   - `<route_file.csv>`: Path to the routes file in CSV format. This file is required to configure the application's routes. If no file is provided, default `routes.csv` file will be used.
   - `--cli` (optional): Enables the command-line interface (CLI) execution.
   - `--web` (optional): Enables the web server execution. If not specified, the web server will be enabled by default if no other option is provided, and it will start on port 5000.


### Using the CLI

Once you start the app, the CLI is ready to go. You can enter routes in the format `FROM-TO`, and it will return the best route and cost.

```bash
$ python app.py routes.csv --cli
Please enter the route (format FROM-TO): GRU-CDG
Best route: GRU - BRC - SCL - ORL - CDG > $40
```

### Using the HTTP API

You can also interact with the app via HTTP endpoints. Here’s how:

1. **Starting the project**:
   ```bash
   $ python app.py routes.csv --web
   ```

2. **Health Check**:
   ```bash
   GET /health
   ```
   This will return a simple JSON indicating the app is running.

3. **Find the Best Route**:
   ```bash
   GET /best-route?from=GRU&to=CDG
   ```
   This returns the best route between the two airports.

4. **Register a New Route**:
   ```bash
   POST /register-route
   Content-Type: application/json
   {
       "from": "GRU",
       "to": "EWR",
       "price": 30
   }
   ```
   This allows you to add a new route to the system.

### Running the App with Docker

If you prefer using Docker, here’s how to get everything set up:

1. **Build the Docker Image**:
   ```bash
   docker build -t best-route-app .
   ```

2. **Run the Docker Container**:
   ```bash
   docker run -p 5000:5000 best-route-app
   ```

   The app will be available on `http://localhost:5000`.


3. **Run with custom csv file**
   ```bash
   docker run -v ./custom_routes.csv:/app/custom_routes.csv -p 5000:5000 best-route-app custom_routes.csv --web
   ```

### Running Tests

To make sure everything is working as expected, you can run the tests:

   ```bash
   python -m unittest discover tests
   ```
