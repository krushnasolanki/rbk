import json
import urllib.parse
import urllib.request
from urllib.error import HTTPError

from util import constants


class APIClient:

    def __init__(self, context, host, port, timeout=constants.API_TIMEOUT_SECONDS):
        self.context = context
        self.host = host
        self.port = port
        self.timeout = timeout
        self.active_request = None
        urllib.request.HTTPSHandler(debuglevel=1)

    def request(self, method, url, headers, body=None):
        self.active_request = urllib.request.Request(url=f"https://{self.host}{url}", headers=headers, method=method)
        content_type = headers.get('content-type', headers.get("Content-Type"))
        if method == "POST":
            if "form" in content_type:
                post_body = urllib.parse.urlencode(body).encode(constants.DEFAULT_CHARACTER_ENCODING)
            else:
                post_body = json.dumps(body).encode(constants.DEFAULT_CHARACTER_ENCODING)
            self.active_request.data = post_body

    def getresponse(self):
        try:
            if constants.EXTRA_LOGGING is True:
                handler = urllib.request.HTTPSHandler(debuglevel=20, context=self.context)
                opener = urllib.request.build_opener(handler)
                resp = opener.open(self.active_request, timeout=self.timeout)
            else:
                resp = urllib.request.urlopen(self.active_request, context=self.context, timeout=self.timeout)
        except HTTPError as err:
            resp = err
        except Exception as ex:
            raise ex
        return resp

    def close(self):
        pass
