hystrix-py
==========

A netflix hystrix implementation in Python.

Features
--------

It's **ALPHA** version and only support launching a group off commands inside
an executor pool.

* Execute synchronous commands.
* Execute asynchronous commands.
* Execute asynchronous commands and attach a callback.

Requirements
------------

It depends on [concurrent.futures](https://docs.python.org/3/library/concurrent.futures.html#module-concurrent.futures), New in Python version 3.2.

Instalation
-----------

```
mkproject --python=<fullpath_to_python_3.2+> hystrix-py
git clone https://github.com/wiliamsouza/hystrix-py hystrix-py
```

or

```
pip install -e https://github.com/wiliamsouza/hystrix-py
```

Development and test dependencies
---------------------------------


```
pip install -r requirements.txt
pip install -r requirements_test.txt
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
     print(future.result)

future = command.observe()
future.add_done_callback(print_result)
```
