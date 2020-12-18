from setuptools import setup

setup(
    name = "dependencies",
    version = "1.0",
    description = "coustom packages install",

    author = "Adbert",

    packages = [
        'dependencies',
        'dependencies/google_search/ec',
        'dependencies/google_search/forum',
        ],
    include_package_data = True,
    platforms = "any",
    install_requires = [],

    scripts = [],
)
