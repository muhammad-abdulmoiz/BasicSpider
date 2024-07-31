import os
import scrapy
from scrapy.http import TextResponse
import json
import copy
from basic_spider.items import ProductItem


class ProductsSpider(scrapy.Spider):
    name = "aeropostale"

    def start_requests(self):
        file_path = ('/Users/abdul.moiz01/PycharmProjects/BasicSpider'
                     '/basic_spider/basic_spider/Aeropostale '
                     'Page_Source/home_page.html')

        url = f"file://{file_path}"

        yield scrapy.Request(url=url, callback=self.parse, meta={
            'file_path': file_path, 'navigation_path': []})

    def parse(self, response, **kwargs):
        file_path = response.meta['file_path']
        # navigation_path = response.meta['navigation_path']
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()

        local_response = TextResponse(url=response.url, body=html_content,
                                      encoding='utf-8')
        level_one_options = local_response.css(".menu-category .level-1 > li")

        for level_one_option in level_one_options:
            option_name = [level_one_option.css("span a::text").get().strip(
                "\n")]
            option_url = level_one_option.css("span a::attr(href)").get()

            json_line = (json.dumps({"navigation_path": option_name,
                                     "url": option_url}) + "\n")
            with open('level_one.json', 'a') as level_1:
                level_1.write(json_line)

            level_two_options = level_one_option.css("div.level-2 > "
                                                     "ul:first-of-type > li")

            for level_two_option in level_two_options:
                level_two_option_name = level_two_option.css("a::text").get()
                level_two_option_url = level_two_option.css("a::attr("
                                                            "href)").get()

                if level_two_option_name and level_two_option_url:
                    navigation_path = copy.deepcopy(option_name)
                    navigation_path.append(level_two_option_name.strip(
                        "\n").replace("\n", " "))

                    json_line = (json.dumps({"navigation_path":
                                             navigation_path, "url":
                                             level_two_option_url}) + "\n")

                    with open('level_two.json', 'a') as level_2:
                        level_2.write(json_line)

                level_three_options = level_two_option.css("ul.level-3 li")

                for level_three_option in level_three_options:
                    level_three_option_name = level_three_option.css(
                        "a::text").get()
                    level_three_option_url = level_three_option.css(
                        "a::attr(href)").get()

                    if level_three_option_name and level_three_option_url:
                        navigation_path = copy.deepcopy(option_name)
                        navigation_path.append(level_two_option_name.strip(
                            "\n").replace("\n", " "))
                        navigation_path.append(level_three_option_name.strip(
                            "\n").replace("\n", " "))

                        json_line = (json.dumps({"navigation_path":
                                     navigation_path,
                                     "url": level_three_option_url}) + "\n")

                        with open('level_three.json', 'a') as level_3:
                            level_3.write(json_line)

            level_two_other_options = level_one_option.css("div.level-2 > "
                                                           "ul.last-child li")

            for level_two_option in level_two_other_options:
                level_two_option_name = level_two_option.css("a span"
                                                             "::text").get()
                level_two_option_url = level_two_option.css("li a::attr("
                                                            "href)").get()

                if not level_two_option_name:
                    level_two_option_name = level_two_option.css("li a::"
                                                                 "text").get()

                if level_two_option_name and level_two_option_url:
                    navigation_path = copy.deepcopy(option_name)
                    navigation_path.append(level_two_option_name.strip(
                        "\n"))

                    json_line = (json.dumps({"navigation_path":
                                             navigation_path, "url":
                                             level_two_option_url}) + "\n")

                    with open('level_two.json', 'a') as level_2:
                        level_2.write(json_line)

        yield from self.pass_call_to_listing_page()

    def pass_call_to_listing_page(self):
        listing_file_path = (
            '/Users/abdul.moiz01/PycharmProjects/BasicSpider/basic_spider'
            '/basic_spider/Aeropostale Page_Source/listing_page.html (Men > '
            'Accessories).html')

        url = f"file://{listing_file_path}"

        yield scrapy.Request(url=url, callback=self.parse_listing_page,
                             meta={'file_path': listing_file_path})

    def parse_listing_page(self, response,  **kwargs):
        file_path = response.meta['file_path']

        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()

        local_response = TextResponse(url=response.url, body=html_content,
                                      encoding='utf-8')

        products = local_response.css("#search-result-items > div")

        for product in products:
            product_name = product.css(".product-name a::text").get().strip(
                "\n")
            product_url = product.css(".product-name a::attr(href)").get()

            if product_name and product_url:
                json_line = json.dumps({"product_name": product_name,
                                        "product_url": product_url}) + "\n"

                with open('listing_page_products.json', 'a') as product_file:
                    product_file.write(json_line)

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
            ".long-description li::text").get().strip()
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








