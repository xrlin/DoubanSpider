import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.shell import inspect_response

from DoubanSpider.items import Movie, MovieLoader


class MoviesSpider(scrapy.Spider):
    name = 'movies_spider'
    allowed_domains = ['movie.douban.com']
    start_urls = ['https://movie.douban.com/tag/?view=cloud']

    def parse(self, response):
        """
        爬取标签列表
        :param response:
        :return:
        """
        for link in LinkExtractor(allow=('tag/.+',), deny=('tag/\?.*',)).extract_links(response):
            yield scrapy.Request(link.url, self.parse_movies_with_tag)

    def parse_movies_with_tag(self, response):
        """
        爬取标签下的电影列表
        :param response:
        :return:
        """
        next_page_link = response.css('#content > div > div.article > div.paginator > span.next > a')\
            .xpath('@href').extract_first()

        for movie_link in LinkExtractor(allow=('subject/\d+/')).extract_links(response):
            yield scrapy.Request(movie_link.url, self.parse_movie_detail)

        if next_page_link:
            yield scrapy.Request(next_page_link, self.parse_movies_with_tag)

    def parse_movie_detail(self, response):
        """
        爬取电影详情
        :param response:
        :return:
        """
        movie_loader = MovieLoader(item=Movie(), response=response)
        movie_loader.add_value('url', response.url)
        movie_loader.add_css('actors', 'span.actor')
        movie_loader.add_css('name', '#content > h1 > span:nth-child(1)::text')
        movie_loader.add_css('rate', 'strong.rating_num::text')
        movie_loader.add_css('screenwriters', '#info > span:nth-child(3) > span.attrs > a::text')
        movie_loader.add_css('directors', '#info > span:nth-child(1) > span.attrs')
        movie_loader.add_css('genre', 'span[property="v:genre"]::text')
        movie_loader.add_xpath('language', '//*[@id="info"]/span[text()="语言:"]/following::text()[1]')
        movie_loader.add_css('release_date', 'span[property="v:initialReleaseDate"]::text')
        movie_loader.add_xpath('length', '//span[@property="v:runtime"]/@content')
        yield movie_loader.load_item()

    def parse_item(self, response):
        # i = {}
        #i['domain_id'] = response.xpath('//input[@id="sid"]/@value').extract()
        #i['name'] = response.xpath('//div[@id="name"]').extract()
        #i['description'] = response.xpath('//div[@id="description"]').extract()
        print(response.headers)
        # print(response.xpanth('//*[@id="content"]/h1/span[1]').extract_first())
