# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

try:
  import tornado, pycurl
  # connection reuse, http/2
  which = 'tornado'
except ImportError:
  try:
    import aiohttp
    which = 'aiohttp'
    # connection reuse
  except ImportError:
    try:
      import httpx
      which = 'httpx'
    except ImportError:
      import tornado
      which = 'tornado'
      # fallback

m = __import__('%s_httpclient' % which, globals(), locals(), level=1)
__all__ = m.__all__
for x in __all__:
  globals()[x] = getattr(m, x)

from .base import TemporaryError
