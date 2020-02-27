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

import os.path
import subprocess
import logging


class Benchmark(object):
    def __init__(self, config, **kwargs):
        self.config = config
        self.binary = self.config.mb_binary
        self.name = kwargs['name']

        # Configure
        self.args = [self.binary]
        if not self.config.explicit_connect_args:
            self.args += ['--server', '127.0.0.1',
                          '--port', str(self.config.redis_process_port)
                          ]
        self.args += ['--out-file', os.path.join(config.results_dir,
                                                 'mb.stdout'),
                      '--json-out-file', os.path.join(config.results_dir,
                                                      'mb.json')]

        if self.config.mb_threads is not None:
            self.args += ['--threads', str(self.config.mb_threads)]
        if self.config.mb_clients is not None:
            self.args += ['--clients', str(self.config.mb_clients)]
        if self.config.mb_pipeline is not None:
            self.args += ['--pipeline', str(self.config.mb_pipeline)]
        if self.config.mb_requests is not None:
            self.args += ['--requests', str(self.config.mb_requests)]
        if self.config.mb_test_time is not None:
            self.args += ['--test-time', str(self.config.mb_test_time)]

        self.args += kwargs['args']

    @classmethod
    def from_json(cls, config, json):
        return cls(config, **json)

    def write_file(self, name, data):
        mode = 'w'
        if type(data)==bytes:
            mode = 'wb'
        with open(os.path.join(self.config.results_dir, name), mode) as outfile:
            outfile.write(data)

    def run(self):
        logging.debug('  Command: %s', ' '.join(self.args))
        process = subprocess.Popen(
            stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            executable=self.binary, args=self.args)
        _stdout, _stderr = process.communicate()
        if _stderr:
            logging.debug('  >>> stderr <<<\n%s\n', _stderr)
            self.write_file('mb.stderr', _stderr)
        return process.wait() == 0
