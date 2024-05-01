from pathlib import Path

from used_car_tracker.tracker import get_results

if __name__ == "__main__":
    get_results(Path(".local"))
