import os
import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.meta import MetaExtension
import yaml
from flask import Blueprint, render_template, request, abort, current_app, session, redirect, url_for
from functools import lru_cache
from datetime import datetime

blog_bp = Blueprint('blog', __name__)

# Define the directory containing blog post markdown files
POSTS_DIR = os.path.join(os.path.dirname(__file__), 'posts')
PROJECTS_DIR = os.path.join(os.path.dirname(__file__), 'projects')
VITRIOL_DIR = os.path.join(os.path.dirname(__file__), 'vitriol')


def parse_date(date_str):
    """Parse date string into datetime object."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except (ValueError, TypeError):
        return datetime.min


def setup_markdown(extensions):
    """Setup Markdown with the given extensions."""
    return markdown.Markdown(extensions=extensions, output_format='html5')


def parse_markdown_file(filepath, md):
    """Parse a markdown file and return the content and metadata."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        meta = {}
        html_content = ""

        if content.startswith('---'):
            try:
                _, front_matter, markdown_content = content.split('---', 2)
                meta = yaml.safe_load(front_matter) or {}
                html_content = md.convert(markdown_content)
            except (yaml.YAMLError, ValueError) as e:
                current_app.logger.error(f"Error parsing {filepath}: {str(e)}")
                html_content = md.convert(content)
        else:
            html_content = md.convert(content)

        return html_content, meta
    except Exception as e:
        current_app.logger.error(f"Error processing {filepath}: {str(e)}")
        return "", {}


def get_tag_colors(tags):
    """Generate consistent colors for tags that won't change between sessions."""
    color_palette = [
        "#D33F49", "#3E92CC", "#2EC4B6", "#FF9F1C", "#845EC2",
        "#4D8B31", "#FF6B6B", "#4A6C6F", "#F9C80E", "#5C415D"
    ]

    # Create a fixed mapping based on tag name
    tag_colors = {}
    for tag in tags:
        # Sum the character codes in the tag name
        char_sum = sum(ord(c) for c in tag)
        # Use this to deterministically select a color
        index = char_sum % len(color_palette)
        tag_colors[tag] = color_palette[index]

    return tag_colors


@lru_cache(maxsize=32)
def load_posts(directory):
    """Load and parse posts from the given directory with caching. Returns list of posts sorted by date."""
    posts = []
    if not os.path.exists(directory):
        os.makedirs(directory)
        return posts

    md = setup_markdown([
        CodeHiliteExtension(),
        TableExtension(),
        FencedCodeExtension(),
        MetaExtension(),
        'markdown.extensions.toc'
    ])

    for filename in os.listdir(directory):
        if not filename.endswith('.md'):
            continue

        filepath = os.path.join(directory, filename)
        html_content, meta = parse_markdown_file(filepath, md)

        post = {
            'slug': filename[:-3],
            'content': html_content,
            'title': meta.get('title', 'Untitled'),
            'author': meta.get('author', 'Unknown'),
            'date': meta.get('date', ''),
            'tags': meta.get('tags', []),
            'summary': meta.get('summary', ''),
            'toc': getattr(md, 'toc', ''),
            'last_modified': datetime.fromtimestamp(os.path.getmtime(filepath))
        }

        if directory == PROJECTS_DIR:
            # Project-specific fields
            post.update({
                'description': meta.get('description', post.get('summary', '')),
                'image': meta.get('image', ''),
                # 'demo_link': meta.get('demo_link', ''),
                'github_link': meta.get('github_link', ''),
                'technologies': meta.get('technologies', []),
                # Completed, In Progress, etc.
                'status': meta.get('status', 'Completed'),
                'date': meta.get('date', ''),
                'client': meta.get('client', ''),
                'role': meta.get('role', '')
            })

            # Use description as summary if summary is not provided
            if not post['summary'] and post.get('description'):
                post['summary'] = post['description']

        posts.append(post)

    posts.sort(key=lambda post: parse_date(post['date']), reverse=True)
    return posts


@blog_bp.route('/')
def index():
    """Blog index page with optional search functionality. Supports filtering by tag and search query."""
    query = request.args.get('q', '').strip().lower()
    tag = request.args.get('tag', '').strip().lower()
    posts = load_posts(POSTS_DIR)

    if query or tag:
        filtered_posts = [
            post for post in posts
            if (not query or query in post['title'].lower() or query in post['content'].lower()) and
               (not tag or tag in [t.lower() for t in post['tags']])
        ]
    else:
        filtered_posts = posts

    all_tags = sorted(set(tag for post in posts for tag in post['tags']))
    tag_colors = get_tag_colors(all_tags)

    return render_template('index.html',
                           posts=filtered_posts,
                           tags=all_tags,
                           tag_colors=tag_colors,
                           current_tag=tag,
                           query=query)


@blog_bp.route('/post/<slug>')
def post_detail(slug):
    """Individual post page with related posts suggestion."""
    posts = load_posts(POSTS_DIR)
    post = next((post for post in posts if post['slug'] == slug), None)

    if not post:
        abort(404, description="Post not found")

    related_posts = sorted(
        (other_post for other_post in posts if other_post['slug'] != slug and set(
            other_post['tags']) & set(post['tags'])),
        key=lambda p: len(set(p['tags']) & set(post['tags'])),
        reverse=True
    )[:3]

    # Get all tags for consistent coloring
    all_tags = sorted(set(tag for p in posts for tag in p.get('tags', [])))
    tag_colors = get_tag_colors(all_tags)

    return render_template('post.html', post=post, related_posts=related_posts, tag_colors=tag_colors, is_vitriol=False)


@blog_bp.route('/tag/<tag>')
def tag_posts(tag):
    """Show posts filtered by tag."""
    posts = [post for post in load_posts(POSTS_DIR) if tag.lower() in [
        t.lower() for t in post['tags']]]
    all_tags = sorted(set(tag for post in load_posts(POSTS_DIR)
                      for tag in post['tags']))
    tag_colors = get_tag_colors(all_tags)
    return render_template('index.html', posts=posts, current_tag=tag, tags=all_tags, tag_colors=tag_colors)


@blog_bp.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@blog_bp.route('/experience')
def experience():
    """Experience/CV page from resume.md"""
    resume_path = os.path.join(os.path.dirname(
        __file__), 'experience/resume.md')

    try:
        md = setup_markdown([
            CodeHiliteExtension(),
            TableExtension(),
            FencedCodeExtension(),
            'markdown.extensions.toc'
        ])
        html_content, meta = parse_markdown_file(resume_path, md)

        post = {
            'content': html_content,
            'title': meta.get('title', 'Untitled'),
            'toc': getattr(md, 'toc', ''),
            'tags': meta.get('tags', []),
            'summary': meta.get('summary', ''),
        }

        # Calculate tag colors here, after creating the post dictionary
        tag_colors = get_tag_colors(post['tags'])

        # Set the CV download path
        cv_download_path = url_for(
            'static', filename='assets/pdf/cv/federico_caria_cv.pdf')

        # Pass tag_colors to the template
        return render_template('experience.html', post=post, tag_colors=tag_colors,
                               cv_download_path=cv_download_path, show_cv_button=True)

    except FileNotFoundError:
        current_app.logger.error("Resume file not found")
        abort(404, description="Resume not found")
    except Exception as e:
        current_app.logger.error(f"Error processing resume: {str(e)}")
        abort(500, description="Error processing resume")


@blog_bp.route('/projects')
def projects():
    """Projects page showing all project posts"""
    # Load all project posts from the projects directory
    projects = load_posts(PROJECTS_DIR)

    # Ensure each project has all required fields
    for project in projects:
        # Ensure slug is available
        if 'slug' not in project:
            project['slug'] = project.get(
                'title', '').lower().replace(' ', '-')

        # Set default values for optional fields if not present
        project['summary'] = project.get(
            'summary', project.get('description', ''))
        project['technologies'] = project.get('technologies', [])
        project['image'] = project.get('image', '')
        project['demo_link'] = project.get('demo_link', '')
        project['github_link'] = project.get('github_link', '')

    # Get all tags for consistent coloring
    all_tags = sorted(
        set(tag for project in projects for tag in project.get('tags', [])))
    tag_colors = get_tag_colors(all_tags)

    return render_template('projects.html', projects=projects, tag_colors=tag_colors)


@blog_bp.route('/project/<slug>')
def project_detail(slug):
    """Individual project page"""
    projects = load_posts(PROJECTS_DIR)
    project = next(
        (project for project in projects if project['slug'] == slug), None)

    if not project:
        abort(404, description="Project not found")

    # Find related projects (those sharing tags)
    related_projects = []
    if 'tags' in project:
        related_projects = sorted(
            (other_project for other_project in projects if other_project['slug'] != slug and
             set(other_project.get('tags', [])) & set(project.get('tags', []))),
            key=lambda p: len(set(p.get('tags', [])) &
                              set(project.get('tags', []))),
            reverse=True
        )[:3]

    # Get all tags for consistent coloring
    all_tags = sorted(set(tag for p in projects for tag in p.get('tags', [])))
    tag_colors = get_tag_colors(all_tags)

    return render_template('post.html', post=project, related_posts=related_projects,
                           tag_colors=tag_colors, is_project=True)


@blog_bp.route('/vitriol', methods=['GET', 'POST'])
def vitriol():
    """Secret area requiring an acronym solution to access a list of posts"""
    correct_solution = "visita interiora terrae rectificando invenies occultum lapidem"

    if request.method == 'POST':
        solution = request.form.get('solution', '').lower().strip()

        if solution == correct_solution:
            session['vitriol_solved'] = True
            vitriol_posts = load_posts(VITRIOL_DIR)

            # Generate tag colors
            all_tags = sorted(
                set(tag for post in vitriol_posts for tag in post.get('tags', [])))
            tag_colors = get_tag_colors(all_tags)

            return render_template('vitriol.html', posts=vitriol_posts, solved=True,
                                   tags=all_tags, tag_colors=tag_colors)
        else:
            return render_template('vitriol.html', error="Incorrect solution. Try again.", solved=False)

    if session.get('vitriol_solved'):
        vitriol_posts = load_posts(VITRIOL_DIR)

        # Generate tag colors
        all_tags = sorted(
            set(tag for post in vitriol_posts for tag in post.get('tags', [])))
        tag_colors = get_tag_colors(all_tags)

        return render_template('vitriol.html', posts=vitriol_posts, solved=True,
                               tags=all_tags, tag_colors=tag_colors)

    return render_template('vitriol.html', solved=False)


@blog_bp.route('/vitriol/<slug>')
def vitriol_post(slug):
    """Show individual vitriol post"""
    if not session.get('vitriol_solved'):
        return redirect(url_for('blog.vitriol'))

    posts = load_posts(VITRIOL_DIR)
    post = next((post for post in posts if post['slug'] == slug), None)

    if not post:
        abort(404, description="Post not found")

    related_posts = sorted(
        (other_post for other_post in posts if other_post['slug'] != slug and set(
            other_post['tags']) & set(post['tags'])),
        key=lambda p: len(set(p['tags']) & set(post['tags'])),
        reverse=True
    )[:3]

    # Generate tag colors for all posts to ensure consistency
    all_tags = sorted(set(tag for p in posts for tag in p.get('tags', [])))
    tag_colors = get_tag_colors(all_tags)

    return render_template('post.html', post=post, related_posts=related_posts,
                           tag_colors=tag_colors, is_vitriol=True)
