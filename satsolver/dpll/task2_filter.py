import random

from argparse import ArgumentParser
from os import listdir, remove
from os.path import isfile, join

def filter_files(dir_name):
    total_number_of_files = sum([1 for f in listdir(dir_name) if isfile(join(dir_name, f))])
    to_keep = random.sample(list(range(total_number_of_files)), total_number_of_files // 10)
    
    for i, file in enumerate(listdir(dir_name)):
        total_number_of_files += 1
        if isfile(join(dir_name, file)) and i not in to_keep:
            remove(join(dir_name, file))

def main():
    parser = ArgumentParser()
    parser.add_argument("dir_name")
    args = parser.parse_args()
    filter_files(args.dir_name)

if __name__ == "__main__":
    main()