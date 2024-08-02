import os
import scrapy
import json
from scrapy.http import TextResponse
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
    name = "kipling"

    def start_requests(self, **kwargs):
        file_path = (
            '/Users/abdul.moiz01/PycharmProjects/BasicSpider/basic_spider'
            '/basic_spider/Kipling Page_Source/home_page.html'
        )
        url = f"file://{file_path}"
        yield scrapy.Request(url=url, callback=self.parse, meta={
            'file_path': file_path})

    def parse(self, response, **kwargs):
        file_path = response.meta['file_path']
        html_content = self.read_local_file(file_path)
        local_response = TextResponse(url=response.url, body=html_content,
                                      encoding='utf-8')

        for level_one_option in local_response.css(".main-navigation-items "
                                                   "> li"):

            option_name = [level_one_option.css(".level-top > "
                           "span.ui-menu-item__label::text").get()]
            option_url = level_one_option.css(
                "a.level-top::attr(href)").get()

            if option_name and option_url:
                self.write_to_file('kipling_level_one.json', json.dumps({
                    "navigation_path": option_name, "url": option_url
                }))

                self.process_level_two_options(level_one_option, option_name)

            yield from self.pass_call_to_listing_page()


    def process_level_two_options(self, level_one_option, option_name):
        for level_two_option in level_one_option.css("div ul li"):
            level_two_option_name = level_two_option.css("a span + "
                                                         "span::text").get()
            level_two_option_url = level_two_option.css("a::attr(href)").get()

            if level_two_option_name and level_two_option_url:
                navigation_path = option_name + [
                    level_two_option_name.strip().replace("\n", " ")]
                self.write_to_file('kipling_level_two.json', json.dumps({
                    "navigation_path": navigation_path, "url":
                        level_two_option_url}))

    def pass_call_to_listing_page(self):
        listing_file_path = (
            '/Users/abdul.moiz01/PycharmProjects/BasicSpider/basic_spider'
            '/basic_spider/Kipling Page_Source/listing_page (Bags > Sports '
            'Bag).html'
        )

        url = f"file://{listing_file_path}"
        yield scrapy.Request(url=url, callback=self.parse_listing_page,
                             meta={'file_path': listing_file_path})

    def parse_listing_page(self, response, **kwargs):
        file_path = response.meta['file_path']
        html_content = self.read_local_file(file_path)
        local_response = TextResponse(url=response.url, body=html_content,
                                      encoding='utf-8')

        for product in local_response.css(".products > li"):
            product_name = product.css("h2.product-item-name a::text").get()
            product_url = product.css("h2.product-item-name a::attr("
                                      "href)").get()
            product_colors = product.css("span.counter::text"
                                         ).get().strip(" Colours")
            description = product.css(".product-item-description > "
                                      "p::text").get()
            price = product.css("span.price::text").get()

            if product_name and product_url:
                self.write_to_file(
                    'kipling_listing_page_products.json',
                    json.dumps({
                        "product_name": product_name,
                        "product_url": product_url,
                        "colors_available": product_colors,
                        "product_description": description,
                        "product_price": price
                    })
                )

        yield from self.pass_call_to_details_pages()

    def pass_call_to_details_pages(self):
        details_pages_path = (
            '/Users/abdul.moiz01/PycharmProjects/BasicSpider/basic_spider'
            '/basic_spider/Kipling Page_Source/details_pages')

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
        item['title'] = local_response.css("h1.page-title span::text").get()
        item['brand_name'] = "Kipling"
        item['description'] = local_response.css(".product-info-description "
                                                 "p::text").get()
        item['navigation_path'] = "dummy-data"
        item['base_sku'] = local_response.css(".product-add-form form::attr("
                                              "data-product-sku)").get()
        item['color_sku'] = local_response.css(
            ".colorpattern-wrapper-product-details div::attr("
            "data-product-id)").get()
        item['old_price'] = str(local_response.css("div.active .price-box "
                                                   "div.old-price "
                                                   "span.price::text").get(
                                            )).replace("£", "$")
        item['current_price'] = str(local_response.css("div.active "
                                                       ".price-box "
                                                       "div.normal-price "
                                                       "span.price::text").get(
                                            )).replace("£", "$")
        item['discount_percentage'] = str(self.calculate_discount(
            item['old_price'], item['current_price'])) + "%"
        item['color_name'] = local_response.css(
            ".colorpattern-wrapper-product-details div::attr(colorname)").get()
        item['image_urls'] = local_response.css(".product-gallery__thumbs li "
                                                "img::attr(src)").getall()
        item['sizes'] = local_response.css(
            "div.vf-size-dimension-details::text").get().strip()

        yield item

    @staticmethod
    def calculate_discount(old_price, current_price):
        if old_price and current_price:
            try:
                old_price = float(old_price.strip("$"))
                current_price = float(current_price.strip("$"))
                discount = ((old_price - current_price) / old_price) * 100
                return round(discount, 2)
            except ValueError:
                return 0
        return 0
