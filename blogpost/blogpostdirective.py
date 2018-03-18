# -*- coding: utf-8 -*-
# Copyright (c) 2018, Anders Lervik.
# Distributed under the LGPLv2.1+ License. See LICENSE for more info.
"""An extension for sphinx for making a blog-like web page."""
from datetime import datetime
import os
from docutils import nodes
from docutils.parsers.rst import Directive
from docutils.parsers.rst.directives import positive_int


BLOG_ITEMS = {
    'author': 'string',
    'author_email': 'string',
    'tags': 'set',
    'title': 'string',
    'category': 'string',
    'location_city': 'string',
    'location_country': 'string',
    'time': 'string',
    'summary': 'string',
    'summary_image': 'string',
}


def shorten_text(text, length=50, suffix='...'):
    """Shorten text for a summary.

    Parameters
    ----------
    text : string
        The intput text.
    length : integer
        The maximum length.
    suffix : string
        The suffix to add after the maximum length.

    Returns
    -------
    out : string
        The shortened string.

    Note
    ----
    The output string can be longer than 50 characters since
    the suffix is added to the shortened string.

    """
    if len(text) <= length:
        return text
    return text[:length].rsplit(' ', 1)[0] + suffix


def cvs_to_list(argument):
    """Extract comma-separated values.

    Parameters
    ----------
    argument : string
        A string with comma separated values.

    Returns
    -------
    out : list of strings
        A list of strings as read from the input string.

    """
    if argument is None:
        return []
    value = [i.strip().lower() for i in argument.split(',')]
    return value


def stripped(argument):
    """Return the argument text, stripped.

    Parameters
    ----------
    argument : string
        The input text to strip.

    """
    if argument is None:
        return ''
    return argument.strip()


class BlogNode(nodes.General, nodes.Element):
    """A simple node for a blog post.

    This node is used by :py:class:`.BlogPostDirective` to store
    the arguments for the blog post when parsing the directive.

    """

    # pylint: disable=unused-argument
    pass


class BlogOutputNode(nodes.General, nodes.Element):
    """A simple node for a blog categories.

    This node is used to store information which is used
    for creating the small summaries in the list of tags, categories
    and for the archive.

    """

    # pylint: disable=unused-argument
    pass


class CategoryNode(nodes.General, nodes.Element):
    """A simple node for a blog categories.

    This node is used by :py:class:`.BlogCategoryDirective` to store
    category information from the blog posts.

    """

    # pylint: disable=unused-argument
    pass


class TagNode(nodes.General, nodes.Element):
    """A simple node for a blog categories.

    This node is used by :py:class:`.BlogTagDirective` to store
    tag information from the blog posts.

    """

    # pylint: disable=unused-argument
    pass


class TagListNode(nodes.General, nodes.Element):
    """A simple node for a blog categories.

    This node is used by :py:class:`.BlogTagListDirective` to store
    tag information from the blog posts.

    """

    # pylint: disable=unused-argument
    pass


class ArchiveNode(nodes.General, nodes.Element):
    """A simple node for a blog categories.

    This node is used by :py:class:`.BlogArchiveDirective` to store
    information from the blog posts.

    """

    # pylint: disable=unused-argument
    pass


class RecentNode(nodes.General, nodes.Element):
    """A simple node for a blog categories.

    This node is used by :py:class:`.BlogRecentDirective` to store
    information from the most recent blog posts.

    """

    # pylint: disable=unused-argument
    pass


class BlogPostDirective(Directive):
    """A directive representing a blog post."""

    has_content = False
    required_arguments = 0
    optional_arguments = 0
    option_spec = {}
    empty_defaults = {}
    date_format = '%d.%m.%Y, %H:%M:%S'
    short_date_format = '%B %d, %Y'

    for key in BLOG_ITEMS:
        if key == 'tags':
            option_spec[key] = cvs_to_list
        else:
            option_spec[key] = stripped
        empty_defaults[key] = option_spec[key](None)

    def run(self):
        """Execute the directive parsing."""
        node = BlogNode()
        for key in self.option_spec:
            if key in self.options:
                node[key] = self.options[key]
            else:
                node[key] = self.empty_defaults[key]
        # Extract some time information:
        time = datetime.strptime(node['time'], self.date_format)
        year = time.year
        node['short_time'] = time.strftime(self.short_date_format)
        node['time'] = time
        node['category_ref'] = None
        node['docname'] = None
        node['tags_ref'] = [None for _ in node['tags']]
        node['tags_and_ref'] = [(None, None) for _ in node['tags']]
        node['year'] = year
        # Store information about the node, for further processing in
        # other directives.
        return_nodes = []
        try:
            env = self.state.document.settings.env
            targetid = "post-%d" % env.new_serialno('post')
            targetnode = nodes.target('', '', ids=[targetid])
            node['docname'] = env.docname
            node['dirname'] = os.path.dirname(env.docname)
            node['targetid'] = targetid
            if node['summary_image']:
                sub = nodes.substitution_definition()
                img = nodes.image()
                img['uri'] = node['summary_image']
                env.images.add_file('', img['uri'])
                sub += img
                return_nodes.append(sub)
            if not hasattr(env, 'all_posts'):
                env.all_posts = []
            env.all_posts.append(
                {
                    'time': time,
                    'post_node': node.deepcopy(),
                    'docname': env.docname,
                    'datetime': time,
                    'targetid': targetid,
                    'targetnode': targetnode,
                }
            )
            return_nodes.append(targetnode)
            return_nodes.append(node)
            return return_nodes
        except AttributeError:
            pass
        return [node]


class BlogCategoryDirective(Directive):
    """A directive for listing the categories."""

    has_content = False

    def run(self):
        """Parse directive."""
        node = CategoryNode()
        env = self.state.document.settings.env
        if not hasattr(env, 'category_docname'):
            env.category_docname = env.docname
        else:
            raise ValueError('Only one category list is supported!')
        node['categories'] = []
        return [node]


class BlogTagDirective(Directive):
    """A directive for listing the tags."""

    has_content = False

    def run(self):
        """Parse directive."""
        node = TagNode()
        env = self.state.document.settings.env
        if not hasattr(env, 'tag_docname'):
            env.tag_docname = env.docname
        else:
            raise ValueError('Only one tag list is supported!')
        node['tags'] = []
        return [node]


class BlogTagListDirective(Directive):
    """A directive for listing the tags."""

    has_content = False

    def run(self):
        """Parse directive."""
        node = TagListNode()
        env = self.state.document.settings.env
        node['docname'] = env.docname
        return [node]


class BlogArchiveDirective(Directive):
    """A directive for making the archive list."""

    has_content = False

    def run(self):
        """Parse directive."""
        node = ArchiveNode()
        env = self.state.document.settings.env
        if not hasattr(env, 'archive_docname'):
            env.archive_docname = env.docname
        else:
            raise ValueError('Only one archive list is supported!')
        node['years'] = []
        return [node]


class BlogRecentDirective(Directive):
    """A directive for the recent blog posts."""

    has_content = False
    required_arguments = 0
    optional_arguments = 0
    option_spec = {'length': positive_int}

    def run(self):
        """Parse directive."""
        node = RecentNode()
        for key in self.option_spec:
            node[key] = self.options[key]
        node['items'] = []
        node['nmax'] = 0
        env = self.state.document.settings.env
        if not hasattr(env, 'recent_docname'):
            env.recent_docname = env.docname
        else:
            raise ValueError('Recent posts can only be inserted once!')
        if not hasattr(env, 'recent_nodes'):
            env.recent_nodes = []
        env.recent_nodes.append(node)
        return [node]
