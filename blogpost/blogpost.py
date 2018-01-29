# -*- coding: utf-8 -*-
# Copyright (c) 2018, Anders Lervik.
# Distributed under the LGPLv2.1+ License. See LICENSE for more info.
"""An extension for sphinx for making a blog-like web page."""
from datetime import datetime
import os
import jinja2
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


HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(HERE, 'templates')


TEMPLATES = {
    'blogpost': {
        'pre': {'file': os.path.join(TEMPLATE_DIR, 'blogpost.html')},
        'post': {'file': None}
    },
    'blogoutput': {
        'pre': {'file': os.path.join(TEMPLATE_DIR, 'blogoutput.html')},
        'post': {'file': None}
    },
    'recent': {
        'pre': {'file': os.path.join(TEMPLATE_DIR, 'recent.html')},
        'post': {'file': None}
    },
}


def set_up_templates():
    """Load files for the templates."""
    for template in TEMPLATES:
        for key in ('pre', 'post'):
            template_file = TEMPLATES[template][key]['file']
            if template_file is None or not os.path.isfile(template_file):
                TEMPLATES[template][key]['template'] = jinja2.Template('')
            else:
                with open(template_file, 'r') as template_raw:
                    TEMPLATES[template][key]['template'] = jinja2.Template(
                        template_raw.read()
                    )


set_up_templates()


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


def html_visit_blogpost(self, node):
    """Add HTML code for the blog post."""
    self.body.append(
        TEMPLATES['blogpost']['pre']['template'].render(
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
        TEMPLATES['blogpost']['post']['template'].render()
    )


def html_visit_blogoutput(self, node):
    """Add HTML code for blog summaries."""
    summary = shorten_text(node['summary'], length=100)
    self.body.append(
        TEMPLATES['blogoutput']['pre']['template'].render(
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
        TEMPLATES['blogoutput']['post']['template'].render()
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
        TEMPLATES['recent']['pre']['template'].render(
            length=node['nmax'],
            items=node['items'],
        )
    )


def html_depart_recent(self, node):
    """Add HTML code for the recent cards."""
    # pylint: disable=unused-argument
    self.body.append(
        TEMPLATES['recent']['post']['template'].render()
    )


def make_references(app, fromdocname):
    """Build references to posts from a given document.

    Parameters
    ----------
    app : object like :py:class:`sphinx.application.Sphinx`
        The application object used.
    fromdocname : string
        The document to create references from.

    Returns
    -------
    out : list of objects like :py:class:`docutils.nodes.reference`
        These nodes give the references to the posts from the
        given document name.

    """
    env = app.builder.env
    references = []
    for post_info in env.all_posts:
        post_node = post_info['post_node']
        newnode = nodes.reference(post_node['title'], post_node['title'])
        newnode['refuri'] = app.builder.get_relative_uri(
            fromdocname, post_info['docname'])
        newnode['refuri'] += '#' + post_info['targetnode']['refid']
        references.append(newnode)
    return references


def build_category_info(app, fromdocname):
    """Build info about categories.

    Parameters
    ----------
    app : object like :py:class:`sphinx.application.Sphinx`
        The application object used.
    fromdocname : string
        The document where the categories will be listed.

    Returns
    -------
    out : dict of list of dicts
        For each category, this dict contains a list of posts
        labeled with the category. Each post is represented with
        a dict.

    """
    env = app.builder.env
    categories = {}
    references = make_references(app, fromdocname)
    for post_info, refnode in zip(env.all_posts, references):
        post_node = post_info['post_node']
        cat = post_node['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(
            {
                'time': post_info['time'],
                'refnode': refnode,
                'post_node': post_node,
            }
        )
    # sort items in categories on time:
    for cat, items in categories.items():
        categories[cat] = sorted(items, key=lambda x: x['time'], reverse=True)

    if not hasattr(env, 'category_id'):
        env.category_id = {}
        for cat in sorted(categories):
            cat_id = 'category-%d' % env.new_serialno('category')
            env.category_id[cat] = cat_id
    return categories


def build_tag_info(app, fromdocname):
    """Build info about tags.

    Parameters
    ----------
    app : object like :py:class:`sphinx.application.Sphinx`
        The application object used.
    fromdocname : string
        The document where the tags will be listed.

    Returns
    -------
    out : dict of list of dicts
        For each tag, this dict contains a list of posts
        labeled with the tag. Each post is represented with
        a dict.

    """
    env = app.builder.env
    tags = {}
    references = make_references(app, fromdocname)
    for post_info, refnode in zip(env.all_posts, references):
        post_node = post_info['post_node']
        for tag in post_node['tags']:
            if tag not in tags:
                tags[tag] = []
            tags[tag].append(
                {
                    'time': post_info['time'],
                    'refnode': refnode,
                    'post_node': post_node,
                }
            )
    for tag, items in tags.items():
        tags[tag] = sorted(items, key=lambda x: x['time'], reverse=True)

    if not hasattr(env, 'tag_id'):
        env.tag_id = {}
        for tag in sorted(tags):
            tag_id = 'tag-%d' % env.new_serialno('tag')
            env.tag_id[tag] = tag_id
    return tags


def build_archive_info(app, fromdocname):
    """Buld info about all posts.

    Parameters
    ----------
    app : object like :py:class:`sphinx.application.Sphinx`
        The application object used.
    fromdocname : string
        The document where the archive will be listed.

    Returns
    -------
    out : dict of list of dicts
        For each year, this dict contains a list of posts
        from that year. Each post is represented with
        a dict.

    """
    env = app.builder.env
    archive = {}
    archive_flat = []
    references = make_references(app, fromdocname)
    for post_info, refnode in zip(env.all_posts, references):
        post_node = post_info['post_node']
        year = post_node['year']
        if year not in archive:
            archive[year] = []
        archive[year].append(
            {
                'time': post_info['time'],
                'refnode': refnode,
                'post_node': post_node,
            }
        )
        archive_flat.append(
            {
                'time': post_info['time'],
                'refnode': refnode,
                'post_node': post_node,
                'docname': post_info['docname'],
            }
        )
    for year, items in archive.items():  # sort on time
        archive[year] = sorted(items, key=lambda x: x['time'], reverse=True)
    archive_flat = sorted(archive_flat, key=lambda x: x['time'], reverse=True)
    if not hasattr(env, 'archive_id'):
        env.archive_id = {}
        for year in sorted(archive):
            year_id = 'year-%d' % env.new_serialno('year')
            env.archive_id[year] = year_id
    return archive, archive_flat


def make_new_section(key, item_dict, env_id):
    """Make a new section for a list of posts..

    The created section is used to show a list of post which
    are grouped in some way, for instance on tags,
    categories or years.

    Parameters
    ----------
    key : string
        The name of the new section
    item_dict : dict of list of dicts
        This dictionary contains the items in this section.
        Each post for a section is represented by a dict.
    env_id : dict of strings
        The unique references associated with the given key.

    Returns
    -------
    out[0] : object like :py:class:`docutils.nodes.section`
        The new section.
    out[1] : object like :py:class:`docutils.nodes.list_item`
        The contents of the section.

    """
    titl = '{} ({})'.format(key, len(item_dict[key]))
    section = nodes.section()
    section['ids'] = [env_id[key]]
    section['names'] = [env_id[key]]
    section['blog'] = titl
    title = nodes.subtitle('', '')
    ref = nodes.reference(titl, titl)
    ref['refid'] = env_id[key]
    title += ref
    section += title

    par = nodes.paragraph()
    ref = nodes.reference(titl, titl)
    ref['refid'] = env_id[key]
    par += ref
    section_item = nodes.list_item()
    section_item += par
    return section, section_item


def make_item_list(item_list):
    """Make output nodes for the items in a section.

    Parameters
    ----------
    item_list : list of dicts
        The posts for which we will generate some output.

    Returns
    -------
    out : object like :py:class:`docutils.nodes.bullet_list`
        The content of the section, represented as a bullet list.

    """
    item_bullet_list = nodes.bullet_list()
    for item in item_list:
        new_node = BlogOutputNode()
        new_node['title'] = item['post_node']['title']
        new_node['summary'] = item['post_node']['summary']
        new_node['refid'] = item['refnode']['refuri']
        new_node['time'] = item['time']
        item_par = nodes.paragraph()
        item_par += new_node
        list_item = nodes.list_item()
        list_item += item_par
        item_bullet_list += list_item
    return item_bullet_list


def update_node_replace(doctree, obj, item_dict, env_id, reverse=False):
    """Update a node with contents so that it will be rendered.

    This method is meant for replacing the archive node, the
    list-of-tags node and the list-of-categories node. These nodes
    will be replaced by other nodes which sphinx can handle.

    Parameters
    ----------
    doctree : object like :py:class:`docutils.nodes.document`
        The document in which we will be updating the node.
    obj : object
        This is the object class we will be looking for in the
        document.
    item_dict : dict of list of dicts.
        This dict contains the blog post, sorted on the keys and
        on time in each list.
    env_id : dict of strings
        These are the references for the categories/tags etc.
    reverse : boolean
        If True the posts will be sorted in reverse w.r.t. time.

    """
    for node in doctree.traverse(obj):
        sections = []
        section_list = nodes.bullet_list()
        par_sections = nodes.paragraph()
        for key in sorted(item_dict, reverse=reverse):
            # For each key add title/section
            section, section_item = make_new_section(key, item_dict, env_id)
            sections.append(section)
            section_list += section_item
            # Collect content for this section:
            section_content = make_item_list(item_dict[key])
            par_sections += section
            par_sections += section_content
        par = nodes.paragraph()
        par += section_list
        content = [par, par_sections]
        node.replace_self(content)


def get_image_name(app, env, docname, node):
    """Return the path to the summary image."""
    imgdir = os.path.dirname(
        app.builder.get_relative_uri(
            env.recent_docname, docname
        )
    )
    imgraw = os.path.join(imgdir, node['summary_image'])
    imgstatic = env.images[imgraw][1]
    imgfile = os.path.join(app.builder.imagedir, imgstatic)
    return imgfile


def update_recent_nodes(app, doctree, env, archive_flat):
    """Run the update for recent nodes."""
    for node in doctree.traverse(RecentNode):
        nmax = min(node['length'], len(archive_flat))
        node['nmax'] = nmax
        node['items'] = []
        for item in archive_flat[:nmax]:
            post_node = item['post_node']
            cat = post_node['category']
            new_item = {
                'title': post_node['title'],
                'category': cat,
                'short_time': post_node['short_time'],
                'summary': shorten_text(post_node['summary'], length=100),
                'time': item['time'],
                'author': post_node['author'],
                'has_image': False,
            }
            new_item['category_ref'] = app.builder.get_relative_uri(
                env.recent_docname, env.category_docname
            )
            new_item['category_ref'] += '#' + env.category_id[cat]
            new_item['tags_and_ref'] = []

            if post_node['summary_image']:
                new_item['has_image'] = True
                new_item['imagefile'] = get_image_name(
                    app, env, item['docname'], post_node
                )

            for tag in post_node['tags']:
                ref = app.builder.get_relative_uri(
                    env.recent_docname, env.tag_docname
                )
                ref += '#' + env.tag_id[tag]
                new_item['tags_and_ref'].append({'tag': tag, 'ref': ref})
            new_item['post_ref'] = app.builder.get_relative_uri(
                env.recent_docname, post_node['docname']
            )
            new_item['post_ref'] += '#' + post_node['targetid']
            node['items'].append(new_item)


def process_blog_posts(app, doctree, fromdocname):
    """Process the categories encountered in the blog posts."""
    env = app.builder.env

    categories = build_category_info(app, fromdocname)
    tags = build_tag_info(app, fromdocname)
    archive, archive_flat = build_archive_info(app, fromdocname)

    update_node_replace(doctree, CategoryNode, categories,
                        env.category_id)
    update_node_replace(doctree, TagNode, tags, env.tag_id)
    update_node_replace(doctree, ArchiveNode, archive, env.archive_id,
                        reverse=True)
    update_recent_nodes(app, doctree, env, archive_flat)
    # Also update category refs for post nodes:
    for node in doctree.traverse(BlogNode):
        cat = node['category']
        node['category_ref'] = app.builder.get_relative_uri(
            node['docname'], env.category_docname
        )
        node['category_ref'] += '#' + env.category_id[cat]
        node['tags_ref'] = []
        for tag in node['tags']:
            ref = app.builder.get_relative_uri(
                node['docname'], env.tag_docname
            )
            ref += '#' + env.tag_id[tag]
            node['tags_ref'].append(ref)
        node['tags_and_ref'] = []
        for tag, ref in zip(node['tags'], node['tags_ref']):
            node['tags_and_ref'].append({'tag': tag, 'ref': ref})
        add_next_prev(app, node, archive_flat)


def add_next_prev(app, node, archive_flat):
    """Add next/prev navigation for a node."""
    postmax = len(archive_flat) - 1
    for i, item in enumerate(archive_flat):
        if node['time'] == item['time']:
            idx_prev = i + 1
            if idx_prev > postmax:
                idx_prev = 0
                node['prev_text'] = 'Newest &olarr;'
            else:
                node['prev_text'] = 'Previous &rarr;'
            idx_next = i - 1
            if idx_next < 0:
                idx_next = postmax
                node['next_text'] = '&orarr; Oldest'
            else:
                node['next_text'] = '&larr; Next'
            node['next'] = app.builder.get_relative_uri(
                node['docname'], archive_flat[idx_next]['docname']
            )
            node['prev'] = app.builder.get_relative_uri(
                node['docname'], archive_flat[idx_prev]['docname']
            )


def make_toc(doctree, head='Tags'):
    """Make toc from a doctree."""
    fmt = '<li><a class="reference internal" href="{}">{}</a></li>'
    toc = [
        '<ul>',
        '<li><a class="reference internal" href="#">{}</a><ul>'.format(head),
    ]
    for node in doctree.traverse(nodes.section):
        if 'blog' in node:
            tag = node['ids'][0]
            toc.append(fmt.format('#'+tag, node['blog']))
    toc.append('</ul>')
    toc.append('</li>')
    toc.append('</ul>')
    return '\n'.join(toc)


def modify_toc(app, pagename, templatename, context, doctree):
    """Add contents to toc in a hackish way.

    The `toc` is used to add items to the `page` in the navigation bar.
    """
    # pylint: disable=unused-argument
    env = app.builder.env
    postdir = env.config.post_directory
    for key in ('tags', 'categories', 'archive'):
        dirname = os.path.join(postdir, key)
        if dirname in pagename:
            context['toc'] = make_toc(doctree, head=key.title())


def setup(app):
    """Register the new directive."""
    app.add_node(
        CategoryNode,
        html=(html_visit_empty, html_depart_empty),
    )
    app.add_node(
        TagNode,
        html=(html_visit_empty, html_depart_empty),
    )
    app.add_node(
        ArchiveNode,
        html=(html_visit_empty, html_depart_empty),
    )
    app.add_node(
        RecentNode,
        html=(html_visit_recent, html_depart_recent),
    )
    app.add_node(
        BlogNode,
        html=(html_visit_blogpost, html_depart_blogpost),
    )
    app.add_node(
        BlogOutputNode,
        html=(html_visit_blogoutput, html_depart_blogoutput),
    )
    app.add_config_value('post_directory', 'posts', 'env')
    app.add_directive('blog-post', BlogPostDirective)
    app.add_directive('blog-post-categories', BlogCategoryDirective)
    app.add_directive('blog-post-tags', BlogTagDirective)
    app.add_directive('blog-post-archive', BlogArchiveDirective)
    app.add_directive('blog-post-recent', BlogRecentDirective)
    app.connect('doctree-resolved', process_blog_posts)
    app.connect('html-page-context', modify_toc)
    return {'version': '0.1'}
