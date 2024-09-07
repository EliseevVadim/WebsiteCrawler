import os
import shutil

from datetime import datetime
from difflib import SequenceMatcher
from core.logger import logger
from core.constants import PROBLEM_LINKS_FILENAME


def prepare_crawl_environment(data_path):
    crawl_result_directory = create_directory_for_crawl(data_path)
    create_problem_links_file()
    return crawl_result_directory


def create_problem_links_file():
    file = open(PROBLEM_LINKS_FILENAME, "w")
    file.close()
    logger.info("Файл для записи проблемных ссылок успешно создан")


def create_directory_for_crawl(data_path):
    directory_name = f"{data_path}/crawl_at_{datetime.now().strftime('%d.%m.%Y')}"
    if os.path.exists(directory_name):
        shutil.rmtree(directory_name)
        logger.info(f"Директория {directory_name} успешно очищена")
    os.makedirs(directory_name)
    os.makedirs(f"{directory_name}/files")
    logger.info(f"Директория {directory_name} успешно создана")
    return directory_name


def normalize_filenames(directory):
    logger.info("Процедура нормализации имен файлов запущена")
    filenames = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    part_to_remove = find_longest_common_substring(filenames)
    if not part_to_remove:
        return
    for filename in filenames:
        new_name = filename.replace(part_to_remove, "").strip()
        new_path = os.path.join(directory, new_name)
        old_path = os.path.join(directory, filename)
        os.rename(old_path, new_path)
    logger.info("Имена файлов успешно нормализованы")


def find_longest_common_substring(strings):
    if not strings:
        return ""

    common_substring = strings[0]

    for s in strings[1:]:
        sequence_matcher = SequenceMatcher(None, common_substring, s)
        matched = sequence_matcher.find_longest_match(0, len(common_substring), 0, len(s))
        common_substring = common_substring[matched.a: matched.a + matched.size]

        if not common_substring:
            break

    return common_substring.strip()
