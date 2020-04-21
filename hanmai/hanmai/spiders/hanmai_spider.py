import scrapy
import re

class HanmaiSpider(scrapy.Spider):
    name = "hanmai"
    key_words = ['词', '曲', '喊麦', '伴奏', '搜索', '\r', 'MC', '演唱']

    def start_requests(self):
        urls = ['http://www.0453dj.com/news/show-{}.html'.format(i) \
            for i in range(4, 3124)]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        content = response \
            .xpath('//*[@class="content"]/*[not(self::a)]//text()').getall()
        filtered_strings = [s for s in content if not any(key_word in s for key_word in self.key_words)]
        break_space_strings = [ns for s in filtered_strings for ns in s.split(' ')]
        stripped_strings = filter(None, [s.strip() for s in break_space_strings])
        only_chinese = filter(lambda item: not bool(re.search('[a-z0-9]+$', item, re.IGNORECASE)),
            list(stripped_strings))
        remove_short_long = filter(lambda item: 20 > len(item) > 2,
            list(only_chinese))
        
        lyrics = '\\n'.join \
            (filter(None, [x.replace(u'\xa0|-', u'') for x in remove_short_long]))

        if '请谨记以下注意事项' not in lyrics and lyrics:
            with open('a.json', 'a+') as f:
                    f.write('["' + lyrics + '"]\n')
            self.log('Saved file')
        
        yield {'content': lyrics}
