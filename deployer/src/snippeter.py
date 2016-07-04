from __future__ import absolute_import

try:
    import algolia_helper
    import fetchers
except ImportError:
    from . import algolia_helper, fetchers


def _is_automatically_updated(config, attribute):
    for start_url in config['start_urls']:
        if not isinstance(start_url, basestring):
            if 'variables' in start_url:
                for variable in start_url['variables']:
                    if (variable == attribute):
                        if not isinstance(start_url['variables'][variable], list):
                            return True
    return False


def get_email_for_config(config):
    base_template = """\n==============================\nHi there,

Congratulations, your search is now ready!
I've successfully configured the underlying crawler and it will now run every 24h.

You're now a few steps away from having it working on your website:
- Copy the following CSS/JS snippets and add them to your page

<!-- at the end of the HEAD -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/docsearch.js/1/docsearch.min.css" />
<!-- at the end of the BODY -->
<script type="text/javascript" src="https://cdn.jsdelivr.net/docsearch.js/1/docsearch.min.js"></script>
<script type="text/javascript"> docsearch({
  apiKey: '{{API_KEY}}',
  indexName: '{{INDEX_NAME}}',
  inputSelector: '### REPLACE ME ####'{{ALGOLIA_OPTIONS}},
  debug: false // Set debug to true if you want to inspect the dropdown
});
</script>

- Add a search input if you don't have any yet, and update the inputSelector value in the code snippet to a CSS selector that targets your input field.{{FACETS}}
- Optionally customize the look and feel by following the DocSearch documentation (https://community.algolia.com/docsearch/documentation/)

Feel free to get back to us if you have any issues or questions regarding the integration.
We'd also be happy to get your feedback and thoughts about DocSearch - so we can continue to improve it.

Have a nice day :)\n==============================\n"""

    base_facet_template = """\n- Replace ${{CAPITALISE_NAME}} with the {{NAME}} you want to search on.
   The list of possible {{NAME}} {{UPDATED}}.
   So as of today you have: {{VALUES}}\n"""

    base_example_template = "\n  For example if you want the search on {{EXAMPLE_PHRASE}} just specify: 'facetFilters': [{{EXAMPLE_CODE}}]\n"

    facets = algolia_helper.get_facets(config)

    facet_template = ""
    algolia_options = ""

    if facets is not None:
        facet_template = "\n"
        configs, inverted, crawler_ids = fetchers.get_configs_from_website()

        example_phrase = []
        example_code = []
        example_options = []

        for name, values in facets.iteritems():
            keys = values.keys()
            keys.sort()

            if len(keys) > 0:
                updated = "is automatically fetched from your website" if _is_automatically_updated(configs[config], name) else "is harcoded in the config"
                facet_template += base_facet_template.replace('{{NAME}}', name)\
                                                 .replace('{{CAPITALISE_NAME}}', name.upper())\
                                                 .replace("{{UPDATED}}", updated)\
                                                 .replace("{{VALUES}}", ', '.join(keys))

                example_phrase.append('the ' + name + ' "' + keys[0] + '"')
                example_code.append("\"" + name + ":" + keys[0] + "\"")
                example_options.append("\"" + name + ":$" + name.upper() + "\"")

        if len(example_options) > 0:
            algolia_options += "\n  algoliaOptions: { 'facetFilters': ["+ (', '.join(example_options)) +"] }"
            facet_template += base_example_template.replace('{{EXAMPLE_PHRASE}}', ' and '.join(example_phrase))\
                                                   .replace('{{EXAMPLE_CODE}}', ', '.join(example_code))

    api_key = algolia_helper.get_docsearch_key(config)
    api_key = "### REPLACE ME ####" if api_key == 'Not found' else api_key

    template = base_template.replace('{{API_KEY}}', api_key)\
                            .replace('{{INDEX_NAME}}', config)\
                            .replace('{{FACETS}}', facet_template)\
                            .replace('{{ALGOLIA_OPTIONS}}', algolia_options)

    return template
