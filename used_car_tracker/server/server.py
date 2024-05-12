import json
import logging
import os
from datetime import datetime
from http import HTTPStatus
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socket import socket
from socketserver import BaseServer
from typing import Any, Dict, List, Optional, Tuple, Type, Union

logger = logging.getLogger(__name__)

ID_KEY = "id"


def get_cars(dir: str) -> Dict[str, List[Dict[str, Any]]]:

    cars: Dict[str, List[Dict[str, Any]]] = {}

    # iterate over directories
    for file_path in os.listdir(dir):
        full_path = dir + "/" + file_path
        file_stat = os.stat(full_path)
        created_at = file_stat.st_ctime
        created = datetime.fromtimestamp(created_at)
        formatted_created = created.strftime("%B-%d")
        with open(full_path, "r", encoding="utf-8") as f:
            car = json.load(f)
        if ID_KEY not in car:
            continue
        id = car[ID_KEY]
        if id not in cars:
            new_car_list: List[Dict[str, Any]] = []
            cars[id] = new_car_list
        cars[id].append({"date": formatted_created, "car": car, "date_int": created_at})
    
    for k,v in cars.items():
        cars[k] = sorted(v, key=lambda x: x["date_int"])
        
    return cars


def requestHandlerFactory(site_dir: str, data_dir: str) -> Type[SimpleHTTPRequestHandler]:
    class DirectoryHTTPRequestHandler(SimpleHTTPRequestHandler):
        def __init__(
            self,
            request: Union[socket, Tuple[bytes, socket]],
            client_address: Any,
            server: BaseServer,
            *,
            directory: Optional[str] = None,
        ) -> None:
            super().__init__(request, client_address, server, directory=site_dir)

        def do_GET(self) -> None:
            if self.path == "/api/data":
                cars = get_cars(data_dir)
                cars_serialized = json.dumps(cars)
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-type", "application/json")
                self.send_header("Content-Length", str(len(cars_serialized)))
                self.end_headers()
                self.wfile.write(bytes(cars_serialized, "utf-8"))
                return

            return super().do_GET()

    return DirectoryHTTPRequestHandler


def start_server(site_dir: str, data_dir: str):
    server_address = ("", 8000)

    httpd = HTTPServer(server_address, requestHandlerFactory(site_dir, data_dir))
    logger.info(f"Starting server {server_address}")
    httpd.serve_forever()


# HTTP Server
# paths that resolve to handlers that:
# 1. handle getting files from a directory
# 2. handle getting data from an endpoint
