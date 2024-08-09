import scrapy
import json
from basic_spider.items import ProductItem
from scrapy.http import Response


class BaseSpider(scrapy.Spider):
    @staticmethod
    def read_local_file(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    @staticmethod
    def write_to_file(filename, data):
        with open(filename, 'a', encoding='utf-8') as file:
            file.write(data + "\n")


class ProductsSpider(BaseSpider):
    name = "orsay"
    start_urls = ["https://www.orsay.de/"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize the set to track the visited urls
        self.visited_urls = set()

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.extract_json_data)

    def extract_json_data(self, response: Response, **kwargs):
        script_content = response.css('script#__NEXT_DATA__::text').get()
        if script_content:
            try:
                data = json.loads(script_content)
                yield from self.extract_and_store_menu_items(data, response)
            except json.JSONDecodeError:
                self.logger.error("Failed to decode JSON from script tag.")
        else:
            self.logger.error(
                "No script tag with id '__NEXT_DATA__' found.")

    def extract_and_store_menu_items(self, data, response):
        menu_items = \
            data['props']['pageProps']['initialData']['layout']['header'][
                'menuItems']

        level_one_options = []
        level_two_options = []

        for item in menu_items:
            # Process Level One Option
            level_one_title = item.get("title")
            level_one_url = self.validate_url(item.get("url"))

            if level_one_title and level_one_url and self.is_url_new(
                    level_one_url):
                level_one_options.append({
                    "title": level_one_title,
                    "url": level_one_url,
                    "navigation_path": [level_one_title]
                })

                yield response.follow(level_one_url,
                                      callback=self.parse_listing_page,
                                      meta={'navigation_path': [
                                          level_one_title]})

                # Process Level Two Options
                for sub_item in item.get("data", []):
                    level_two_title = sub_item.get("title")
                    level_two_url = self.validate_url(sub_item.get("url"))

                    if (level_two_title and level_two_url and
                            self.is_url_new(level_two_url)):
                        level_two_options.append({
                            "title": level_two_title,
                            "url": level_two_url,
                            "navigation_path": [level_one_title,
                                                level_two_title]
                        })

                        yield response.follow(
                            level_two_url,
                            callback=self.parse_listing_page,
                            meta={'navigation_path': [
                                level_one_title, level_two_title]}
                        )

        self.write_to_file('orsay_level_one.json',
                           json.dumps(level_one_options, ensure_ascii=False,
                                      indent=4))

        self.write_to_file('orsay_level_two.json',
                           json.dumps(level_two_options, ensure_ascii=False,
                                      indent=4))

    def parse_listing_page(self, response, **kwargs):
        navigation_path = response.meta['navigation_path']

        for url in response.css("section.grid-cols-product-list > article > "
                                "div .product-card_colors__ZjuCK a::attr("
                                "href)").getall():
            validated_url = self.validate_url(url)

            if validated_url and self.is_url_new(validated_url):
                item = {
                    "navigation_path": navigation_path,
                    "url": validated_url
                }

                self.write_to_file('orsay_listing_page.json',
                                   json.dumps(item, ensure_ascii=False))

                yield response.follow(url=validated_url,
                                      callback=self.parse_product_page,
                                      meta={'navigation_path':
                                            navigation_path})

    def parse_product_page(self, response, **kwargs):

        item = ProductItem()
        item['title'] = response.css("article > div > div > h1::text").get()
        item['brand_name'] = response.css("div.pl-0 > div > "
                                          "span::text").get() or "Orsay"
        item['description'] = self.get_description(response.css("table > "
                                                                "tbody"))
        item['navigation_path'] = response.meta['navigation_path']
        item['base_sku'] = response.css("tbody > tr:last-child td::text").get()
        item['color_sku'] = str(item['base_sku']) + "_" + response.xpath(
            "//tbody//tr[th[text()='Farbe']]//td/span//text()").get()
        item['old_price'] = response.css("div.mt-2  span["
                                         "data-testid='price-recommended-"
                                         "price-span']::text").get()
        item['current_price'] = response.css("div.mt-2 span["
                                             "data-testid='price-discounted-se"
                                             "lling-price-span']::text").get()
        item['discount_percentage'] = str(self.calculate_discount(
            item['old_price'], item['current_price'])) + "%"
        item['color_name'] = response.xpath(
            "//tbody//tr[th[text()='Farbe']]//td/span//text()").get()
        item['image_urls'] = response.css("div[data-label='gallery, "
                                          "thumbnails'] img::attr("
                                          "src)").getall()
        item['sizes'] = response.css("div["
                                     "data-testid='product-detail-sizes-wrapp"
                                     "er-select-sizes-div'] "
                                     "button::text").getall()

        yield item

    def get_description(self, table_selector):
        description_parts = []

        for row in table_selector.css("tr"):
            # Extract the heading from the <th> element
            key = row.css("th::text").get().strip()

            # Extract the value from the <td> element
            # If <span> element is present
            value = row.css("td > span::text").get()

            # If no <span> is found, get the text directly from <td>
            if not value:
                value = row.css("td::text").get()

            if key and value:
                description_parts.append(f"{key}: {value.strip()}")

        return ", ".join(description_parts)

    def validate_url(self, relative_url):
        if not relative_url:
            return None
        elif relative_url.startswith("http"):
            return relative_url
        else:
            return self.start_urls[0] + relative_url.strip("/")

    def is_url_new(self, url):
        if url in self.visited_urls:
            return False
        else:
            self.visited_urls.add(url)
            return True

    def calculate_discount(self, old_price, current_price):
        if old_price and current_price:
            try:
                old_price = float(
                    old_price.replace(' EUR', '').replace(',', '.'))
                current_price = float(
                    current_price.replace(' EUR', '').replace(',', '.'))

                discount = ((old_price - current_price) / old_price) * 100
                return round(discount, 2)
            except ValueError:
                return 0
        return 0
