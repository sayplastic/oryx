#!/usr/bin/env python
# encoding=utf-8

import os
import sys
import flask
from flask import Flask, after_this_request, abort, request, url_for, current_app
from jinja2 import Environment, PackageLoader

from parsers import Feed


app = Flask(__name__)


class Config(object):
    DEBUG = True
    TESTING = True
    SERVER_PORT = 8110
    # SERVER_NAME = 'localhost'


class ProductionConfig(object):
    DEBUG = False
    TESTING = False
    SERVER_PORT = 8110
    # SERVER_NAME = 'oryx.vr2.net'


config_object = ProductionConfig if 'PRODUCTION' in os.environ else Config
app.config.from_object(config_object)


prev_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not prev_dir in sys.path:
    sys.path.append(prev_dir)

env = Environment(loader=PackageLoader('oryx', 'templates'))

feeds = {
    'macalope': Feed('http://www.macworld.com/author/The-Macalope/', {
        'links': 'div.landing-listing > div.excerpt > a',
        'title': 'article h1',
        'body': 'article section.page',
        'date': 'article .article-meta [itemprop="datePublished"]',
        'author': 'article .author-name span'
    }, title='The Macalope')
}


@app.route('/favicon.ico')
def favicon():
    return flask.send_file('static/oryx.jpg')


@app.route('/<site_name>/')
def feed(site_name):
    @after_this_request
    def add_header(response):
        response.headers['Content-type'] = 'application/atom+xml'
        return response

    try:
        feed = feeds[site_name]
    except KeyError:
        abort(404)

    template = env.get_template('atom.xml')
    return template.render(
        site_title=feed.title, site_url=request.url_root, feed_url=request.base_url,
        updated=feed.updated, articles=feed.fetch(), feed_id=request.base_url
    )

# with app.app_context():
#     app.add_url_rule('/favicon.ico',
#                      redirect_to=url_for('static', filename='oryx.jpg'))


if __name__ == "__main__":
    app.run(port=app.config.get('SERVER_PORT'), debug=app.config.get('DEBUG'))
