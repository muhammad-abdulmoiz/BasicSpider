from scrapy import signals
import logging


class CustomHeadersMiddleware:
    def __init__(self, headers):
        self.headers = headers

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        headers = settings.get('CUSTOM_HEADERS', {})
        return cls(headers)

    def process_request(self, request, spider):
        for header, value in self.headers.items():
            request.headers[header] = value
        logging.debug(f"Request headers: {request.headers}")


CUSTOM_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 '
                  'Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
              'image/avif,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'en-US,en;q=0.9',
}
