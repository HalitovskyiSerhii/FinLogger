import re
from pathlib import Path

from logger import LOGGER


class Parser:
    fn_matcher = re.compile(r'\d*\s*([\d*\-]*TOP.ENC)')

    extractor = re.compile(r'(\d{2}:\d{2}:\d{2})\s*CASH\s*WITHDRAWAL\s*([1-9]*,*[0-9]*,*[0-9]*\.[0-9]{1,2})\s*UAH\s*\n'
                           r'[0-9{1}\-\s]*\s*\n'
                           r'\s*([0-9X]{16}).*\n'
                           r'AUTH\. CODE:\s*(\d*)', re.MULTILINE)

    prosecure = 'None'

    @classmethod
    def get_matchers(cls, path: Path):
        raw_filename = path.stem
        prosecure = cls.fn_matcher.findall(raw_filename)[0]
        cls.prosecure = prosecure

        page_breaker = re.compile(r'.*\n([\s*\d+/\n]*'
                                  r'[[\-\s]*Page[\s\d+\-]*\n]*'
                                  f'ProSecure\s+{prosecure}\s*\n*)', re.MULTILINE)
        first_page = re.compile(r'([[-]*\s*Page\s*\d+[-]*\n]*'
                                f'ProSecure\s+{prosecure}\s*\n*)', re.MULTILINE)

        return first_page, page_breaker

    @classmethod
    def read_pages(cls, path: Path, page_count=-1, from_line=1):
        LOGGER.info('#' * 5 + 'START READING' + '#' * 5)
        page_breaker, first_page = cls.get_matchers(path)
        pages = []
        cur_line = 0
        s = None
        with path.open('rt') as f:
            read_lines = []
            for line in f:
                cur_line += 1
                # Skip empty lines
                if cur_line < from_line or line == '\n':
                    continue

                # Append line to temp list and convert to string
                # collected lines
                read_lines.append(line)
                s = ''.join(read_lines)

                if page_breaker.findall(s):
                    # When end of page found, adding it without page header
                    pages.append(''.join(read_lines[:-3]))
                    # Flush temp lines
                    read_lines = []
                    if len(pages) == page_count:
                        return pages, cur_line + 1
                    continue
                if first_page.match(s):
                    # First page header matcher
                    read_lines = []
        return pages, cur_line + 1, s

    @classmethod
    def extract(cls, pages):
        records = []
        for i in range(len(pages) - 1):
            # Concat two pages to search info into transactions
            # without page pages
            s = pages[i] + pages[i + 1]
            res = cls.extractor.findall(s)
            # Add only unique values
            records += [record for record in res if record not in records]

        return records

    @classmethod
    def pipe(cls, path: Path):
        pgs, _, broken = cls.read_pages(path)
        return cls.extract(pgs + [broken])
