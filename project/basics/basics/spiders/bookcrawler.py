from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from .book import parse_book


class BookcrawlerSpider(CrawlSpider):
    name = "bookcrawler"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    rules = (
        Rule(LinkExtractor(allow='catalogue/page')),
        Rule(LinkExtractor(allow='catalogue', deny=('category', 'page')), callback="parse_item"),
    )

    def parse_item(self, response):
        yield parse_book(response)
