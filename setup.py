from setuptools import setup, find_packages

setup(
    name="mayalabs",
    version="0.0.1",
    packages=find_packages(),
    package_dir={'src': 'src'},
    install_requires=[
        "requests",
        "pydantic",
    ],
)