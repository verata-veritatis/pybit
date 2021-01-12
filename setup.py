from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pybit',
    version='1.1.11',
    description='Python3 Bybit HTTP/WebSocket API Connector', 
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/verata-veritatis/pybit',
    license='MIT License',
    author='Verata Veritatis',
    author_email='verata@pm.me',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    keywords='bybit api connector',
    packages=['pybit'],
    python_requires='>=3.6',
    install_requires=[
        'requests',
        'websocket-client'
    ], 
)
