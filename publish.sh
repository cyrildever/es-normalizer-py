#!/bin/bash

# Remove former distributions
rm dist/es_normalizer_py-*
rm dist/es-normalizer-py-*

# Publish library to PyPI

python3 -m build
python3 -m twine upload dist/*
