from flask import (Blueprint, render_template, abort, request, redirect,
        current_app, url_for, flash, Markup)
from jinja2 import TemplateNotFound
from subscribie.auth import login_required
from subscribie.models import database, Page
from pathlib import Path
import yaml

module_pages = Blueprint('pages', __name__, template_folder='templates', static_folder="static")


@module_pages.route('/add-pages')
@login_required
def get_module_pages_index():
    """Return module_pages index page"""

    return render_template('module_pages_index.html')

@module_pages.route('/add-page')
@login_required
def add_page():
    """Return add page form"""
    return render_template('add_page.html')

@module_pages.route('/delete-pages')
@login_required
def delete_pages_list():
    pages = Page.query.all()
    return render_template('delete_pages_list.html', pages=pages)

@module_pages.route('/delete-page/<path>', methods=['POST', 'GET'])
@login_required
def delete_page_by_path(path):
    """Delete a given page"""
    if "confirm" in request.args:
        confirm = False
        return render_template(
            "delete_pages_list.html",
            path=path,
            confirm=False,
        )
    # Perform template file deletion
    templateFile = path + '.html'
    templateFilePath = Path(str(current_app.config['THEME_PATH']), templateFile)
    try:
        templateFilePath.unlink()
    except FileNotFoundError:
        pass

    # Perform page deletion
    page = Page.query.filter_by(path=path).first()
    database.session.delete(page)
    database.session.commit()

    flash(f'Page "{path}" deleted.')
    return redirect(url_for('views.reload_app') + '?next=' + url_for('pages.delete_pages_list'))

@module_pages.route('/edit-pages')
@login_required
def edit_pages_list():
    pages = Page.query.all()
    return render_template('edit_pages_list.html', pages=pages)

@module_pages.route('/edit-page/<path>', methods=['POST', 'GET'])
@login_required
def edit_page(path):
    """Edit a given page"""
    page = Page.query.filter_by(path=path).first()
    if request.method == 'GET':
        # Get page file contents
        template_file = page.template_file
        with open(Path(str(current_app.config['THEME_PATH']), template_file)) as fh:
            rawPageContent = fh.read()
        return render_template('edit_page.html', rawPageContent=rawPageContent, pageTitle=page.page_name)

    elif request.method == 'POST':
        try:
            page_title = request.form['page-title']
            page.page_name = page_title
        except KeyError:
            return "Error: Page title is required"

        try:
            page_body = request.form['page-body']
        except KeyError:
            return "Error: Page body is required"
        # Generate a valid path for url
        page_path = ''
        for char in page_title:
            if char.isalpha():
                page_path += char.lower()

        # Generate a valid html filename
        template_file = page_path + '.html'.lower()
        page.template_file = template_file

        # Detect if page name has been changed
        if page.path != page_path:
            page.path = page_path
            oldTemplateFile = path + '.html'
            # Rename old template file .old
            oldTemplatePath = Path(str(current_app.config['THEME_PATH']), oldTemplateFile)
            oldTemplatePath.replace(Path(str(current_app.config['THEME_PATH']), oldTemplateFile + '.old'))
        # Writeout new template_file to file
        with open(Path(str(current_app.config['THEME_PATH']), template_file), 'w') as fh:
            fh.write(page_body)

        flash(Markup(f'Page edited. <a href="/{page.path}">{page.page_name}</a> '))

        # Save page to database
        database.session.commit()

        # Graceful reload app to load new page
        return redirect(url_for('views.reload_app') + '?next=' + url_for('pages.edit_pages_list'))



@module_pages.route('/add-page', methods=['POST'])
@login_required
def save_new_page():
    """Save the new page

        Writes out a new file <page-name>.html
        and updates page table with the newly 
        added page.
    """
    try:
        page_title = request.form['page-title']
    except KeyError:
        return "Error: Page title is required"

    try:
        page_body = request.form['page-body']
    except KeyError:
        return "Error: Page body is required"

    # Generate a valid path for url
    pageName = ''
    for char in page_title:
        if char.isalpha():
            pageName += char
    # Generate a valid html filename
    template_file = pageName + '.html'

    page_header = """
        {% extends "layout.html" %}
        {% block title %} {{ title }} {% endblock title %}

        {% block hero %}

            <div class="container">
              <div class="row">
                <div class="col-md-8 pl-0">
                  <h1 class="h1 text-white font-weight-bold">{{ title }}</h1>
                </div>
              </div>
            </div>

        {% endblock %}
        {% block body %}
        <div class="section">
          <div class="container">
          
    """
    page_footer = """
          </div><!-- end container -->
        </div><!-- end section -->
        {% endblock body %}
    """

    # Check page doesnt already exist
    page = Page.query.filter_by(path=pageName).first()
    if page is not None:
        flash(Markup(f'The page <a href="/{pageName}">{pageName}</a> already exists'))
        return redirect(url_for('views.reload_app') + '?next=' + url_for('pages.edit_pages_list'))

    # Add new page
    page = Page()
    page.page_name = page_title
    page.path = pageName.lower()
    page.template_file = template_file.lower()
    database.session.add(page)
    database.session.commit()

    # Writeout template_file to file
    with open(Path(str(current_app.config['THEME_PATH']), template_file.lower()), 'w') as fh:
        full_page = page_header + page_body + page_footer
        fh.write(full_page)

    flash(Markup(f'Your new page <a href="/{page.path}">{page.page_name}</a> will be visable after reloading'))

    # Graceful reload app to load new page
    return redirect(url_for('views.reload_app') + '?next=' + url_for('pages.edit_pages_list'))