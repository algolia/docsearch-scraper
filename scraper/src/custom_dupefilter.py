from scrapy.dupefilters import RFPDupeFilter
from scrapy.utils.job import job_dir
from w3lib.url import canonicalize_url
from scrapy.utils.python import to_bytes
import weakref
import hashlib
import re

_fingerprint_cache = weakref.WeakKeyDictionary()


class CustomDupeFilter(RFPDupeFilter):
    def request_fingerprint(self, request, remove_scheme=None):
        return self.custom_request_fingerprint(request, remove_scheme=remove_scheme)

    def custom_request_fingerprint(self, request, include_headers=None, remove_scheme=None):
        """
        Overriden given that some URL can have a wrong encoding (when it is comes from selenium driver) changes: encode.('utf-8) & in order to be no scheme compliant
        """
        #

        # If use_anchors, anchors in URL matters since each anchor define a different webpage and content (special js_rendering)
        url_for_finger_print = canonicalize_url(request.url) if not self.use_anchors else request.url
        url_for_hash = url_for_finger_print.encode('utf-8')

        # no scheme compliant
        if remove_scheme:
            match_capture_any_scheme = r'(https?)(.*)'
            url_with_no_scheme = re.sub(match_capture_any_scheme, r"\2", url_for_finger_print)
            url_for_hash = url_with_no_scheme
        print "url for hash"
        print remove_scheme
        print url_for_hash


        if include_headers:
            include_headers = tuple(to_bytes(h.lower())
                                    for h in sorted(include_headers))
        cache = _fingerprint_cache.setdefault(request, {})
        print "cache"
        print cache
        if include_headers not in cache:
            fp = hashlib.sha1()
            fp.update(to_bytes(request.method.encode('utf-8')))
            fp.update(to_bytes(url_for_hash))
            fp.update(request.body or ''.encode('utf-8'))
            if include_headers:
                for hdr in include_headers:
                    if hdr in request.headers:
                        fp.update(hdr)
                        for v in request.headers.getlist(hdr):
                            fp.update(v)
            cache[include_headers] = fp.hexdigest()
        return cache[include_headers]

    def __init__(self, path=None, debug=False, use_anchors=False):
        super(CustomDupeFilter, self).__init__(path=path, debug=debug)
        # Spread config bool
        self.use_anchors = use_anchors
        self.fingerprints_redirected = set()

    # Overriden method in order to add the use_anchors attribute
    @classmethod
    def from_settings(cls, settings):
        debug = settings.getbool('DUPEFILTER_DEBUG')
        use_anchors = settings.getbool('DUPEFILTER_USE_ANCHORS')
        return cls(job_dir(settings), debug, use_anchors)

    def request_seen(self, request):

        fp = self.request_fingerprint(request, remove_scheme=True)
        #URL from a redirection
        isRedirected=request.meta.get('redirect_times') and request.meta.get('redirect_times') > 0

        if isRedirected:
            print "REDIRECTED"
            print request.url
            fp_scheme_agnostic = self.request_fingerprint(request, remove_scheme=False)
            print fp_scheme_agnostic
            if fp_scheme_agnostic in self.fingerprints_redirected:
                return True
            self.fingerprints_redirected.add(fp_scheme_agnostic)
            #We don't want a direct hyperlink to duplicate the indexes, we keep track of it
            if fp not in self.fingerprints:
                self.register_fingerprint(fp)
        else:
            if fp in self.fingerprints:
                return True
            print fp
            self.register_fingerprint(fp)

    def register_fingerprint(self, fp):
        self.fingerprints.add(fp)
        if self.file:
            self.file.write(fp + os.linesep)
