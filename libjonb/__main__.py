import os
import argparse

from .jonb import extract_collision_boxes


def abs_path(value):
    value = os.path.abspath(value)

    if not os.path.exists(value):
        raise argparse.ArgumentError("Invalid file path! Does not exist!")

    return value


def main():
    parser = argparse.ArgumentParser("jonb")
    subparsers = parser.add_subparsers(title="commands")

    extract = subparsers.add_parser("extract")
    extract.add_argument(dest="jonb_path", type=abs_path, help="Collision box jonbin file input path.")

    args, _ = parser.parse_known_args()

    jonb_path = getattr(args, "jonb_path", None)

    if jonb_path is not None:
        extract_collision_boxes(jonb_path)


if __name__ == "__main__":
    main()
