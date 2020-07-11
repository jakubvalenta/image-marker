from codecs import open
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='image-marker',
    version='1.1.0',
    description='Image Marker',
    long_description=long_description,
    url='https://github.com/jakubvalenta/image-marker',
    author='Jakub Valenta',
    author_email='jakub@jakubvalenta.cz',
    license='Apache Software License',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Multimedia :: Graphics',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    packages=find_packages(),
    install_requires=['click', 'pyglet'],
    entry_points={'console_scripts': ['image-marker=image_marker.cli:cli']},
)
