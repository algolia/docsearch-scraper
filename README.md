# DocSearch scraper

This repository holds the code of the DocSearch crawler used to power the hosted
version of DocSearch.

If you're looking for a way to add DocSearch to your site, the easiest solution
is to [apply to DocSearch][1]. If you want to run the crawler yourself, you're
at the right place.

## Installation and Usage

Please check the [dedicated documentation ][2] to see how you can install and
run DocSearch yourself: https://community.algolia.com/docsearch/run-your-own.html

## Related projects

DocSearch is made of 3 repositories:

- [algolia/docsearch][3] contains the `docsearch.js` code source and the
  documentation website.
- [algolia/docsearch-configs][4] contains the JSON files representing all the
  configs for all the documentations DocSearch is powering
- [algolia/docsearch-scraper][5] contains the crawler we use to extract data
  from your documentation. The code is open-source and you can run it from
  a Docker image


[1]: https://community.algolia.com/docsearch/
[2]: https://community.algolia.com/docsearch/run-your-own.html
[3]: https://github.com/algolia/docsearch
[4]: https://github.com/algolia/docsearch-configs
[5]: https://github.com/algolia/docsearch-scraper
