hystrix-py
==========

[![Build Status](https://travis-ci.org/wiliamsouza/hystrix-py.svg)
](https://travis-ci.org/wiliamsouza/hystrix-py)
[![Coverage Status](https://img.shields.io/coveralls/wiliamsouza/hystrix-py.svg)](https://coveralls.io/r/wiliamsouza/hystrix-py)
[![Documentation Status](https://readthedocs.org/projects/hystrix-py/badge/?version=latest)](https://readthedocs.org/projects/hystrix-py/?badge=latest)

A Netflix Hystrix port to Python.

**This is a work in progress, please feel free to help!**


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
version 3.2 and [enum]
(https://docs.python.org/3.4/library/enum.html), new in Python version 3.4.
It uses [futures](https://pypi.python.org/pypi/futures) and
[enum34](https://pypi.python.org/pypi/enum34/) backports to run in Python
version 2.7, 3.3 and 3.4.


Installation
------------

Create a virtualenv:

```
mkproject --python=<fullpath_to_python_3.2+> hystrix-py
```

Get the code:

```
git clone https://github.com/wiliamsouza/hystrix-py .
```

Install it:

```
python setup.py develop
```

The last command enter your code in "Development Mode" it creates an
`egg-link` in your virtualenv's `site-packages` making it available
on this environment `sys.path`. For more info see [setuptools development-mode]
(https://pythonhosted.org/setuptools/setuptools.html#development-mode)


Development and test dependencies
---------------------------------

`setup.py` will handle test dependencies, to install development use:

```
pip install -e .[dev]
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

LICENSE
-------

Copyright 2015 Hystrix Python Authors.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

<http://www.apache.org/licenses/LICENSE-2.0>

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
