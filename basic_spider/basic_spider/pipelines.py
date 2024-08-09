import scrapy
import json


class ProductPipeline:
    def __init__(self):
        self.products = None
        self.dropped_products = None

    def open_spider(self, spider):
        self.products = open('orsay_products.json', 'a', encoding='utf-8')
        self.dropped_products = open('orsay_dropped_products.json', 'a', encoding='utf-8')

    def process_item(self, item, spider):
        item['sizes'] = [size.strip() for size in item['sizes']]

        json_line = json.dumps(dict(item), ensure_ascii=False) + "\n"
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

        try:
            discount_percentage = item.get('discount_percentage', '0%').strip('%')
            if float(discount_percentage) < 0:
                return False
        except ValueError:
            return False

        if not all([item.get('title'), item.get('brand_name'),
                    item.get('description'), item.get('current_price')]):
            return False

        return True

    def close_spider(self, spider):
        self.products.close()
        self.dropped_products.close()
