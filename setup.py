from setuptools import setup, find_packages

setup(
    name='autiobooks',
    version='1.1.0',
    packages=find_packages(),
    install_requires=[
    ],
    author='Scott Peterman',
    description='Automatically convert epubs to audiobooks - forked from https://github.com/plusuncold/autiobooks',
    long_description=open('README_Original.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/scottpeterman/autiobooksqt',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GPLv3 License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)