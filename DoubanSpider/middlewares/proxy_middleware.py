import logging
import requests
import json
import random

from scrapy.exceptions import IgnoreRequest
from twisted.internet.error import ConnectionRefusedError, ConnectError, TimeoutError, TCPTimedOutError


class ProxyMiddleware(object):
    """
    Custom proxy middleware.
    """
    proxy_list = []
    proxy_api = []
    cache_counter = 1
    proxy_pool_cache_timeout = 400
    proxy_obj = None

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        if not cls.proxy_obj:
            cls.proxy_api = settings.get('PROXY_API', None)
            cls.proxy_pool_cache_timeout = settings.get('PROXY_POOL_CACHE_TIMEOUT', 400)
            cls.get_proxy_list(cls.proxy_api)
        return cls()

    @classmethod
    def get_proxy_list(cls, proxy_api):
        resp = requests.get('{host}/?types=0&country=国内'.format(host=proxy_api))
        try:
            cls.proxy_list = json.loads(resp.text)
        except Exception as e:
            logging.warn(e)

    @classmethod
    def delete_proxy(cls, proxy):
        ip = proxy.split(':')[0]
        if ip:
            requests.get('{host}/delete?ip={ip}'.format(host=cls.proxy_api, ip=ip))
            cls.update_proxy()

    @classmethod
    def update_proxy(cls):
        cls.cache_counter = 1
        cls.get_proxy_list(cls.proxy_api)

    @classmethod
    def set_request_with_proxy(cls, request):
        if len(cls.proxy_list) == 0:
            return request
        selected_proxy = random.choice(ProxyMiddleware.proxy_list)
        request.meta['proxy'] = 'http://{ip}:{port}'.format(ip=selected_proxy[0], port=selected_proxy[1])
        # Change proxy and retry in the future
        return request

    def process_request(self, request, spider):
        ProxyMiddleware.cache_counter += 1
        ProxyMiddleware.set_request_with_proxy(request)
        if ProxyMiddleware.cache_counter % ProxyMiddleware.proxy_pool_cache_timeout == 0:
            ProxyMiddleware.update_proxy()

    def process_response(self, request, response, spider):
        if '检测到有异常请求从你的 IP 发出' in response.text:
            logging.warning('This proxy {proxy} has been banned!'.format(proxy=request.meta['proxy']))
            logging.warning("Will change proxy and rerun in the future.")
            return ProxyMiddleware.set_request_with_proxy(request)
        return response

    def process_exception(self, request, exception, spider):
        if any(map(lambda ex: isinstance(exception, ex), [ConnectionRefusedError, ConnectError, TimeoutError, TCPTimedOutError])):
            if request.meta['proxy']:
                logging.warning('This proxy {proxy} is invalid!'.format(proxy=request.meta['proxy']))
                ProxyMiddleware.delete_proxy(request.meta['proxy'])
            else:
                print('No proxy used.')
            return ProxyMiddleware.set_request_with_proxy(request)
