# Copyright (C) 2019 Redis Labs Ltd.
#
# This file is part of mbdirector.
#
# mbdirector is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2.
#
# mbdirector is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with memtier_benchmark.  If not, see <http://www.gnu.org/licenses/>.

import os
import logging
import time
import json
from fnmatch import fnmatch

from mbdirector.target import Target
from mbdirector.benchmark import Benchmark


class RunConfig(object):
    next_id = 1

    def __init__(self, base_results_dir, name, config, benchmark_config):
        self.id = RunConfig.next_id
        RunConfig.next_id += 1

        self.redis_process_port = config.get('redis_process_port', 6379)

        mbconfig = config.get('memtier_benchmark', {})
        mbconfig.update(benchmark_config)
        self.mb_binary = mbconfig.get('binary', 'memtier_benchmark')
        self.mb_threads = mbconfig.get('threads')
        self.mb_clients = mbconfig.get('clients')
        self.mb_pipeline = mbconfig.get('pipeline')
        self.mb_requests = mbconfig.get('requests')
        self.mb_test_time = mbconfig.get('test_time')
        self.explicit_connect_args = bool(
            mbconfig.get('explicit_connect_args'))

        self.results_dir = os.path.join(base_results_dir,
                                        '{:04}_{}'.format(self.id, name))

    def __repr__(self):
        return '<RunConfig id={}>'.format(self.id)


class Runner(object):
    def __init__(self, base_results_dir, spec_filename, spec,
                 skip_benchmarks, skip_targets):
        self.spec_filename = spec_filename
        self.spec = spec
        self.skip_benchmarks = skip_benchmarks
        self.skip_targets = skip_targets
        self.base_results_dir = base_results_dir
        self.start_time = None
        self.end_time = None
        self.errors = 0

    def run_benchmark(self, benchmark_json, target_json):
        name = '{}_{}'.format(benchmark_json['name'],
                              target_json['name'])

        logging.info('===== Running benchmark "%s" =====', name)

        config = RunConfig(self.base_results_dir, name,
                           self.spec['configuration'],
                           benchmark_json.get('configuration', {}))
        os.makedirs(config.results_dir)

        # Write benchmark info
        with open(os.path.join(config.results_dir,
                               "benchmark.json"), "w") as bfile:
            json.dump({'benchmark': benchmark_json['name'],
                       'target': target_json['name']}, bfile)

        target = Target.from_json(config, target_json)
        benchmark = Benchmark.from_json(config, benchmark_json)

        logging.info('Setting up target "%s"', target.name)
        try:
            target.setup()
        except Exception as err:
            logging.exception('Failed to set up target: %s' % err)
            self.errors += 1
            return

        logging.info('Running benchmark "%s"', benchmark.name)
        if not benchmark.run():
            logging.error('Benchmark execution failed')
            self.errors += 1

        logging.info('Tearing down target "%s"', target.name)
        target.teardown()

    def write_result(self):
        with open(os.path.join(self.base_results_dir,
                               'result.json'), 'w') as rfile:
            json.dump({'run_time': self.end_time - self.start_time,
                       'errors': self.errors,
                       'spec_filename': self.spec_filename},
                      rfile)

    def write_spec(self):
        with open(os.path.join(self.base_results_dir,
                               'spec.json'), 'w') as sfile:
            json.dump(self.spec, sfile)

    def should_skip_benchmark(self, benchmark):
        for pattern in self.skip_benchmarks:
            if fnmatch(benchmark['name'], pattern):
                return True
        return False

    def should_skip_target(self, target):
        for pattern in self.skip_targets:
            if fnmatch(target['name'], pattern):
                return True
        return False

    def run(self):
        self.write_spec()
        self.start_time = time.time()

        for benchmark in self.spec['benchmarks']:
            if self.should_skip_benchmark(benchmark):
                logging.info('Skipping benchmark: %s', benchmark['name'])
                continue

            for target in self.spec['targets']:
                if self.should_skip_target(target):
                    logging.info('Skipping target: %s', target['name'])
                    continue

                self.run_benchmark(benchmark, target)

        self.end_time = time.time()
        self.write_result()
