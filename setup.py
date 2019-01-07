import os
from setuptools import setup


def read():
    return open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(
    name='hockey_scraper',
    version='1.3',
    description="""This package is designed to allow one to scrape the raw data for both the National Hockey League
                   (NHL) and the National Women's Hockey League (NWHL) off of their respective API and websites. For the 
                   NHL it allows one to scrape the Play by Play and Shift data since the 2007-2008 season. For the 
                   NWHL is allows one to scrape the Play by Play data since the 2015-2016 season. This package supports 
                   the scraping of all preseason, regular season, and playoff games for both leagues.""",
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
    install_requires=['BeautifulSoup4', 'requests', 'lxml', 'html5lib', 'pandas', 'sphinx', 'pytest'],
    include_package_data=True,
    zip_safe=False
)
