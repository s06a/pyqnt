from setuptools import find_packages, setup

NAME = "quant"
DESCRIPTION = "Market data, quantitative analysis, and portfolio management tools for quants"
REQUIRES_PYTHON = ">=3.5.0"

REQUIRED = [
    "numpy>=1.24.0",
    "pandas>=2.0.0",
    "scipy>=1.8.0",
    "requests>=2.18.0",
    "pytse-client>=0.18.0",
]

setup(
    name=NAME,
    packages=["quant"],
    license="MIT Licence",
    version='0.1.0',
    url="https://github.com/s06a/quant",
    description=DESCRIPTION,
    python_requires=REQUIRES_PYTHON,
    install_requires=REQUIRED,
    author='s06a',
)