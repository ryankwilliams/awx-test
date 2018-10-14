import setuptools
import re

with open("README.md", "r") as fh:
    long_description = fh.read()


requirements = [
    x.strip() for x
    in open('requirements.txt').readlines() if not x.startswith('#')
]


setuptools.setup(
    name="awx-wrapper",
    version="0.1.1",
    author="rywillia",
    author_email="rywillia@gmail.com",
    description="awx python wrapper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rywillia/awx-test",
    packages=['awx'],
    install_requires=requirements,
    classifiers=(
        "Programming Language :: Python :: 3.5",
        "Operating System :: OS Independent",
    ),
)
