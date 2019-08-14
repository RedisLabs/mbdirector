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

    def run(self):
        logging.debug('  Command: %s', ' '.join(self.args))
        process = subprocess.Popen(
            stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            executable=self.binary, args=self.args)
        return process.wait() == 0
