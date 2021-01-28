import scrapy
from scrapy_splash import SplashRequest

class PacotesSpider(scrapy.Spider):
    name = 'packages'
    allowed_domains = ['www.hurb.com']

    script1 = '''
        function main(splash, args)
            splash.private_mode_enabled = false
            assert(splash:go(args.url))
            assert(splash:wait(2))
            splash:set_viewport_full()
            return splash:html()
        end
    '''

    script2 = '''
        function main(splash, args)
            assert(splash:go(args.url))
            assert(splash:wait(2))
            cookies_btn = splash:select('a.c-button')
            assert(splash:wait(1))
            cookies_btn:mouse_click()
            splash:set_viewport_full()
            return {
                html = splash:html(),
                png = splash:png(),
            }
        end
    '''

    def start_requests(self):
        yield SplashRequest(
            url=f'https://www.hurb.com/br/search/packages?q=2021&tab=packages&departureCities=departurecity_{self.city}',
            callback=self.parse_links, endpoint="execute", args={
                'lua_source': self.script1
            }
        )
    
    def parse_links(self, response):
        links = response.xpath("//main//div/a/@href").getall()
        for link in links:
            yield SplashRequest(
                url=link,
                callback=self.parse_pack,
                endpoint="execute",
                args={
                    'lua_source': self.script2
                }
            )
    
    def parse_pack(self, response):
        yield {
            'from': self.city,
            'to': response.xpath('normalize-space(//section/span/h2/text())').get(),
            'name': response.xpath("normalize-space((//div[@class='row filter-description']//following-sibling::div[@style='display: block;'][1]//span/text())[1])").get(),
            'promotion-price': response.xpath("//div[@class='promotion-price-box']/span[2]/text()").get(),
            'details': response.xpath('normalize-space(//span[@itemprop]/text())').get(),
            'min-days': response.xpath("normalize-space(//div[@class='daily-container']//span[@class='number-daily'][1]/text())").get(),
            'max-days': response.xpath("normalize-space(//div[@class='daily-container']//span[@class='number-daily'][2]/text())").get(),
            'date_1': response.xpath("(//div[@class='formated-date']/@data-date)[1]").get(),
            'date_2': response.xpath("(//div[@class='formated-date']/@data-date)[2]").get(),
            'url': response.url,
            'user-agent': response.request.headers.get('User-Agent').decode('utf-8')
        }
