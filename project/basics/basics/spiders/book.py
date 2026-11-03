import scrapy
from ..items import BookItem

number_dict = {'One': '1', 'Two': '2', 'Three': '3', 'Four': '4', 'Five': '5'}


def parse_book(response):
    """책 상세 페이지 -> BookItem. book / bookcrawler 스파이더가 함께 사용."""
    book = BookItem()

    book['name'] = response.css('div.product_main h1::text').get()
    book['price_exc_tax'] = response.xpath('//th[text()="Price (excl. tax)"]/following-sibling::td/text()').get()
    book['price_inc_tax'] = response.xpath('//th[text()="Price (incl. tax)"]/following-sibling::td/text()').get()
    book['upc'] = response.xpath('//th[text()="UPC"]/following-sibling::td/text()').get()
    book['availability'] = response.xpath('//th[text()="Availability"]/following-sibling::td/text()').get()
    book['tax'] = response.xpath('//th[text()="Tax"]/following-sibling::td/text()').get()

    # breadcrumb: Home > Books > <카테고리>
    book['category'] = response.css('ul.breadcrumb li:nth-child(3) a::text').get()

    # class="star-rating Three" -> '3'
    star_class = response.css('p.star-rating::attr(class)').get('')
    book['stars'] = number_dict.get(star_class.split(' ')[-1])

    image_src = response.css('div.active img::attr(src)').get()
    book['image_url'] = response.urljoin(image_src) if image_src else None

    return book


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response):
        book_links = response.css('article.product_pod h3 a::attr(href)').getall()
        for book_link in book_links:
            yield response.follow(book_link, callback=self.parse_books)

        next_page_link = response.css('li.next a::attr(href)').get()

        if next_page_link is not None:
            yield response.follow(next_page_link, callback=self.parse)

    def parse_books(self, response):
        yield parse_book(response)
