# DocSearch scraper

This repository holds the code of the DocSearch scraper used to power the hosted
version of DocSearch.

If you're looking for a way to add DocSearch to your site, the easiest solution
is to [apply to DocSearch][1]. To run the scraper yourself, you're at the right
place.

## Installation and Usage

Please check the [dedicated documentation][2] to see how you can install and
run DocSearch yourself.

This project supports Python 3.6+

## Related projects

DocSearch is made of 4 repositories:

- [algolia/DocSearch][3] contains the `docsearch.js` code source.
- [algolia/docsearch-configs][4] contains the JSON files representing all the
  configurations for all the documentations DocSearch is powering.
- [algolia/docsearch-scraper][5] contains the scraper we use to extract data
  from your documentation. The code is open source and you can run it from a
  Docker image.
- [algolia/docsearch-website][6] contains the documentation website.

[1]: https://docsearch.algolia.com/
[2]: https://docsearch.algolia.com/docs/legacy/run-your-own/
[3]: https://github.com/algolia/docsearch
[4]: https://github.com/algolia/docsearch-configs
[5]: https://github.com/algolia/docsearch-scraper
[6]: https://github.com/algolia/docsearch-website
