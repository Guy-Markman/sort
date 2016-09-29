import os
import math
import argparse
import multiprocessing
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


def get_length():
    params = parse_args()
    return int(math.ceil(params.NUMBER_PER_LINE/3.0)*4+2)


def bubblesort(alist):
    for passnum in range(len(alist)-1, 0, -1):
        for i in range(passnum):
            if alist[i] > alist[i+1]:
                temp = alist[i]
                alist[i] = alist[i+1]
                alist[i+1] = temp
    return alist


def create_queue(q):
    params = parse_args()
    length = get_length()
    fd = os.open(params.FILE_NAME, os.O_RDONLY)
    try:
        for x in range(params.NUMBER_LINES / params.LINES_PER_FILE):
            start = os.read(fd, length)
            os.lseek(fd, length*(params.LINES_PER_FILE-2), 1)
            end = os.read(fd, length)
            q.put({"Start": start, "End": end, "StartLine": x*length*params.LINES_PER_FILE})
        
        nextline = os.read(fd, length)
        if nextline!="":
            int(math.ceil(params.NUMBER_LINES / params.LINES_PER_FILE))*length*params.LINES_PER_FILE
            start = nextline
            end = start
            while True:
                nextline = os.read(fd, length)
                if nextline=="":
                    break
                end=nextline
            q.put({
                    "Start": start
                    , "End": end,
                    "StartLine": int(math.ceil(params.NUMBER_LINES / params.LINES_PER_FILE))*length*params.LINES_PER_FILE
                    })
        
    finally:
        os.close(fd)


def sort_records_process(q):
    params = parse_args()
    fd = os.open(params.FILE_NAME, os.O_RDWR)
    length = get_length()
    try:
        while not q.empty():            
            block = q.get()
            os.lseek(fd, block["StartLine"], 0)
            txt=os.read(fd, get_length()*params.LINES_PER_FILE)        
            txt = "\n".join(
                bubblesort(txt[:-1].split(DOWN_LINE))
                )+"\n"
            os.lseek(fd, block["StartLine"], 0)
            os.write(fd, txt)
        
    finally:
        os.close(fd)


def sort_records():
    q = multiprocessing.Queue()
    create_queue(q)
    jobs = []
    for x in range(multiprocessing.cpu_count()):
        p = multiprocessing.Process(target=sort_records_process, args=(q, ))
        jobs.append(p)
        p.start()
    for job in jobs:
        job.join()
        print job
    q.close()


def sort_and_print(file_input, output, lines):
    params = parse_args()
    length = get_length()
    for z in range(params.NUMBER_LINES):
        smallest_line = bubblesort([x["line"] for x in lines])[0]
        n = [x["line"] for x in lines].index(smallest_line)
        os.write(output, smallest_line)
        os.lseek(file_input, lines[n]["cursor"], 0)
        newline = os.read(file_input, length)
        # If we finished reading the record
        if lines[n]["number_line"] == params.LINES_PER_FILE-1 or newline == "":
            del lines[n]
        # Switch to the next line
        else:
            lines[n]["number_line"] += 1
            lines[n]["cursor"] += get_length()
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


def check(output):
    params = parse_args()
    os.lseek(output, 0, 0)
    ans = True
    first_line = os.read(output, get_length())
    for x in range(params.NUMBER_LINES-1):
        second_line = os.read(output, get_length())
        if second_line < first_line:
            print "%s%s"%(second_line, first_line)
            ans = False
        first_line = second_line
    return ans


def main():
    start_time=time.time()
    params = parse_args()
    file_input = os.open(params.FILE_NAME, os.O_RDWR)
    output = os.open(params.FILE_OUTPUT_NAME, os.O_RDWR | os.O_CREAT)
    try:
        sort_records()
        start_time=time.time()
        lines = change_to_dictionaries(file_input)
        sort_and_print(file_input, output, lines)
        print check(output)
        print time.time() - start_time
    finally:
        os.close(file_input)
        os.close(output)
        

if __name__ == "__main__":
    main()