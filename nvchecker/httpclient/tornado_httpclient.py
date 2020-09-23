# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import json as _json
from urllib.parse import urlencode
from typing import Optional, Dict, Any

from tornado.httpclient import AsyncHTTPClient, HTTPRequest

try:
  import pycurl
  AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient", max_clients=20)
except ImportError:
  pycurl = None # type: ignore

from .base import BaseSession, TemporaryError, Response

__all__ = ['session']

HTTP2_AVAILABLE = None if pycurl else False

def try_use_http2(curl):
  global HTTP2_AVAILABLE
  if HTTP2_AVAILABLE is None:
    try:
      curl.setopt(pycurl.HTTP_VERSION, 4)
      HTTP2_AVAILABLE = True
    except pycurl.error:
      HTTP2_AVAILABLE = False
  elif HTTP2_AVAILABLE:
    curl.setopt(pycurl.HTTP_VERSION, 4)

class TornadoSession(BaseSession):
  async def request_impl(
    self, url: str, *,
    method: str,
    proxy: Optional[str] = None,
    headers: Dict[str, str] = {},
    params = (),
    json = None,
    body = None,
  ) -> Response:
    kwargs: Dict[str, Any] = {
      'method': method,
      'headers': headers,
    }

    if json:
      kwargs['body'] = _json.dumps(json)
    if body:
      kwargs['body'] = body
    kwargs['prepare_curl_callback'] = try_use_http2

    if proxy:
      host, port = proxy.rsplit(':', 1)
      kwargs['proxy_host'] = host
      kwargs['proxy_port'] = int(port)

    if params:
      q = urlencode(params)
      url += '?' + q

    r = HTTPRequest(url, **kwargs)
    res = await AsyncHTTPClient().fetch(
      r, raise_error=False)
    if res.code >= 500:
      raise TemporaryError(
        res.code, res.reason, res
      )
    else:
      res.rethrow()

    return Response(res.body)

session = TornadoSession()
