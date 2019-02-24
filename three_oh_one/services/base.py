# encoding=utf-8
'''Base class for URL shortener services'''

import datetime
import logging
import re
import sys
import time

from requests.exceptions import ConnectionError

from three_oh_one.client import VERSION
from three_oh_one.client.errors import (UnhandledStatusCode,
                                        UnexpectedNoResult, ScraperError,
                                        PleaseRetry, MalformedResponse)
from three_oh_one.services.status import URLStatus
from html.parser import HTMLParser


__all__ = ['BaseService', 'registry']
DEFAULT_USER_AGENT = (
    'URLTeam TerrorOfTinyTown/{version} (ArchiveTeam; '
    '+http://archiveteam.org/index.php?title=URLTeam/Appeal)'
).format(version=VERSION)


class BaseService(object):
    def __init__(self, params):
        self.params = params
        self.logger = logging.getLogger(self.__class__.__name__)
        self.current_shortcode = None
        self.user_agent = DEFAULT_USER_AGENT
        self.tolerate_missing_location_header = bool(
            self.params.get('location_anti_regex') and \
            re.search(self.params['location_anti_regex'], ''))

    def prepare(self):
        pass

    def wait(self):
        sleep_time = self.params['request_delay']
        time.sleep(sleep_time)

    def scrape_one(self, shortcode):
        self.current_shortcode = shortcode
        url = self.params['url_template'].format(shortcode=shortcode)

        self.logger.info('Requesting %s', url)

        response = self.fetch_url(url)
        url_status, result_url, encoding = self.process_response(response)

        if url_status == URLStatus.ok:
            assert result_url is not None
            self.logger.info('Got a result.')
            self.logger.debug('%s %s', result_url, response.encoding)

            return {
                'shortcode': shortcode,
                'url': result_url,
                'encoding': encoding or 'latin-1'
            }

    def fetch_url(self, url, method=None):
        # this import is moved here so that tracker can import
        # registry without installing requests
        import requests

        assert method in (None, 'get', 'head'), method

        headers = {
            'User-Agent': self.user_agent,
        }

        try:
            if method == 'get' or self.params['method'] == 'get':
                response = requests.get(
                    url, allow_redirects=False, headers=headers, timeout=60)
            else:
                response = requests.head(
                    url, allow_redirects=False, headers=headers, timeout=60)
        except ConnectionError as e:
            return self.process_connection_error(e)

        return response

    def process_response(self, response):
        status_code = response.status_code

        if status_code in self.params['redirect_codes']:
            return self.process_redirect(response)
        elif status_code in self.params['no_redirect_codes']:
            return self.process_no_redirect(response)
        elif status_code in self.params['unavailable_codes']:
            return self.process_unavailable(response)
        elif status_code in self.params['banned_codes']:
            return self.process_banned(response)
        else:
            return self.process_unknown_code(response)

    def process_redirect(self, response):
        if 'Location' in response.headers:
            result_url = response.headers['Location']

            if sys.version_info[0] == 2 and \
                    isinstance(result_url, binary_type):
                # Headers are treated as latin-1
                # This is needed so that unit tests don't need to
                # do implicit unicode conversion. Ick!
                result_url = result_url.decode('latin-1')

            response.content  # read the response to allow connection reuse
            return self.check_anti_regex(response, result_url, None)
        elif self.params.get('body_regex'):
            return self.process_redirect_body(response)
        elif self.tolerate_missing_location_header:
            response.content  # read the response to allow connection reuse
            return self.process_no_redirect(response)
        else:
            response.content  # read the response to allow connection reuse

            raise UnexpectedNoResult(
                'Unexpectedly did not get a redirect result for {0}'
                .format(repr(response.url))
            )

    def process_redirect_body(self, response):
        pattern = self.params['body_regex']
        match = re.search(pattern, html_unescape(response.text))

        if match:
            return self.check_anti_regex(response, match.group(1), response.encoding)
        else:
            raise UnexpectedNoResult(
                'Unexpectedly did not get a body result for {0}'
                .format(repr(response.url))
            )

    def process_no_redirect(self, response):
        return (URLStatus.not_found, None, None)

    def process_unavailable(self, response):
        return (URLStatus.unavailable, None, None)

    def process_banned(self, response):
        raise PleaseRetry('Server said: {0}'.format(repr(response.reason)))

    def process_unknown_code(self, response):
        raise UnhandledStatusCode(
            'Unknown status code {0} for {1}'.format(response.status_code,
                                                     repr(response.url))
        )

    def process_connection_error(self, exception):
        if 'ProtocolError' in repr(exception.args):
            raise MalformedResponse(
                'Malformed response: {0}'.format(repr(exception.args)))
        else:
            raise PleaseRetry('Connection error: {0}'.format(repr(exception.args)))

    def check_anti_regex(self, response, result_url, encoding):
        if not result_url or self.matches_anti_regex(result_url):
            return self.process_no_redirect(response)
        else:
            return (URLStatus.ok, result_url, encoding)

    def matches_anti_regex(self, result_url):
        anti_regex = self.params.get('location_anti_regex')
        return (anti_regex and re.search(anti_regex, result_url))


class DefaultService(BaseService):
    pass


_html_parser_unescaper = HTMLParser()


def html_unescape(text):
    return _html_parser_unescaper.unescape(text)
