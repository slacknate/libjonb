from setuptools import setup, find_packages


setup(

    name="libjonb",
    version="0.0.1",
    url="https://github.com/slacknate/libjonb",
    description="A library for parsing and building BlazBlue collision box data.",
    packages=find_packages(include=["libjonb", "libjonb.*"]),
)
