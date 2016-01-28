import scrapy.utils.request

# patching scrappy to avoid canonalizing urls in the reactor
def request_fingerprint_non_canonicalize(request, include_headers=None):
    if include_headers:
        include_headers = tuple([h.lower() for h in sorted(include_headers)])
    cache = scrapy.utils.request._fingerprint_cache.setdefault(request, {})
    if include_headers not in cache:
        fp = scrapy.utils.request.hashlib.sha1()
        fp.update(request.method)
        fp.update(request.url)
        fp.update(request.body or '')
        if include_headers:
            for hdr in include_headers:
                if hdr in request.headers:
                    fp.update(hdr)
                    for v in request.headers.getlist(hdr):
                        fp.update(v)
        cache[include_headers] = fp.hexdigest()
    return cache[include_headers]


scrapy.utils.request.request_fingerprint = request_fingerprint_non_canonicalize