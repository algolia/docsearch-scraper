CONFIG_SCHEMA = {
    'index_name': {
        'type': 'string',
        'required': True,
        'empty': False
    },
    'allowed_domains': {
        'type': ['string', 'list'],
        'required': False
    },
    'custom_settings': {
        'type': 'dict',
        'required': False
    },
    'js_wait': {
        'type': 'integer',
        'required': False
    },
    'js_render': {
        'type': 'boolean',
        'required': False
    },
    'min_indexed_level': {
        'type': 'integer',
        'required': False
    },
    'remove_get_params': {
        'type': 'boolean',
        'required': False
    },
    'scrape_start_urls': {
        'type': 'boolean',
        'required': False
    },
    'selectors': {
        'type': 'dict',
        'required': True,
        'empty': False,
        'schema': {
            'lvl0': {
                'type': ['string', 'dict']
            },
            'lvl1': {
                'type': ['string', 'dict']
            },
            'lvl2': {
                'type': ['string', 'dict']
            },
            'lvl3': {
                'type': ['string', 'dict']
            },
            'lvl4': {
                'type': ['string', 'dict']
            },
            'lvl5': {
                'type': ['string', 'dict']
            },
            'text': {
                'type': ['string', 'dict']
            }
        }
    },
    'selectors_exclude': {
        'type': 'list',
        'required': False
    },
    'start_urls': {
        'type': ['string', 'list'],
        'required': True,
        'empty': False,
    },
    'stop_urls': {
        'type': 'list',
        'required': False
    },
    'strict_redirect': {
        'type': 'boolean',
        'required': False
    },
    'strip_chars': {
        'type': 'string',
        'required': False
    },
    'use_anchors': {
        'type': 'boolean',
        'required': False
    },
    'sitemap_urls': {
        'type': 'list',
        'required': False
    },
    'sitemap_urls_regexs': {
        'type': 'list',
        'required': False,
        'dependencies': 'sitemap_urls'
    },
    'force_sitemap_urls_crawling': {
        'type': 'boolean',
        'required': False,
        'dependencies': 'sitemap_urls'
    },
    'nb_hits_max': {
        'type': 'integer',
        'required': False
    }
}
