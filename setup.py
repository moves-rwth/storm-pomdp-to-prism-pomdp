import os
from setuptools import setup

# Get the long description from the README file
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.md')) as f:
    long_description = f.read()

setup(
    name="storm-pomdp-to-prism-pomdp",
    version="0.1",
    author="S. Junges",
    author_email="sebastian.junges@cs.rwth-aachen.de",
    maintainer="S. Junges",
    maintainer_email="sebastian.junges@cs.rwth-aachen.de",
    url="https://github.com/moves-rwth/storm-pomdp-to-prism-pomdp",
    description="Conversion script",
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        "stormpy>=1.4.0"
    ],
    python_requires='>=3',
)
