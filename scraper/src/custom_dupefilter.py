from scrapy.dupefilters import *
from scrapy.utils.request import *
import re

_fingerprint_cache = weakref.WeakKeyDictionary()
class CustomDupeFilter(RFPDupeFilter):
    def request_fingerprint(self, request):
        return self.custom_request_fingerprint(request)

    def custom_request_fingerprint(self, request, include_headers=None):
        """
        Return the request fingerprint.
        The request fingerprint is a hash that uniquely identifies the resource the
        request points to. For example, take the following two urls:
        http://www.example.com/query?id=111&cat=222
        http://www.example.com/query?cat=222&id=111
        Even though those are two different URLs both point to the same resource
        and are equivalent (ie. they should return the same response).
        Another example are cookies used to store session ids. Suppose the
        following page is only accesible to authenticated users:
        http://www.example.com/members/offers.html
        Lot of sites use a cookie to store the session id, which adds a random
        component to the HTTP Request and thus should be ignored when calculating
        the fingerprint.
        For this reason, request headers are ignored by default when calculating
        the fingeprint. If you want to include specific headers use the
        include_headers argument, which is a list of Request headers to include.
        """
        scheme_regex=r'(https?)(.*)'
        canonical_with_no_scheme_url=re.sub(scheme_regex, r"https?\2", canonicalize_url(request.url))


        if include_headers:
            include_headers = tuple(to_bytes(h.lower())
                                    for h in sorted(include_headers))
        cache = _fingerprint_cache.setdefault(request, {})
        if include_headers not in cache:
            fp = hashlib.sha1()
            fp.update(to_bytes(request.method))
            fp.update(to_bytes(canonical_with_no_scheme_url))
            fp.update(request.body or b'')
            if include_headers:
                for hdr in include_headers:
                    if hdr in request.headers:
                        fp.update(hdr)
                        for v in request.headers.getlist(hdr):
                            fp.update(v)
            cache[include_headers] = fp.hexdigest()
        # print cache[include_headers]
        # print type(canonicalize_url(request.url))
        # print re.sub(scheme_regex, r"https?\2", canonicalize_url(request.url))
        # print request.body
        return cache[include_headers]