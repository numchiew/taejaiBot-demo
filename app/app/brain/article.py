from elasticsearch_dsl import DocType, Date, Integer, Keyword, Text
from elasticsearch_dsl.connections import connections
from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

client = connections.create_connection(host='128.199.70.132')

class Article(DocType):
    title = Text(analyzer='thai', fields={'raw': Keyword()})
    body = Text(analyzer='thai')
    tags = Keyword()
    lines = Integer()
    slug = Text
    end_date = Text

    class Meta:
        index = 'blog'

    def save(self, ** kwargs):
        self.lines = len(self.body.split())
        return super(Article, self).save(** kwargs)

def insertDoc(_id,title,tags,slug,end_date):
    Article.init()
    article = Article(meta={'id':_id}, title=title, tags=[tags])
    article.body = ''
    article.slug = slug
    article.end_date = end_date
    result = article.save()
    return result

def search(txt):
    s = Search(using=client, index="project").query("match", title = txt)
    response = s.execute()
    return response


