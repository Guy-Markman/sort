import os
import base64
import math
import argparse

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
        '--TEMP-FILE-NAME',
        default="t",
        help='The name of the files before their number, default: %(default)s',
    )
    parser.add_argument(
        '--FILE-OUTPUT-NAME',
        default="output.txt",
        help='The file output file, default: %(default)s',
    )
    
    args = parser.parse_args()
    return args
    
    
def bubbleSort(alist):
    for passnum in range(len(alist)-1,0,-1):
        for i in range(passnum):
            if alist[i]>alist[i+1]:
                temp = alist[i]
                alist[i] = alist[i+1]
                alist[i+1] = temp
    return alist
    
    
def write_temp_file(fd, new_file_name, n_letters):
    params=parse_args()
    try:
        new_file = os.open(new_file_name, os.O_RDWR | os.O_CREAT)
        lines = []
        for x in range(params.LINES_PER_FILE):
            lines.append(os.read(fd, n_letters))
        lines.sort()
        os.write(new_file, "".join(lines))
        lines=bubbleSort(lines)
    finally:
        os.close(new_file)


def create_temp_files(base_file):
    params=parse_args()
    for x in range(params.NUMBER_LINES/params.LINES_PER_FILE):
        write_temp_file(base_file, "%s%s.txt" % (params.TEMP_FILE_NAME, x),
                        int(math.ceil(params.NUMBER_PER_LINE/8.0)*8+2))


def merge(number_files):  # Notice that number_files start at 0. return the last file
    x = 0
    while x <= number_files:
        if x < number_files:
            file_merge(number_files, x)
            x += 2
            number_files+=1
        else:
            x += 1
    return number_files


def file_merge(number_files, x):#merging files
    params=parse_args()
    new_file = os.open("%s%s.txt"%(params.TEMP_FILE_NAME, number_files+1), os.O_RDWR | os.O_CREAT)
    fd1 = os.open("%s%s.txt"%(params.TEMP_FILE_NAME, x), os.O_RDWR)
    fd2 = os.open("%s%s.txt"%(params.TEMP_FILE_NAME, x+1), os.O_RDWR)
    length = int(math.ceil(params.NUMBER_PER_LINE/8.0)*8+2)
    t1 = os.read(fd1, length)
    t2 = os.read(fd2, length)
    while t1 != '' and t2 != '':
        if t1 < t2:
            os.write(new_file, t1)
            t1 = os.read(fd1, length)
        else:
            os.write(new_file, t2)
            t2 = os.read(fd2, length)

    if t1 != '':
        os.write(new_file, t1)
        t1 = os.read(fd1, 100)
        while t1 != '':
            os.write(new_file, t1)
            t1 = os.read(fd1, 100)
    if t2 != '':
        os.write(new_file, t2)
        t2 = os.read(fd2, 100)
        while t2 != '':
            os.write(new_file, t2)
            t2 = os.read(fd2, 100)

    try:
        os.close(new_file)

    except IOError:
        pass

    try:
        os.close(fd1)
        os.remove("%s%s.txt"%(params.TEMP_FILE_NAME, x))
    except IOError:
        pass

    try:
        os.close(fd2)
        os.remove("%s%s.txt"%(params.TEMP_FILE_NAME, x+1))

    except IOError:
        pass


def main():
    params=parse_args()
    try:   
        fd = os.open(params.FILE_NAME, os.O_RDWR)
        create_temp_files(fd)
        output=merge((params.NUMBER_LINES/params.LINES_PER_FILE)-1)

    finally:
        try:
            os.close(fd)
        except IOError:
            pass
    os.rename("%s%s.txt" % (params.TEMP_FILE_NAME, output), params.FILE_OUTPUT_NAME)
if __name__ == "__main__":
    main()
