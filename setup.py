import os
from setuptools import setup


def read():
    return open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(
    name='hockey_scraper',
    version='1.2.1',
    description="""This package is designed to allow people to scrape Play by Play and Shift data off of the National
                Hockey League (NHL) API and website for all preseason, regular season and playoff games since the 
                2007-2008 season""",
    long_description=read(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        'Intended Audience :: Science/Research',
        "License :: OSI Approved :: MIT License",
        'Programming Language :: Python :: 3',
        "Programming Language :: Python :: 2",
    ],
    keywords='NHL',
    url='https://github.com/HarryShomer/Hockey-Scraper',
    author='Harry Shomer',
    author_email='Harryshomer@gmail.com',
    license='MIT',
    packages=['hockey_scraper'],
    install_requires=['BeautifulSoup4', 'requests', 'lxml', 'html5lib', 'pandas', 'sphinx'],
    include_package_data=True,
    zip_safe=False
)
