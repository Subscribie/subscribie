import click
from os import environ
import subprocess

@click.group()
def cli():
    pass

@cli.command()
def run():
    """Install subscribie"""
    click.echo('Installing subscribie...')
    #TODO create initial .env file in cwd
    #TODO create initial jamla file in cwd
    #TODO run migrations

@cli.command()
def run():
    """Run subscribie"""
    environ['FLASK_APP'] = 'subscribie'
    from werkzeug.serving import run_simple
    click.echo('Running subscribie...')
    subprocess.call("flask run", shell=True)
