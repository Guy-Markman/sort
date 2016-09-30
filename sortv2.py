import os
import math
import argparse
import time

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
    parser.add_argument(
        '--LINES-PER-FILE',
        default=10,
        type=int,
        help='Number of lines in each temporary file, default: %(default)s',
    )
    parser.add_argument(
        '--FILE-OUTPUT-NAME',
        default="output.txt",
        help='The file output file, default: %(default)s',
    )
    args = parser.parse_args()
    return args


def bubbleSort(alist):
    for passnum in range(len(alist)-1, 0, -1):
        for i in range(passnum):
            if alist[i] > alist[i+1]:
                temp = alist[i]
                alist[i] = alist[i+1]
                alist[i+1] = temp
    return alist


def sort_records():
    params = parse_args()
    fd = os.open(params.FILE_NAME, os.O_RDWR)
    length = int(math.ceil(params.NUMBER_PER_LINE/3.0)*4+2)
    size = length*params.LINES_PER_FILE
    try:
        for x in range(
                    int(math.ceil(float
                        (params.NUMBER_LINES)/params.LINES_PER_FILE)
                        )
                    ):
            txt = "\n".join(
                bubbleSort(os.read(fd, size)[:-1].split(DOWN_LINE))
                )+"\n"
            os.lseek(fd, x*size, 0)
            os.write(fd, txt)
    finally:
        os.close(fd)


def sort_and_print(input, output, lines):
    params = parse_args()
    length = int(math.ceil(params.NUMBER_PER_LINE/3.0)*4+2)
    for z in range(params.NUMBER_LINES):        
        smallestLine = bubbleSort([x["line"] for x in lines])[0]
        n = [x["line"] for x in lines].index(smallestLine)
        os.write(output, smallestLine)
        os.lseek(input, lines[n]["cursor"], 0)
        newline = os.read(input, length)
        # If we finished reading the record
        if lines[n]["number_line"] == params.LINES_PER_FILE-1 or newline == "":
            del lines[n]
        # Switch to the next line
        else:
            lines[n]["number_line"] += 1
            lines[n]["cursor"] += length
            lines[n]["line"] = newline

def change_to_dictionaries(fd):
    params = parse_args()
    ans = []
    length = int(math.ceil(params.NUMBER_PER_LINE/3.0)*4+2)
    for x in range(
            int(math.ceil(float(params.NUMBER_LINES) / params.LINES_PER_FILE))
            ):
        ans.append(
            {
                "number_line": 0,
                "cursor": x*length*params.LINES_PER_FILE+length,
                "line": os.read(fd, length)
            }
        )
        os.lseek(fd, (params.LINES_PER_FILE-1)*length, os.SEEK_CUR)
    os.lseek(fd, 0, 0)
    return ans

    
def get_length():
    params = parse_args()
    return int(math.ceil(params.NUMBER_PER_LINE/3.0)*4+2)


def check(output):
    params = parse_args()
    os.lseek(output, 0, 0)
    ans = True
    length = get_length()
    first_line = os.read(output, length)
    for x in range(params.NUMBER_LINES-1):
        second_line = os.read(output, length)
        if second_line < first_line:
            print "%s%s" % (second_line, first_line)
            ans = False
        first_line = second_line
    return ans

def main():
    params = parse_args()
    file_input = os.open(params.FILE_NAME, os.O_RDWR)
    output = os.open(params.FILE_OUTPUT_NAME, os.O_RDWR | os.O_CREAT)
    try:
        start_time=time.time()
        sort_records()
        lines = change_to_dictionaries(file_input)
        sort_and_print(file_input, output, lines)
        print check(output)
        print time.time() - start_time

    finally:
        os.close(file_input)
        os.close(output)

if __name__ == "__main__":
    main()
