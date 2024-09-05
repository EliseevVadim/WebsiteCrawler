import requests
import re

from bs4 import BeautifulSoup
from core.file_utils import *
from urllib.parse import urljoin, urlparse, unquote
from core.logger import logger
from core.constants import *


def get_soup_by_link(link):
    try:
        response = requests.get(link, timeout=TIMEOUT)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.exceptions.Timeout:
        raise TimeoutError
    except Exception as err:
        logger.error(f"Ошибка при запросе {link}: {err}")


def extract_url_from_onclick(onclick_value):
    match = re.search(r"['\"](https?://.*?|/.*?)['\"]", onclick_value)
    if match:
        return match.group(1)


def link_lead_to_file(url):
    parsed_url = urlparse(url)
    possible_file_name = os.path.basename(parsed_url.path)
    file_extension = os.path.splitext(possible_file_name)[1].lower()
    return file_extension != ""


class Crawler:
    def __init__(self, url, content_class, data_path, ignore_files=False):
        self.__url = url
        self.__content_class = content_class
        self.__data_path = data_path
        self.__ignore_files = ignore_files
        self.__visited = set()
        self.__base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"

    def crawl(self, depth=None, normalize_names=False):
        directory_name = prepare_crawl_environment(self.__data_path)
        self.__data_path = directory_name
        self.crawling_step(self.__url, depth)
        if normalize_names:
            normalize_filenames(directory_name)

    def crawling_step(self, url, depth):
        try:
            if url in self.__visited:
                return
            if link_lead_to_file(url):
                if not self.__ignore_files:
                    self.download_file(url)
                return
            logger.info(f"Обрабатываем url: {url}")
            self.__visited.add(url)
            soup = get_soup_by_link(url)
            self.save_page_text(soup, url)
            if depth is not None:
                if depth <= 0:
                    return
                depth -= 1
            links = self.get_links(soup)
            if links:
                for link in links:
                    self.crawling_step(link, depth)
        except TimeoutError:
            logger.warning(f"Обработка URL {url} заняла много времени. Ссылка записана в соответствующий файл")
            with open(PROBLEM_LINKS_FILENAME, "a") as f:
                f.write(url + "\n")
        except Exception as err:
            logger.error(f"При обработке {url} произошла ошибка {err}")

    def get_links(self, soup: BeautifulSoup):
        if soup is None:
            return
        links = set()
        for link in soup.find_all('a', href=True):
            new_url = urljoin(self.__base_url, link['href'])
            if new_url not in self.__visited and new_url.startswith(self.__base_url):
                links.add(new_url)
        for element in soup.find_all(attrs={"onclick": True}):
            onclick_value = element['onclick']
            onclick_url = extract_url_from_onclick(onclick_value)
            if onclick_url:
                new_url = urljoin(self.__base_url, onclick_url)
                if new_url not in self.__visited and new_url.startswith(self.__base_url):
                    links.add(new_url)
        return list(links)

    def save_page_text(self, soup, url):
        try:
            content_div = soup.find('div', class_=self.__content_class)
            if content_div is None:
                logger.warning(f"Контент на странице {url} не найден")
                return
            page_text = content_div.get_text(separator='\n\n', strip=True)
            title = soup.title.string.strip() if soup.title else "index"
            page_name = re.sub(r'[\\/*?:"<>|]', "_", title)
            with open(f"{self.__data_path}/{page_name}.txt", "w", encoding="utf-8") as f:
                f.write(page_text)
            logger.info(f"Page {page_name} saved")
        except Exception as err:
            logger.error(f"При обработке url: {url} произошла ошибка {err}")

    def download_file(self, url):
        try:
            parsed_url = urlparse(url)
            file_name = os.path.basename(parsed_url.path)
            file_name = unquote(file_name)
            response = requests.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            file_path = os.path.join(self.__data_path, "files", file_name)
            with open(file_path, "wb") as file:
                file.write(response.content)
            logger.info(f"Файл {file_name} успешно скачан")
        except requests.exceptions.Timeout:
            raise TimeoutError
        except requests.exceptions.RequestException as err:
            logger.error(f"Ошибка при загрузке файла {url}: {err}")
