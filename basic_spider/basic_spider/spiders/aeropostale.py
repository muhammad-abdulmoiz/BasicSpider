import os
import scrapy
from scrapy.http import TextResponse
import json
from basic_spider.items import ProductItem


class BaseSpider(scrapy.Spider):
    @staticmethod
    def read_local_file(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    @staticmethod
    def write_to_file(filename, data):
        with open(filename, 'a') as file:
            file.write(data + "\n")


class ProductsSpider(BaseSpider):
    name = "aeropostale"

    def start_requests(self, **kwargs):
        file_path = (
            '/Users/abdul.moiz01/PycharmProjects/BasicSpider/basic_spider/'
            'basic_spider/Aeropostale Page_Source/home_page.html'
        )
        url = f"file://{file_path}"
        yield scrapy.Request(url=url, callback=self.parse, meta={
            'file_path': file_path})

    def parse(self, response, **kwargs):
        file_path = response.meta['file_path']
        html_content = self.read_local_file(file_path)
        local_response = TextResponse(url=response.url, body=html_content,
                                      encoding='utf-8')

        for level_one_option in local_response.css(
                ".menu-category .level-1 > li"):
            option_name = [level_one_option.css(
                "span a::text").get().strip()]
            option_url = level_one_option.css("span a::attr(href)").get()

            self.write_to_file('level_one.json', json.dumps({
                "navigation_path": option_name, "url": option_url
            }))

            self.process_level_two_options(level_one_option, option_name)
            self.process_level_two_other_options(level_one_option, option_name)

        yield from self.pass_call_to_listing_page()

    def process_level_two_options(self, level_one_option, option_name):
        for level_two_option in level_one_option.css(
                "div.level-2 > ul:first-of-type > li"):
            level_two_option_name = level_two_option.css(
                "a::text").get()
            level_two_option_url = level_two_option.css(
                "a::attr(href)").get()

            if level_two_option_name and level_two_option_url:
                navigation_path = option_name + [
                    level_two_option_name.strip().replace("\n", " ")]
                self.write_to_file('level_two.json', json.dumps({
                    "navigation_path": navigation_path, "url":
                        level_two_option_url}))

            self.process_level_three_options(level_two_option, option_name,
                                             level_two_option_name)

    def process_level_three_options(self, level_two_option, option_name,
                                    level_two_option_name):
        for level_three_option in level_two_option.css(
                "ul.level-3 li"):
            level_three_option_name = level_three_option.css(
                "a::text").get()
            level_three_option_url = level_three_option.css(
                "a::attr(href)").get()

            if level_three_option_name and level_three_option_url:
                navigation_path = option_name + [
                    level_two_option_name.strip(),
                    level_three_option_name.strip().replace("\n", " ")]
                self.write_to_file('level_three.json', json.dumps({
                    "navigation_path": navigation_path, "url":
                        level_three_option_url}))

    def process_level_two_other_options(self, level_one_option, option_name):
        for level_two_option in level_one_option.css(
                "div.level-2 > ul.last-child li"):
            level_two_option_name = level_two_option.css(
                "a span::text").get() or level_two_option.css(
                "li a::text").get()
            level_two_option_url = level_two_option.css(
                "li a::attr(href)").get()

            if level_two_option_name and level_two_option_url:
                navigation_path = option_name + [
                    level_two_option_name.strip().replace("\n", " ")]
                self.write_to_file('level_two.json', json.dumps({
                    "navigation_path": navigation_path, "url":
                        level_two_option_url}))

    def pass_call_to_listing_page(self):
        listing_file_path = (
            '/Users/abdul.moiz01/PycharmProjects/BasicSpider/basic_spider/'
            'basic_spider/Aeropostale Page_Source/listing_page.html '
            '(Men > Accessories).html'
        )
        url = f"file://{listing_file_path}"
        yield scrapy.Request(url=url, callback=self.parse_listing_page,
                             meta={'file_path': listing_file_path})

    def parse_listing_page(self, response, **kwargs):
        file_path = response.meta['file_path']
        html_content = self.read_local_file(file_path)
        local_response = TextResponse(url=response.url, body=html_content,
                                      encoding='utf-8')

        for product in local_response.css("#search-result-items > div"):
            product_name = product.css(".product-name a::text").get().strip()
            product_url = product.css(".product-name a::attr(href)").get()

            if product_name and product_url:
                self.write_to_file('listing_page_products.json', json.dumps({
                    "product_name": product_name, "product_url": product_url
                }))

        yield from self.pass_call_to_details_pages()

    def pass_call_to_details_pages(self):
        details_pages_path = (
            '/Users/abdul.moiz01/PycharmProjects/BasicSpider/basic_spider'
            '/basic_spider/Aeropostale Page_Source/details_pages')

        for filename in os.listdir(details_pages_path):
            file_path = os.path.join(details_pages_path, filename)
            url = f"file://{file_path}"

            yield scrapy.Request(url=url, callback=self.parse_details_page,
                                 meta={'file_path': file_path})

    def parse_details_page(self, response, **kwargs):
        file_path = response.meta['file_path']

        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()

        local_response = TextResponse(url=response.url, body=html_content,
                                      encoding='utf-8')

        item = ProductItem()
        item['title'] = local_response.css(".product-name::text").get().strip()
        item['brand_name'] = local_response.css(
            "#product-content span::text").get().strip()
        item['description'] = local_response.css(
            "div.product-detail + div .long-description > p + ul "
            "li::text").getall()
        item['navigation_path'] = "dummydata"
        item['base_sku'] = local_response.css(".bfx-sku::text").get().strip()
        item['color_sku'] = local_response.css(
            ".product-variations a::attr(data-name)").get().strip()
        item['old_price'] = local_response.css(
            ".product-price .bfx-list-price::text").get().strip()
        item['current_price'] = local_response.css(
            ".product-price .price-promo::text").get().strip()
        item['discount_percentage'] = str(self.calculate_discount(
            item['old_price'], item['current_price'])) + "%"
        item['color_name'] = local_response.css(
            ".product-variations span::text").get().strip()
        item['image_urls'] = local_response.css(
            "img.product-image__desktop::attr(src)").getall()
        item['sizes'] = self.get_sizes(local_response)

        yield item

    @staticmethod
    def calculate_discount(old_price, current_price):
        if old_price and current_price:
            try:
                old_price = float(old_price.replace('$', ''))
                current_price = float(current_price.replace('$', ''))
                discount = ((old_price - current_price) / old_price) * 100
                return round(discount, 2)
            except ValueError:
                return 0
        return 0

    @staticmethod
    def get_sizes(response):
        sizes = []
        size_names = response.css(".product-variations a::attr("
                                  "data-value)").getall()
        size_ids = response.css(".product-variations .tabs-content "
                                "a::text").getall()
        size_ids = [size_id.strip() for size_id in size_ids]
        sizes.append({
            'size_names': size_names,
            'size_ids': size_ids
        })
        return sizes
