from setuptools import setup, find_packages


if __name__ == '__main__':
    setup(
        name='hockey_scrape',
        version='0.1.0',

        install_requires=[
            'pandas',
            'beautifulsoup4',
            'requests',
            'lxml',
        ],

        description="Hockey play-by-play/shift scraper",

        author='Harry Shomer',
        url='https://github.com/HarryShomer/Hockey',

        packages=find_packages(exclude=['tests']),

        classifiers=[
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3',
        ]
    )
