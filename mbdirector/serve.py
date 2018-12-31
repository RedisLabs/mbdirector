import os.path
import json

from flask import (Flask, render_template, send_file, abort, Response,
                   send_from_directory)
from werkzeug.serving import run_simple

class Config(object):
    RESULTS_BASEDIR = 'results'

app = Flask(__name__)
app.config.from_object('mbdirector.serve.Config')

class BenchmarkResults(object):
    def __init__(self, dirname):
        self.dirname = dirname
        self.info = {}
        self.stats = {}
        self.read()
        self.name = '{}|{}'.format(
            self.info['benchmark'], self.info['target'])

    def read(self):
        with open(os.path.join(self.dirname, 'benchmark.json'), 'r') as bfile:
            self.info = json.load(bfile)

        try:
            with open(os.path.join(self.dirname, 'mb.json'), 'r') as sfile:
                self.json = json.load(sfile)
                self.stats = self.json.get('ALL STATS', {})
        except Exception:
            self.json = {}
            self.stats = {}

    def print_json(self):
        return json.dumps(self.json, indent=2)

    def files(self):
        all_files = ['redis.log', 'mb.stdout']
        result = [f for f in all_files
                  if os.path.exists(os.path.join(self.dirname, f))]
        return result

class RunResults(object):
    OK = 'ok'
    NOTFOUND = 'results-not-found'
    INVALID = 'results-invalid'

    def __init__(self, dirname):
        self.name = dirname
        self.dirname = os.path.join(app.config['RESULTS_BASEDIR'], dirname)
        self.results = {}
        self.status = self.OK
        self.read_results()
        self.benchmarks = {}
        self.read_benchmark_results()

    def read_benchmark_results(self):
        dirs = []
        try:
            dirs = os.listdir(self.dirname)
        except OSError:
            pass
        for benchdir in dirs:
            path = os.path.join(self.dirname, benchdir)
            if os.path.isdir(path):
                benchmark = BenchmarkResults(path)
                self.benchmarks[benchmark.name] = benchmark

    def read_results(self):
        try:
            with open(os.path.join(self.dirname, 'result.json'), 'r') as rfile:
                self.results = json.load(rfile)
        except IOError:
            self.status = self.NOTFOUND
        except ValueError:
            self.status = self.INVALID

    def get_benchmark_labels(self):
        return [b.name for b in self.benchmarks.itervalues()]

    def __render_dataset(self, benchmark, section_key_list):
        return {
            'label': '{}|{}'.format(benchmark.info['benchmark'],
                                    benchmark.info['target']),
            'data': [benchmark.stats.get(sk[0], {}).get(sk[1])
                     for sk in section_key_list]
        }

    def render_tps_stats(self):
        return {
            'labels': ['Total', 'Gets', 'Sets'],
            'datasets': [self.__render_dataset(b, [('Totals', 'Ops/sec'),
                                                   ('Gets', 'Ops/sec'),
                                                   ('Sets', 'Ops/sec')])
                         for b in self.benchmarks.itervalues()]
        }

    def render_latency_stats(self):
        return {
            'labels': ['Average', 'Gets', 'Sets'],
            'datasets': [self.__render_dataset(b, [('Totals', 'Latency'),
                                                   ('Gets', 'Latency'),
                                                   ('Sets', 'Latency')])
                         for b in self.benchmarks.itervalues()]
        }

    def render_bandwidth_stats(self):
        return {
            'labels': ['Total', 'Gets', 'Sets'],
            'datasets': [self.__render_dataset(b, [('Totals', 'KB/sec'),
                                                   ('Gets', 'KB/sec'),
                                                   ('Sets', 'KB/sec')])
                         for b in self.benchmarks.itervalues()]
        }


def get_run_results():
    dirs = []
    try:
        dirs = os.listdir(app.config['RESULTS_BASEDIR'])
    except OSError:
        pass

    return [RunResults(d) for d in sorted(dirs)]

@app.route('/')
def index():
    return render_template('index.html', results=get_run_results())

@app.route('/run/<run>')
def get_run(run):
    return render_template('run.html', run=RunResults(run))

@app.route('/run/<run>/spec')
def get_run_spec(run):
    specfile = open(os.path.join(
        app.config['RESULTS_BASEDIR'], run, 'spec.json'), 'r')
    return send_file(specfile, mimetype='text/plain')

@app.route('/run/<run>/<benchmark>/json')
def get_benchmark_json(run, benchmark):
    run = RunResults(run)
    if not benchmark in run.benchmarks:
        abort(404)
    return Response(run.benchmarks[benchmark].print_json(),
                    mimetype='text/plan')

@app.route('/run/<run>/<benchmark>/file/<filename>')
def get_benchmark_file(run, benchmark, filename):
    run = RunResults(run)
    if not benchmark in run.benchmarks:
        abort(404)
    return send_from_directory(
        os.path.abspath(run.benchmarks[benchmark].dirname),
        filename, mimetype='text/plan')

def run_webserver(bind, port):
    run_simple(bind, port, app)
