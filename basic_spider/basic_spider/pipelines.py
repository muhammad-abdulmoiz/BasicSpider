import scrapy
import json


class ProductPipeline:
    def __init__(self):
        self.products = None
        self.dropped_products = None

    def open_spider(self, spider):
        self.products = open('products.json', 'a')
        self.dropped_products = open('dropped_products.json', 'a')

    def process_item(self, item, spider):
        json_line = json.dumps(dict(item)) + "\n"
        if self.validate_item(item):
            self.products.write(json_line)
        else:
            self.dropped_products.write(json_line)

        return item

    @staticmethod
    def validate_item(item):
        if len(item.get('base_sku', '')) >= 35:
            return False

        if len(item.get('color_sku', '')) >= 50:
            return False

        if item.get('discount_percentage', 0) < 0:
            return False

        if not all([item.get('title'), item.get('brand_name'),
                    item.get('description'), item.get('current_price')]):
            return False

        return True

    def close_spider(self, spider):
        self.products.close()
        self.dropped_products.close()
