from os import path
from setuptools import setup, find_packages


here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="robotframework-djangorobotlibrary",
    version="19.1a0",
    description="A Robot Framework library for Django.",
    long_description=long_description,
    url="https://github.com/hugis/robotframework-djangorobotlibrary",
    author="Peter Hyben",
    author_email="peter.hyben@hugis.eu",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Environment :: Web Environment",
        "Framework :: Robot Framework",
        "Framework :: Django",
        "Framework :: Django :: 2.2",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    keywords="robotframework django test",
    packages=find_packages(),
    install_requires=["Django>=2.2", "factory_boy", "robotframework"],
    project_urls={
        "Source": "https://github.com/hugis/robotframework-djangorobotlibrary"
    },
)
