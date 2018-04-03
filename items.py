# -*- coding: utf-8 -*-
import scrapy
class autInfoItem(scrapy.Item):
    pass
class weiboItem(scrapy.Item):
    BloggerName = scrapy.Field()
    TimeFlag = scrapy.Field()
    WeiboContent = scrapy.Field()
    WeiboForwards = scrapy.Field()
    WeiboComments = scrapy.Field()
    WeiboLikes = scrapy.Field()

class xmlynewItem(scrapy.Item):
    SoundID = scrapy.Field()
    SoundName = scrapy.Field()
    SoundDir = scrapy.Field()
    AlbumName = scrapy.Field()
    SoundPlayCount = scrapy.Field()

class xmlyItem(scrapy.Item):
    AlbumName = scrapy.Field()
    AlbumInfoHref = scrapy.Field()
    AlbumID = scrapy.Field()
    AlbumCategory = scrapy.Field()
    AlbumTag = scrapy.Field()
    AlbumUpdateDate = scrapy.Field()
    AlbumPlayCount = scrapy.Field()
    AlbumIntro = scrapy.Field()
    SoundInfo = scrapy.Field()

class cnkiItem(scrapy.Item):
    artinfo = scrapy.Field()    

class DmozItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    desc = scrapy.Field()
    
class TestItem(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    description = scrapy.Field()

class TutorialItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

