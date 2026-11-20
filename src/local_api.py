"""Local HTTP API Server simulating Amazon API Gateway.

Routes POST /predict to the simulated Lambda function and returns predictions.
Strictly local: binds to 127.0.0.1.
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from src.simulation_config import SIMULATED_CONFIG
from src.local_aws_simulator import LocalAWSSimulator

_simulator_instance = None


def get_simulator():
    global _simulator_instance
    if _simulator_instance is None:
        _simulator_instance = LocalAWSSimulator()
        _simulator_instance.init_simulated_endpoint()
    return _simulator_instance


class SimulatedAPIGatewayHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler simulating Amazon API Gateway proxy integration."""

    def do_POST(self):
        if self.path != "/predict":
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "error",
                "message": f"Route {self.path} not found. Use POST /predict."
            }).encode("utf-8"))
            return

        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else ""

        # Format simulated API Gateway proxy event
        event = {
            "resource": "/predict",
            "path": "/predict",
            "httpMethod": "POST",
            "headers": dict(self.headers),
            "body": raw_body,
            "isBase64Encoded": False
        }

        simulator = get_simulator()
        lambda_response = simulator.invoke_simulated_lambda(event)

        status_code = lambda_response.get("statusCode", 500)
        headers = lambda_response.get("headers", {"Content-Type": "application/json"})
        body = lambda_response.get("body", "{}")

        self.send_response(status_code)
        for k, v in headers.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "healthy",
                "service": "Simulated Amazon API Gateway",
                "endpoint": SIMULATED_CONFIG.simulated_sagemaker_endpoint_name
            }).encode("utf-8"))
            return

        self.send_response(405)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({
            "status": "error",
            "message": "Method not allowed. Use POST /predict."
        }).encode("utf-8"))

    def log_message(self, format, *args):
        # Suppress noisy standard server logging
        pass


def run_local_api(host: str = SIMULATED_CONFIG.local_api_host, port: int = SIMULATED_CONFIG.local_api_port):
    """Start local simulated API Gateway HTTP server."""
    get_simulator()
    server_address = (host, port)
    httpd = HTTPServer(server_address, SimulatedAPIGatewayHandler)
    print(f"==================================================")
    print(f" SIMULATED API GATEWAY STARTED LOCALLY")
    print(f" Listening at: http://{host}:{port}/predict")
    print(f" Health check: http://{host}:{port}/health")
    print(f" Press Ctrl+C to terminate.")
    print(f"==================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down simulated API Gateway server.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    run_local_api()
