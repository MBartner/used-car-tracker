import logging
from .server import start_server

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    start_server(site_dir="./static", data_dir="./.local")