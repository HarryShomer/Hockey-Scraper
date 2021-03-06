import os
from setuptools import setup, find_packages


def read():
    return open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(
    name='hockey_scraper',
    version='1.37.6',
    description="""Python Package for scraping NHL Play-by-Play and Shift data.""",
    long_description=read(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        'Programming Language :: Python :: 3',
        "Programming Language :: Python :: 2",
    ],
    keywords='NHL',
    url='https://github.com/HarryShomer/Hockey-Scraper',
    author='Harry Shomer',
    author_email='Harryshomer@gmail.com',
    license='GNU General Public License v3 (GPLv3)',
    packages=find_packages(),
    install_requires=['BeautifulSoup4', 'requests', 'lxml', 'html5lib', 'pandas', 'pytest'],
    zip_safe=False,

    package_data={
        "": ["*.json"],
    }

    # entry_points={
    #     'console_scripts': [
    #         'hockey-scraper = hockey_scraper.cli:main',
    #     ],
    # }
)
