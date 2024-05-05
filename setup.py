"""Build gpsd Python package for PyPI.

This file is Copyright by the GPSD project
SPDX-License-Identifier: BSD-2-clause
"""

# This code runs compatibly under Python 2 and 3.x for x >= 2.
# Preserve this property!
from pathlib import Path

try:
    from setuptools import setup
except ImportError:  # No setuptools in Python 2
    from distutils.core import setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.markdown").read_text()

setup(
    name="gps-sizzle",
    version="2024.5.5",
    description="a standalone fork of tools originally from GPSD",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://github.com/JamesB192/gpsd-sizzle.git",
    author="James Browning",
    author_email="JamesB.fo80@gmail.com",
    maintainer="James Browning",
    maintainer_email="JamesB.fo80@gmail.com",
    license="BSD-2-Clause License",
    packages=["gps"],
    project_urls={
        "Bug Tracker": "https://github.com/jamesb192/gps-sizzle",
        "IRC": "https://web.libera.chat/",
        "Project": "https://github.com/jamesb192/gps-sizzle",
        "tiplink": "https://www.patreon.com/JamesB192",
    },
    scripts=[
        "scripts/gpscat",
        "scripts/gpscsv",
        "scripts/gpsData",
        "scripts/gpsfake",
        "scripts/gpsplot",
        "scripts/gpsprof",
        "scripts/gpssim.py",
        "scripts/gpssubframe",
        "scripts/ntpshmviz",
        "scripts/skyview2svg",
        "scripts/ubxtool",
        "scripts/webgps",
        "scripts/xgps",
        "scripts/xgpsspeed",
        "scripts/zerk",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Programming Language :: Python",
    ],
)
