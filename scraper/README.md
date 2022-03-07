Introduction
============

This is a firmware scraper that aims to download firmware images and associated
metadata from supported device vendor websites. The original version is designed by https://github.com/firmadyne/scraper. The spiders are extended and updated.

Dependencies
============
* [psycopg2](http://initd.org/psycopg/)
* [scrapy](http://scrapy.org/)

Usage
=====

To run a specific scraper, e.g. `dlink`:

`scrapy crawl dlink`

To run all scrapers with maximum 4 in parallel, using [GNU Parallel](https://www.gnu.org/software/parallel/):

The scriper is not fully tested when running in parallel. 
```parallel -j 4 scrapy crawl ::: `for i in ./firmware/spiders/*.py; do basename ${i%.*}; done` ```
