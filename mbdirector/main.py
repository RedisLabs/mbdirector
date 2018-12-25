"""
Main module.
"""
import sys
import os.path
import json
import logging
import datetime
import pkg_resources

import click
from jsonschema import validate

from mbdirector.runner import Runner
from mbdirector.serve import run_webserver

def config_logging(log_filename):
    formatter = logging.Formatter(
        fmt='%(asctime)s %(levelname)s %(message)s')

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(stdout_handler)
    root_logger.addHandler(file_handler)
    root_logger.setLevel(logging.INFO)

@click.group()
def cli():
    pass

@cli.command()
@click.option('--spec', '-s', required=True, type=file,
              help='Benchmark specifications')
def benchmark(spec):
    schema_file = pkg_resources.resource_filename(
        'mbdirector', 'schema/mbdirector_schema.json')
    try:
        schema = json.load(open(schema_file))
    except Exception as err:
        click.echo('Error: failed to load schema: {}'.format(err))
        sys.exit(1)

    try:
       spec_json = json.load(spec)
    except Exception as err:
        click.echo('Error: failed to spec: {}: {}'.format(
            spec.name, err))
        sys.exit(1)

    try:
        validate(spec_json, schema)
    except Exception as err:
        click.echo('Error: invalid test: {}: {}'.format(spec.name, err))
        sys.exit(1)

    base_results_dir = os.path.join(
        'results', '{}Z'.format(datetime.datetime.utcnow().isoformat()))
    os.makedirs(base_results_dir)
    config_logging(os.path.join(base_results_dir, 'mbdirector.log'))

    _runner = Runner(base_results_dir, spec.name, spec_json)
    _runner.run()

@cli.command()
@click.option('--bind', '-b', required=False, default='127.0.0.1',
              help='Address to bind to')
@click.option('--port', '-p', required=False, default=8080,
              help='Port to listen on')
def serve(bind, port):
    run_webserver(bind, port)
