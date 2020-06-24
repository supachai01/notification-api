#!/bin/bash

function increase_patch_number () {
  patch_version=`echo $1 | sed 's/\(.*[0-9]\.\)\([0-9]\)/\2/'`
  first_portion=`echo $1 | sed 's/\(.*[0-9]\.\)\([0-9]\)/\1/'`

  if [[ $patch_version =~ [0-9] ]];then
    echo "Invalid patch version: $1"
    exit 1
  else
    ((patch_version++))
    result=$first_portion$patch_version
  fi
  echo $result
}

function get_latest_version_tag () {
  local latest_version_tag=$(git describe --tags `git rev-list --tags --max-count=1`)
  if [ -z "$latest_version_tag" ]; then
    latest_version_tag="rc-0.0.0"
  fi
  echo $latest_version_tag
}

current_version_tag=$(get_latest_version_tag)
increase_patch_number $current_version_tag
