import os
import yaml
from resteasy import requests, APIEndpoint

from resteasycli.config import Config
from resteasycli.exceptions import MethodNotAllowedException


requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning)


class Endpoint(object):
    '''Holds endpoint of a site'''

    def __init__(self, endpoint_id, site, slug=None):
        data = site.endpoints[endpoint_id]
        self.endpoint_id = endpoint_id
        self.site = site
        self.logger = site.logger
        self.auth_applied = None
        self.headers_applied = None
        self.timeout_applied = None
        self.verify_applied = None
        self.allowed_methods = Config.DEFAULT_ALLOWED_METHODS
        self.api = APIEndpoint(endpoint=('{}/{}'.format(site.base_url, data['route'])),
                session=site.session,
                timeout=site.timeout, debug=site.debug)
        if slug is not None:
            self.api = self.api.route(slug)
        if 'auth' in data:
            self.auth_applied = site.workspace.get_auth(data['auth'])
            self.auth_applied.apply(self.api.session)
        if 'headers' in data:
            self.headers_applied = site.workspace.get_headers(data['headers'])
            self.headers_applied.apply(self.api.session)
        if 'timeout' in data:
            self.timeout_applied = data['timeout']
            self.api.timeout = data['timeout']
        if 'verify' in data:
            self.verify_applied = data['verify']
            self.api.session.verify = data['verify']
        if 'methods' in data:
            self.allowed_methods = list(
                map(lambda x: x.upper(), data['methods']))
            self.allowed_methods_applied = self.allowed_methods

    def do(self, method, kwargs={}):
        '''Do the request'''

        if method not in self.allowed_methods:
            raise MethodNotAllowedException('allowed methods are: ' + (', '.join(self.allowed_methods)))

        return self.api.do(method, kwargs)
