import os
import math
import argparse
import multiprocessing

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


def get_length(number_per_line):
    return int(math.ceil(number_per_line/3.0)*4+2)


def bubblesort(alist):
    for passnum in range(len(alist)-1, 0, -1):
        for i in range(passnum):
            if alist[i] > alist[i+1]:
                temp = alist[i]
                alist[i] = alist[i+1]
                alist[i+1] = temp
    return alist


def create_queue(q, number_lines, lines_per_file, number_per_line):
    length = get_length(number_per_line)
    for x in range(int(math.ceil(float(number_lines) / lines_per_file))):
        q.put({"StartLine": x*length*lines_per_file})


def sort_records_process(q, number_per_line):
    params = parse_args()
    fd = os.open(params.FILE_NAME, os.O_RDWR)
    length = get_length(number_per_line)
    try:
        while not q.empty():            
            block = q.get()
            os.lseek(fd, block["StartLine"], 0) 
            txt = "\n".join(
                bubblesort(os.read(fd, length*params.LINES_PER_FILE)[:-1].split(DOWN_LINE))
                )+"\n"
            os.lseek(fd, block["StartLine"], 0)
            os.write(fd, txt)        
    finally:
        os.close(fd)


def sort_records(number_lines, lines_per_file, number_per_line):
    q = multiprocessing.Queue()
    create_queue(q, number_lines, lines_per_file, number_per_line)
    jobs = []
    for x in range(multiprocessing.cpu_count()):
        p = multiprocessing.Process(target=sort_records_process, args=(q, number_per_line))
        jobs.append(p)
        p.start()
    q.close()
    for job in jobs:
        job.join()


def sort_and_print(file_input, output, lines, number_lines, lines_per_file, number_per_line):
    length = get_length(number_per_line)
    for z in range(number_lines):
        smallest_line = bubblesort([x["line"] for x in lines])[0]
        n = [x["line"] for x in lines].index(smallest_line)
        os.write(output, smallest_line)        
        os.lseek(file_input, lines[n]["cursor"], 0)   
        newline = os.read(file_input, length)
        # If we finished reading the record
        if lines[n]["number_line"] == lines_per_file-1 or newline == "":
            del lines[n]
        # Switch to the next line
        else:
            lines[n]["number_line"] += 1
            lines[n]["cursor"] += length
            lines[n]["line"] = newline
        

def change_to_dictionaries(fd, number_lines, lines_per_file, number_per_line):
    ans = []
    length = get_length(number_per_line)
    for x in range(
            int(math.ceil(float(number_lines) / lines_per_file))
            ):
        ans.append(
            {
                "number_line": 0,
                "cursor": x*length*lines_per_file+length,
                "line": os.read(fd, length)
            }
        )
        os.lseek(fd, (lines_per_file-1)*length, os.SEEK_CUR)
    os.lseek(fd, 0, 0)
    return ans


def check(output, number_lines, number_per_line):
    os.lseek(output, 0, 0)
    ans = True
    length = get_length(number_per_line)
    first_line = os.read(output, length)
    for x in range(number_lines-1):
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
        sort_records(params.NUMBER_LINES, params.LINES_PER_FILE, params.NUMBER_PER_LINE)
        lines = change_to_dictionaries(file_input, params.NUMBER_LINES, params.LINES_PER_FILE, params.NUMBER_PER_LINE)
        sort_and_print(file_input, output, lines, params.NUMBER_LINES, params.LINES_PER_FILE, params.NUMBER_PER_LINE)
        print check(output, params.NUMBER_LINES, params.NUMBER_PER_LINE)
    finally:
        os.close(file_input)
        os.close(output)
        

if __name__ == "__main__":
    main()
