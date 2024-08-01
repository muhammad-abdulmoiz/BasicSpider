import scrapy


class ProductItem(scrapy.Item):
    title = scrapy.Field()
    brand_name = scrapy.Field()
    description = scrapy.Field()
    navigation_path = scrapy.Field()
    base_sku = scrapy.Field()
    color_sku = scrapy.Field()
    old_price = scrapy.Field()
    current_price = scrapy.Field()
    discount_percentage = scrapy.Field()
    color_name = scrapy.Field()
    image_urls = scrapy.Field()
    sizes = scrapy.Field()
