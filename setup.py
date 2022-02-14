from setuptools import setup

with open("README.md") as f:
    README = f.read()

setup(
    entry_points={"kedro.plugins": ["kedrojson = kedrojson.plugin:commands"]},
)
