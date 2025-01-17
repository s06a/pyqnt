from setuptools import setup, find_packages

with open("requirements.txt") as f:
    all_requirements = f.read().splitlines()

setup(
    name="pyqnt",
    version="0.0.1",
    description="A CLI tool for portfolio optimization and quantitative analysis.",
    author="s06a",
    url="https://github.com/s06a/pyqnt",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=all_requirements,
    entry_points={
        "console_scripts": [
            "pyqnt=cli.main:pyqnt",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
