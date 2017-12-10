'''
- This File invokes uses Scrapy module to crawl the webpage - https://www.goodreads.com/search?q=authors
- Extracts contents of the webpage and Generates a CSV file

Author: Bala Vineeth Netha Thatipamula
'''

import scrapy
from scrapy.http import FormRequest
from unidecode import unidecode

class ContentSpider(scrapy.Spider):
    name = "content_spider"
    start_urls = [
        'https://www.goodreads.com/user/sign_in',
    ]
    authors_url = 'https://www.goodreads.com/search?q=authors'

    def __init__(self, *args, **kwargs):
        super(ContentSpider, self).__init__(*args, **kwargs)

    def parse(self,response):
        return [FormRequest.from_response(response,
                formdata={'user[email]': 'balavnth@gmail.com', 'user[password]': 'Expedia@GoodReads'},
                callback=self.after_login)]

    def after_login(self, response):
        yield response.follow(self.authors_url, callback=self.parse_content)

    def parse_content(self, response):
        bookContents = response.xpath('//tr[@itemtype="http://schema.org/Book"]/td[@width="100%"]')
        for bookContent in bookContents:
            book_name = bookContent.xpath('a[@class="bookTitle"]/span[@itemprop="name"]//text()').extract_first()
            ratings = bookContent.xpath('span[contains(@class, "greyText")]/span[contains(@class, "minirating")]/text()').extract_first().strip().split(' ')
            yield{
                'Book' : book_name.replace(';', ',') if ';' in book_name else book_name,
                'Author' :  bookContent.xpath('span[@itemprop="author"]/a[@class="authorName"]/span[@itemprop="name"]/text()').extract_first(),
                'Avg Rating': ' '.join(ratings[:3]),
                'Ratings' : ' '.join(ratings[4:]),
            }
