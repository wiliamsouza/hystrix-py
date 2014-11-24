hystrix-py
==========

[![Build Status](https://travis-ci.org/wiliamsouza/hystrix-py.svg)
](https://travis-ci.org/wiliamsouza/hystrix-py)

[![Coverage Status](https://img.shields.io/coveralls/wiliamsouza/hystrix-py.svg)](https://coveralls.io/r/wiliamsouza/hystrix-py)

A Netflix Hystrix implementation in Python.

What is Hystrix?
----------------

For more information see the [Netflix Hystrix]
(https://github.com/Netflix/Hystrix/wiki) Wiki documentation.

How it works
------------

To know more see the [Netflix Hystrix]
(https://github.com/Netflix/Hystrix/wiki/How-it-Works) Wiki How it works
section documentation.

Features
--------

It's **ALPHA** version and only support launching a group of commands inside
an executor pool.

* Execute synchronous commands.
* Execute asynchronous commands.
* Execute asynchronous commands and attach a callback.

Requirements
------------

It depends on [concurrent.futures]
(https://docs.python.org/3/library/concurrent.futures.html), new in Python
version 3.2.
It uses [futures](https://pypi.python.org/pypi/futures), backport to run in
Python version 2.7.

Installation
------------

```
mkproject --python=<fullpath_to_python_3.2+> hystrix-py
git clone https://github.com/wiliamsouza/hystrix-py hystrix-py
pip install -r requirements.txt
```

or

```
pip install -e https://github.com/wiliamsouza/hystrix-py
```

Development and test dependencies
---------------------------------

```
pip install -r requirements_test.txt
pip install -r requirements_development.txt
```

or

```
pip install -e .[dev,test]
```

Tests
-----

```
python setup.py test
```

Hello world
-----------

Code to be isolated is wrapped inside the `run()` method of a `hystrix.Command` similar to the following:

```python
from hystrix import Command

class HelloWorldCommand(Command):
    def run(self):
        return 'Hello World'
```

This command could be used like this:

```python
command = HelloCommand()

# synchronously
print(command.execute())
'Hello World'

# asynchronously
future = command.queue()
print(future.result())
'Hello Wold'

# callback
def print_result(future)
     print(future.result())

future = command.observe()
future.add_done_callback(print_result)
```
