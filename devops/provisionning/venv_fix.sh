#!/bin/bash
cd /home/
mkdir venvs
cd venvs
pyvenv --without-pip myenv
source myenv/bin/activate
curl https://bootstrap.pypa.io/get-pip.py | python
deactivate
source myenv/bin/activate