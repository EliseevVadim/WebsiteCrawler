import argparse
import sys

from core.crawling_utils import *

data_path = "data"


def check_arguments(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', type=str, help='root URL for crawl', required=True)
    parser.add_argument('-tag', '--content_class', type=str, help='tag to get text content from',
                        required=True)
    parser.add_argument('-d', '--depth', type=int, help='depth of crawl', required=False, default=None)
    parser.add_argument('-n', '--normalize_filenames', action=argparse.BooleanOptionalAction,
                        help='marks that we gonna normalize names of files for parsed html pages', required=False,
                        default=False)
    parser.add_argument('-ignore_files', '--ignore_files', action=argparse.BooleanOptionalAction,
                        help='marks that we gonna parse html pages only', required=False,
                        default=False)
    parsed = parser.parse_args(args)
    return parsed.url, parsed.content_class, parsed.depth, parsed.normalize_filenames, parsed.ignore_files


if __name__ == '__main__':
    url, content_class, depth, normalize_filenames, ignore_files = check_arguments(sys.argv[1:])
    crawler = Crawler(url=url, data_path=data_path, content_class=content_class, ignore_files=ignore_files)
    crawler.crawl(normalize_names=normalize_filenames, depth=depth)
