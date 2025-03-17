import os
from setuptools import setup, find_packages

# Read requirements.txt - but exclude the spaCy model URL
with open('requirements.txt', 'r') as f:
    requirements = [line.strip() for line in f.readlines()
                   if line.strip() and not line.startswith('#')
                   and not line.startswith('en_core_web_sm @')]

# Add spaCy as a dependency
requirements.append("spacy>=3.8.0")

# Read the README file
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="autiobooksqta",
    version="0.1.0",
    author="Scott Peterman",
    author_email="scottpeterman@gmail.com",
    description="A PyQt6-based application for converting EPUB books to audiobooks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/scottpeterman/autiobooksqta",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'autiobooksqta': ['models/en_core_web_sm-3.8.0-py3-none-any.whl'],
    },
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "autiobooksqta=autiobooksqta.__main__:main",
        ],
    },
)