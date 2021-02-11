import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from hampdenandco.items import Article


class HampdenSpider(scrapy.Spider):
    name = 'hampden'
    start_urls = ['https://www.hampdenandco.com/insights']

    def parse(self, response):
        articles = response.xpath('//div[@class="post"]')
        for article in articles:
            link = article.xpath('.//h4/a/@href').get()
            date = article.xpath('.//div[@class="date"]/text()').get()
            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

    def parse_article(self, response, date):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = datetime.strptime(date.strip(), '%b %d, %Y')
        date = date.strftime('%Y/%m/%d')

        content = response.xpath('//section[@class="content"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[1:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
