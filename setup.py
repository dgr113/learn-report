# coding: utf-8

from setuptools import setup, find_packages




setup(
    name='learn_report',
    version='0.4.1',
    description='Learn reporter',
    long_description='Learn reporter',
    classifiers=[
        'Development Status :: 4',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Topic :: Data Processing :: Iterators :: Mail :: Utility',
    ],
    keywords='Learn reporter',
    url='',
    author='dgr113',
    author_email='dmitry-gr87@yandex.ru',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'reportlab',
        'jsonschema',
        'more-itertools',
        'helpful-vectors'
    ],
    dependency_links=[
        'http://github.com/dgr113/helpful-vectors/tarball/master#egg=package-1.0'
    ],
    entry_points={
        'console_scripts': [
            'learn-report-cli=cli'
        ],
    },
    include_package_data=True,
    zip_safe=False
)
