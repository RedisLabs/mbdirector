Memtier-Benchmark Director
==========================

This is a front-end tool that makes it easier to run successive benchmarking
sessions using the memtier_benchmark tool by automating tasks such as:

* Setting up and tearing down Redis instances
* Running memtier_benchmark
* Collecting and organizing all data, logs, etc.
* Providing a simple web front to access data and a visual summary

![Screenshot](../assets/screenshot1.png?raw=true)

Getting Started
---------------

Clone this repo and `cd` into it.  Next, set up a local Python virtualenv and
install:

```
mkdir .env
virtualenv .env
. .env/bin/activate
python setup.py install
```

To run, create a benchmark JSON file and run:

```
mbdirector benchmark -s mybenchmark.json
```

This will set up the necessary targets, execute benchmarks, and store the
results in a `results` directory.  To access the results run `mbdirector serve`
from the same directory and point your browser to `http://localhost:8080`.

Benchmark Configuration
-----------------------

The benchmark configuration defines:
1. One or more *target*.  A target is a Redis database which is set up for the
   purpose of running a benchmark and teared down when it is complete.

   Currently the only supported target type is a local Redis process.  A useful
   "TODO" item would be to support Redis Enterprise API to provision a database
   of arbitrary configuration.

2. One or more *benchmark*.  A benchmark is a description of how to run
   `memtier_benchmark` (i.e. with specific arguments controlling size of
   elements, pipelining, etc.).

When executed, `mbdirector` runs a combination of all configured benchmarks and
all configured targets.

