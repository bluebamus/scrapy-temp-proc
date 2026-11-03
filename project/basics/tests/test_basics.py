# 실행: cd project/basics && python -m unittest discover -s tests
import logging
import unittest

from scrapy.exceptions import DropItem, NotConfigured
from scrapy.http import HtmlResponse, Request
from scrapy.utils.test import get_crawler

from basics.items import BookItem
from basics.middlewares import RotateUserAgentAndProxyMiddleware
from basics.pipelines import BasicsPipeline, DropperPipeline
from basics.spiders.book import parse_book

BOOK_URL = 'https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'
BOOK_HTML = b'''<html><body>
<ul class="breadcrumb"><li><a href="/">Home</a></li><li><a href="/b">Books</a></li>
<li><a href="/c">Poetry</a></li><li class="active">A Light in the Attic</li></ul>
<div class="product_main"><h1>A Light in the Attic</h1>
<p class="star-rating Three"></p></div>
<div class="item active"><img src="../../media/cache/fe/72/x.jpg"></div>
<table><tr><th>UPC</th><td>a897fe39b1053632</td></tr>
<tr><th>Price (excl. tax)</th><td>\xc2\xa351.77</td></tr>
<tr><th>Price (incl. tax)</th><td>\xc2\xa351.77</td></tr>
<tr><th>Tax</th><td>\xc2\xa30.00</td></tr>
<tr><th>Availability</th><td>In stock (22 available)</td></tr></table>
</body></html>'''


def book(**fields):
    item = BookItem(name='x', price_exc_tax='£1', price_inc_tax='£1', tax='£0',
                    availability='In stock (22 available)')
    item.update(fields)
    return item


class ParseBookTest(unittest.TestCase):
    def test_full_page(self):
        item = parse_book(HtmlResponse(BOOK_URL, body=BOOK_HTML))
        self.assertEqual(item['name'], 'A Light in the Attic')
        self.assertEqual(item['category'], 'Poetry')
        self.assertEqual(item['stars'], '3')
        self.assertEqual(item['upc'], 'a897fe39b1053632')
        self.assertEqual(item['image_url'], 'https://books.toscrape.com/media/cache/fe/72/x.jpg')

    def test_empty_page_does_not_crash(self):
        item = parse_book(HtmlResponse(BOOK_URL, body=b'<html></html>'))
        self.assertIsNone(item['category'])
        self.assertIsNone(item['stars'])
        self.assertIsNone(item['image_url'])


class PipelineTest(unittest.TestCase):
    def test_basics_normalizes(self):
        item = BasicsPipeline().process_item(book(), None)
        self.assertEqual(item['name'], 'X')
        self.assertEqual(item['availability'], '22')
        self.assertEqual(item['price_exc_tax'], '$1')

    def test_basics_handles_missing_values(self):
        item = BasicsPipeline().process_item(book(name=None, tax=None, availability=None), None)
        self.assertEqual(item['availability'], '0')

    def test_dropper(self):
        self.assertEqual(DropperPipeline().process_item(book(), None)['availability'], '22')
        with self.assertRaises(DropItem):
            DropperPipeline().process_item(book(availability='In stock (3 available)'), None)
        with self.assertRaises(DropItem):
            DropperPipeline().process_item(book(availability=None), None)


class RotateMiddlewareTest(unittest.TestCase):
    def setUp(self):
        crawler = get_crawler(settings_dict={'USER_AGENT_LIST': ['ua'], 'PROXY_LIST': ['http://p:1'],
                                             'ROTATE_MAX_RETRIES': 2})
        self.mw = RotateUserAgentAndProxyMiddleware.from_crawler(crawler)
        self.spider = type('S', (), {'logger': logging.getLogger('test')})()

    def test_empty_lists_disable(self):
        with self.assertRaises(NotConfigured):
            RotateUserAgentAndProxyMiddleware.from_crawler(get_crawler())

    def test_retry_is_capped(self):
        request = Request('https://example.com')
        response = HtmlResponse(request.url, status=404, request=request)
        for _ in range(2):
            request = self.mw.process_response(request, response, self.spider)
            self.assertIsInstance(request, Request)
        self.assertIs(self.mw.process_response(request, response, self.spider), response)
        self.assertIsNone(self.mw.process_exception(request, Exception('x'), self.spider))


if __name__ == '__main__':
    unittest.main()
