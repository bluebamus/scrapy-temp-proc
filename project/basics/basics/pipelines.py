# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import openpyxl
import re
import sqlite3


def _stock(adapter):
    # "In stock (22 available)" -> 22, 형식이 다르거나 값이 없으면 0
    match = re.search(r'\((\d+) available\)', adapter.get('availability') or '')
    return int(match.group(1)) if match else 0


def _normalize(adapter):
    adapter['availability'] = str(_stock(adapter))
    for field in ('price_exc_tax', 'price_inc_tax', 'tax'):
        if adapter.get(field):
            adapter[field] = adapter[field].replace('£', '$')


class BasicsPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter.get('name'):
            adapter['name'] = adapter['name'].upper()
        _normalize(adapter)
        return item

class DropperPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if _stock(adapter) < 10:
            raise DropItem(f'Not enough stock for {adapter.get("name")}')
        _normalize(adapter)
        return item

class ExcelPipeline:
    def open_spider(self, spider):
        self.workbook = openpyxl.Workbook()
        self.sheet = self.workbook.active
        self.sheet.title = 'Books'
        self.sheet.append(["name", "price_exc_tax", "price_inc_tax",
                           "category", "stars", "upc", "tax", "availability",
                           "image_url"])

    def process_item(self, item, spider):
        self.sheet.append([item.get('name'),
                           item.get('price_exc_tax'),
                           item.get('price_inc_tax'),
                           item.get('category'),
                           item.get('stars'),
                           item.get('upc'),
                           item.get('tax'),
                           item.get('availability'),
                           item.get('image_url'),
                           ])
        return item

    def close_spider(self, spider):
        self.workbook.save('books_.xlsx')


class SQLitePipeline:

    def open_spider(self, spider):
        self.connection = sqlite3.connect("bookdatabase.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS booktable (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                price_exc_tax TEXT,
                price_inc_tax TEXT,
                category TEXT,
                stars TEXT,
                upc TEXT,
                tax TEXT,
                availability TEXT,
                image_url TEXT
            )
        ''')
        self.connection.commit()

    def process_item(self, item, spider):
        self.cursor.execute('''
            INSERT INTO booktable (
                name, price_exc_tax, price_inc_tax, category, stars, upc, tax, availability, image_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item['name'],
            item['price_exc_tax'],
            item['price_inc_tax'],
            item['category'],
            item['stars'],
            item['upc'],
            item['tax'],
            item['availability'],
            item['image_url']
        ))
        self.connection.commit()
        return item

    def close_spider(self, spider):
        self.connection.close()





