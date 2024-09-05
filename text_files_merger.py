import os
import sys

from core.logger import logger


def merge_files(files_directory, output_file_path):
    filenames = os.listdir(files_directory)
    filenames = [filename for filename in filenames if os.path.isfile(os.path.join(files_directory, filename))]
    filenames = [os.path.join(files_directory, filename) for filename in filenames]
    with open(output_file_path, 'w', encoding='utf-8') as output:
        for filename in filenames:
            with open(filename, 'r', encoding='utf-8') as input_file:
                for line in input_file:
                    output.write(line)
    logger.info("Файлы успешно объединены")


files_path = sys.argv[1]
output_file = sys.argv[2]
merge_files(files_path, output_file)
