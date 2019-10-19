#!/usr/bin/env python
"""The setup script."""
from itertools import chain
from pathlib import Path
from typing import Dict, List

import setuptools
from setuptools import find_packages
from setuptools import setup

# Parse requirements files
REQS = {
    pip_name: pip_lines
    for pip_name, pip_lines in map(
        lambda p: (p.stem.upper(), p.open().read().splitlines()),
        Path().glob(pattern="requirements/*.pip"),
    )
}  # type: Dict[str, List[str]]
# TODO: perform more complex substitution/eval (regexp, jinja, ...)
# https://stackoverflow.com/questions/952914/how-to-make-a-flat-list-out-of-list-of-lists
# https://stackoverflow.com/a/952952
# https://docs.python.org/2/library/itertools.html#itertools.chain.from_iterable
REQS["BASE_ALL"] = list(
    chain.from_iterable([REQS[k] for k in filter(lambda k: "BASE" in k, REQS)])
)

path_dependency_links = Path("requirements/dependency_links")
DEPENDENCY_LINKS = path_dependency_links.open().read().splitlines() if path_dependency_links.exists() else []

long_description = Path("README.md").read_text()

# Find if user has spacy available
try:
    from spacy import __version__

    SPACY_INSTALLED = True
except ImportError:
    SPACY_INSTALLED = False


class DownloadSpacyMatchingModel(setuptools.Command):
    """Command downloading spaCy matching model."""

    description = "download spaCy matching model"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        if SPACY_INSTALLED:
            # https://stackoverflow.com/questions/18421757/live-output-from-subprocess-command
            import subprocess
            import sys

            process = subprocess.Popen(
                "python -m spacy download en_core_web_sm".split(),
                stdout=subprocess.PIPE,
            )
            for line in process.stdout:
                sys.stdout.write(line.decode("utf-8"))
        else:
            raise ModuleNotFoundError(
                "spacy is needed in order to " "download spaCy matching model"
            )


setup(
    name="pyconfr_2019_grpc_nlp_server_tweet_features",
    author="Lionel ATTY",
    author_email="yoyonel@hotmail.com",
    url="https://github.com/yoyonel/pyconfr_2019_grpc_nlp_server_tweet_features.git",
    use_scm_version=True,
    description="",
    # https://packaging.python.org/guides/making-a-pypi-friendly-readme/
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={},
    include_package_data=True,
    install_requires=REQS["BASE_ALL"],
    setup_requires=REQS["SETUP"],
    extras_require={
        "test": REQS["BASE_ALL"] + REQS["TEST"],
        "develop": REQS["BASE_ALL"] + REQS["TEST"] + REQS["DEV"],
        "docs": REQS["DOCS"]
    },
    dependency_links=DEPENDENCY_LINKS,
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    python_requires=">=3.6",
    cmdclass={
        "download_spacy_matching_model": DownloadSpacyMatchingModel,
    },
    entry_points={
        "console_scripts": [
            # RPC Server Storage
            "pyconfr_2019_grpc_nlp_server_tweet_features = tweet_features.tweet_features_server:main"
        ]
    },
    # https://github.com/pypa/sample-namespace-packages/issues/6
    zip_safe=False,
)
