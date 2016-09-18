"""

    Searches nyt API for articles related to climate change and returns them.
    API returns pages, each page has 10 articles. This currently only returns one page.
    Cannot specify how many articles per page in api.
    get_trending function returns articles for the past 3 days.

"""

from nytimesarticle import articleAPI
from datetime import datetime, timedelta
import random


class NytimesApi(object):
    def __init__(self, key):
        self.api = articleAPI(key)
        self.secret_keyword = "sustainable and "
        self.num_days_trending = 3

    def return_all(self, query):
        """
            Keep query as is if climate change is in the query
            If not, add climate change
        """

        if 'climate change' in query:
            return self.api.search(q=query)
        return self.api.search(q=self.secret_keyword + query)

    def return_trending(self):
        """
            NYT API only accepts dates that are of format: YYYYMMDD
        """
        first_date = datetime.today() - timedelta(self.num_days_trending)
        first_date = first_date.strftime("%Y%m%d")
        return self.api.search(q=self.secret_keyword, begin_date=first_date)

    def return_content(self, res):
        article = {}
        article['title'] = res['headline']['main']
        article['abstract'] = res['abstract']
        article['_id'] = res['_id']
        article['source'] = res['source']
        article['web_url'] = res['web_url']
        if len(res['multimedia']) > 0:
            article['image_url'] = 'http://nytimes.com/' + res['multimedia'][0]['url']
        article['date'] = res['pub_date']
        return article

    def clean_response(self, results, num, randomize=False):
        articles = []
        idx = 0
        for doc in results['response']['docs']:
            if doc['abstract'] is None:
                doc['abstract'] = doc['lead_paragraph']
            else:
                continue
            articles.append(self.return_content(doc))
            idx += 1
            if idx == num:
                break
        if randomize:
            random.shuffle(articles)
        return articles

    def return_article_list(self, query, num=1, randomize=False):
        results = self.return_all(query)
        articles = self.clean_response(results, num, randomize)
        return articles

    def return_trending_list(self, num=6, randomize=False):
        results = self.return_trending()
        articles = self.clean_response(results, num, randomize)
        return articles
