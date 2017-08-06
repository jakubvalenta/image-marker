from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='image-marker',

    version='1.0.0',

    description='Image Marker',
    long_description=long_description,

    url='https://lab.saloun.cz/jakub/image-marker',

    author='Jakub Valenta',
    author_email='jakub@jakubvalenta.cz',

    license='Apache Software License',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Multimedia :: Graphics',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
    ],

    packages=find_packages(),

    install_requires=[
        'attrs',
        'click',
        'pyglet',
    ],

    entry_points={
        'console_scripts': [
            'image-marker=image_marker.cli:cli',
        ],
    },
)
