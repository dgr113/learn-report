# coding: utf-8

from setuptools import setup, find_packages




setup(
    name='learn-report',
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
        'https://github.com/dgr113/helpful-vectors/archive/master.zip#egg=helpful_vectors'
    ],
    data_files=[
        ('module', ['learn_report/module/_get.json']),
        ('sources/fonts', ['learn_report/sources/fonts/FreeSans.ttf'])
    ],
    entry_points={
        'console_scripts': [
            'learn-report-cli = learn_report.cli:main'
        ],
    },
    include_package_data=True,
    zip_safe=False
)
