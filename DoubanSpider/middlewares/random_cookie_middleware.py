import random
import string


class RandomCookieMiddleware(object):
    """
    Custom cookie middleware  for crawling douban site.
    """
    @property
    def random_bid(self):
        return ''.join(random.sample(string.ascii_letters + string.digits, 11))

    def process_request(self, request, spider):
        request.cookies.setdefault('bid', self.random_bid)
