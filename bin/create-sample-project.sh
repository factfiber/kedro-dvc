#!/bin/bash
# create a test project under ./tmp which uses the kedro-dvc plugin as 
# "editable" install.
#
set -e

name=$1
from_branch=${2:-sample-project-basic}

if [[ "$name" == "" ]] ; then
  echo "usage: setup-sample-project.sh <name> [from-branch]"
  exit 1
fi
# echo "creating sample project $name from branch $from_branch"

python -m kedro_dvc.create_sample_project $name $from_branch
# mkdir -p tmp
# cd tmp
# mkdir $name
# cd $name
# git clone https://github.com/FactFiber/kedro-dvc.git -b $from_branch .
# python3.8 -m venv env/$name
# source env/$name/bin/activate
# pip install --upgrade pip  # ensure pip version >22
# pip install -r src/requirements.txt
# hash -r # ensure shell notes local version of kedro
pushd tmp/$name && kedro --help || true && popd
# we should see kedro-dvc commands listed
echo "to use the sample project, cd to tmp/$name, run "\""source env/$name/bin/activate"\"""
