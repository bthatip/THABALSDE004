import scrapy
from scrapy.http import FormRequest
from unidecode import unidecode

class AuthorSpider(scrapy.Spider):
    name = "author_spider"
    start_urls=['https://www.goodreads.com/user/sign_in',]
    authors_url = 'https://www.goodreads.com/search?q=authors'

    def __init__(self, *args, **kwargs):
        super(AuthorSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        return [FormRequest.from_response(response,
                formdata={'user[email]': 'balavnth@gmail.com', 'user[password]': 'Expedia@GoodReads'},
                callback=self.after_login)]

    def after_login(self, response):
        yield response.follow(self.authors_url, callback=self.parse_content)

    def parse_content(self, response):
        bookContents = response.xpath('//tr[@itemtype="http://schema.org/Book"]/td[@width="100%"]')
        for bookContent in bookContents:
            author_url = bookContent.xpath('span[@itemprop="author"]/a[@class="authorName"]/@href').extract_first()
            yield response.follow(author_url, callback=self.parse_author)

    def parse_author(self, response):
        genres = response.xpath('//div[@class="dataTitle" and ./text()="Genre"]/following-sibling::div[@class="dataItem" and ./a[contains(@href, "genre")]]//text()').extract()
        birth_date = response.xpath('//div[@class="dataItem" and @itemprop="birthDate"]/text()').extract_first()
        death_date = response.xpath('//div[@class="dataItem" and @itemprop="deathDate"]/text()').extract_first()
        yield{
            'Author': response.xpath('//h1[@class="authorName"]/span[@itemprop="name"]/text()').extract_first(),
             'Birth Date' : birth_date if birth_date is None else birth_date.strip(),
             'Death Date' : death_date if death_date is None else death_date.strip(),
             'Genres' : ''.join(genres[1:-1])
        }
