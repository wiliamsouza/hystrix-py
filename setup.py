import sys
from os import path
from codecs import open

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


here = path.abspath(path.dirname(__file__))

setup_requires = ['pytest', 'tox', 'six']
install_requires = ['six', 'tox']
dev_requires = ['pyflakes', 'pep8', 'pylint', 'check-manifest',
                'ipython', 'ipdb', 'sphinx', 'sphinx_rtd_theme',
                'sphinxcontrib-napoleon']
tests_require = ['pytest-cov', 'pytest-cache', 'pytest-timeout',
                 'coverage==3.7.1']

PY2 = sys.version_info.major is 2
PY32 = sys.version_info.major is 3 and sys.version_info.minor is 2
PY33 = sys.version_info.major is 3 and sys.version_info.minor is 3

if PY2:
    install_requires.append('futures')
    install_requires.append('enum34')

if PY32 or PY33:
    install_requires.append('enum34')

# Get the long description
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['--strict', '--verbose', '--tb=long',
                          '--cov', 'hystrix', '--cov-report',
                          'term-missing', 'tests']
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

setup(
    name='hystrix-py',
    version='0.1.0',
    description='A Netflix Hystrix implementation in Python',
    long_description=long_description,
    url='https://github.com/wiliamsouza/hystrix-py',
    author='The Hystrix Python Authors',
    author_email='wiliamsouza83@gmail.com',
    license='Apache Software License 2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Library',
        'License :: OSI Approved :: Apache Software License 2.0',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='sample setuptools development',
    packages=find_packages(exclude=['docs', 'tests*']),
    setup_requires=setup_requires,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        'dev': dev_requires,
        'test': tests_require,
    },
    cmdclass={'test': PyTest},
)
