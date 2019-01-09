# coding: utf-8

from setuptools import setup, find_packages



setup(
    name='learn_report',
    version='0.3a',
    description='Learn reporter',
    long_description='Learn reporter',
    classifiers=[
        'Development Status :: 3 - Alpha',
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
        'pandas',
        'numpy',
        'matplotlib',
        'more-itertools'
    ],
    include_package_data=True,
    zip_safe=False
)
