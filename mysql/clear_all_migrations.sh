#!/bin/bash

PWD=$(pwd)
file_dir=$(dirname $0)
cd "$PWD/$file_dir/../"

find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc"  -delete
