# -*- coding: utf-8 -*-
# Copyright (c) 2018, Anders Lervik.
# Distributed under the LGPLv2.1+ License. See LICENSE for more info.
"""An extension for sphinx for making a blog-like web page."""
import os
import jinja2
from blogpost.blogpostdirective import shorten_text


HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(HERE, 'templates')


def read_template(template_file):
    """Return a jinja2 template from a template file."""
    if template_file is None or not os.path.isfile(template_file):
        template = jinja2.Template('')
    else:
        with open(template_file, 'r') as template_raw:
            template = jinja2.Template(template_raw.read())
    return template


TEMPLATES = {
    'blogpost': {
        'pre': read_template(os.path.join(TEMPLATE_DIR, 'blogpost.html')),
        'post': read_template(None),
    },
    'blogoutput': {
        'pre': read_template(os.path.join(TEMPLATE_DIR, 'blogoutput.html')),
        'post': read_template(None),
    },
    'taglist': {
        'pre': read_template(os.path.join(TEMPLATE_DIR, 'taglist.html')),
        'post': read_template(None),
    },
    'recent': {
        'pre': read_template(os.path.join(TEMPLATE_DIR, 'recent.html')),
        'post': read_template(None),
    },
}


def html_visit_blogpost(self, node):
    """Add HTML code for the blog post."""
    self.body.append(
        TEMPLATES['blogpost']['pre'].render(
            time=node['short_time'],
            long_time=node['time'],
            author=node['author'],
            category=node['category'],
            category_ref=node['category_ref'],
            tags=node['tags'],
            tags_and_ref=node['tags_and_ref'],
            title=node['title'],
            summary=node['summary'],
            next_node=node['next'],
            next_text=node['next_text'],
            prev_node=node['prev'],
            prev_text=node['prev_text'],
        )
    )


def html_depart_blogpost(self, node):
    """Add HTML code for the blog post."""
    # pylint: disable=unused-argument
    self.body.append(
        TEMPLATES['blogpost']['post'].render()
    )


def html_visit_blogoutput(self, node):
    """Add HTML code for blog summaries."""
    summary = shorten_text(node['summary'], length=100)
    self.body.append(
        TEMPLATES['blogoutput']['pre'].render(
            title=node['title'],
            summary=summary,
            refid=node['refid'],
            time=node['time'],
        )
    )


def html_depart_blogoutput(self, node):
    """Add HTML code for blog summaries."""
    # pylint: disable=unused-argument
    self.body.append(
        TEMPLATES['blogoutput']['post'].render()
    )


def html_visit_empty(self, node):
    """Do not add HTML code."""
    # pylint: disable=unused-argument
    pass


def html_depart_empty(self, node):
    """Do not add HTML code."""
    # pylint: disable=unused-argument
    pass


def html_visit_recent(self, node):
    """Add HTML code for the recent cards."""
    self.body.append(
        TEMPLATES['recent']['pre'].render(
            length=node['nmax'],
            items=node['items'],
        )
    )


def html_depart_recent(self, node):
    """Add HTML code for the recent cards."""
    # pylint: disable=unused-argument
    self.body.append(
        TEMPLATES['recent']['post'].render()
    )


def html_visit_taglist(self, node):
    """Add HTML code for the recent cards."""
    self.body.append(
        TEMPLATES['taglist']['pre'].render(
            tags=node['tags'],
            tags_and_ref=node['tags_and_ref'],
        )
    )


def html_depart_taglist(self, node):
    """Add HTML code for the recent cards."""
    # pylint: disable=unused-argument
    self.body.append(
        TEMPLATES['taglist']['post'].render()
    )
