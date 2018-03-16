__author__ = 'matus'

from elasticsearch_dsl import DocType, Date, Integer, Keyword, Text
from elasticsearch_dsl.connections import connections
from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
import psycopg2


client = connections.create_connection(host='128.199.70.132')
class Article(DocType):
    title = Text(analyzer='thai', fields={'raw': Keyword()})
    body = Text(analyzer='thai')
    tags = Keyword()
    lines = Integer()
    slug = Text
    end_date = Text
    donation_limit = Text
    cover_image = Text

    class Meta:
        index = 'project'

    def save(self, ** kwargs):
        self.lines = len(self.body.split())
        return super(Article, self).save(** kwargs)


def insertDoc(_id,title,tags,slug,end_date, donation_limit, cover_image):
    Article.init()
    article = Article(meta={'id':_id}, title=title, tags=[tags], slug = slug, end_date = end_date, donation_limit = donation_limit, cover_image = cover_image)
    article.body = ''
    k = article.save()
    return k


def insertData():
    try:
        conn = psycopg2.connect("dbname='taejai'")
        cur = conn.cursor()
        cur.execute("""SELECT * from store_donation_donationproject""")
        rows = cur.fetchall()
        print("\nShow me the databases:\n")
        past = str(datetime.now())
        past = past[0:10]
        # print(past)
        for row in rows:
            if(str(row[12]) > past):
    #             print ("   ", row[0],"  ",row[3],"  ",row[7],"  ",row[5],"  ",row[12],"  ",row[17])
                result = a = insertDoc(row[0],row[3],'project',row[5],row[12],row[7],row[17])
                print(result)
    except:
        print("false")

insertData()