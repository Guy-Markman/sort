import os
import base64
import argparse


DOWN_LINE = "\n"


def parse_args():
    """Parse program argument."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--FILE-NAME',
        default="input.txt",
        help='The file that will be created, default: %(default)s',
    )
    parser.add_argument(
        '--NUMBER-LINES',
        default=100,
        type=int,
        help='Number of lines in the file, default: %(default)s',
    )
    parser.add_argument(
        '--NUMBER-PER-LINE',
        default=12,
        type=int,
        help='Number of letter in each file, default: %(default)s',
    )
    args = parser.parse_args()
    return args


def main():
    params = parse_args()
    fd = os.open(params.FILE_NAME, os.O_RDWR | os.O_CREAT)
    try:
        for x in range(params.NUMBER_LINES):
            os.write(fd, base64.b64encode(os.urandom(params.NUMBER_PER_LINE))+DOWN_LINE)
    finally:
        os.close(fd)

if __name__ == "__main__":
    main()
