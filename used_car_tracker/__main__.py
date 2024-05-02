import argparse
from pathlib import Path

from used_car_tracker.tracker import track_cars


def parseArgs() -> argparse.Namespace:
   parser = argparse.ArgumentParser()
   parser.add_argument("log_dir", type=str, help="Path to the file")
   args = parser.parse_args()
   return args

def main():
   args = parseArgs()
   track_cars(Path(args.log_dir))

if __name__ == "__main__":
   main()
