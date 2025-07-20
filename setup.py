from setuptools import setup, find_packages
from importlib.metadata import distribution
import os

with open("requirements.txt") as f:
    install_requires = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="lineview",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "lineview=bin.lineview:main",
        ],
    },
    install_requires=install_requires,
    description="A command-line tool to display specific lines from a file or stream.",
    author="dcloutman",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    include_package_data=True,
    zip_safe=False,  # Ensures dependencies are bundled
)
