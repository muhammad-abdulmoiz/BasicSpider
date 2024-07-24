import scrapy
from basic_spider.items import ProductItem


class ProductsSpider(scrapy.Spider):
    name = "products"
    start_urls = [
        "https://quotes.toscrape.com/page/1/",
    ]

    def parse(self, response, **kwargs):
        demo_item = ProductItem(
            title="Men's Classic T-Shirt",
            brand_name="FashionBrand",
            description="A classic men's t-shirt made from 100% cotton. "
                        "Comfortable and perfect for everyday wear.",
            navigation_path="Home > Men > Clothing > T-Shirts",
            base_sku="MTSHIRT12345",
            color_sku="MTSHIRT-BLUE-L",
            old_price="25.00",
            current_price="20.00",
            discount_percentage=20,
            color_name="Blue",
            image_urls=[
                "http://example.com/images/1.jpg",
                "http://example.com/images/2.jpg"
            ],
            sizes=[
                {"size_name": "S", "size_identifier": "MTSHIRT-BLUE-S",
                 "stock": 15},
                {"size_name": "M", "size_identifier": "MTSHIRT-BLUE-M",
                 "stock": 20},
                {"size_name": "L", "size_identifier": "MTSHIRT-BLUE-L",
                 "stock": 10},
                {"size_name": "XL", "size_identifier": "MTSHIRT-BLUE-XL",
                 "stock": 5}
            ]
        )
        yield demo_item

        another_demo_item = ProductItem(
            brand_name="FashionBrand",
            description="A classic men's t-shirt made from 100% cotton. "
                        "Comfortable and perfect for everyday wear.",
            navigation_path="Home > Men > Clothing > T-Shirts",
            base_sku="MTSHIRT12345",
            color_sku="MTSHIRT-BLUE-L",
            old_price="25.00",
            current_price="20.00",
            discount_percentage=-20,
            color_name="Blue",
            image_urls=[
                "http://example.com/images/1.jpg",
                "http://example.com/images/2.jpg"
            ],
            sizes=[
                {"size_name": "S", "size_identifier": "MTSHIRT-BLUE-S",
                 "stock": 15},
                {"size_name": "M", "size_identifier": "MTSHIRT-BLUE-M",
                 "stock": 20},
                {"size_name": "L", "size_identifier": "MTSHIRT-BLUE-L",
                 "stock": 10},
                {"size_name": "XL", "size_identifier": "MTSHIRT-BLUE-XL",
                 "stock": 5}
            ]
        )
        yield another_demo_item


