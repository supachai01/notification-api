#!/bin/bash

function increase_patch_number () {
  patch_version=`echo $1 | sed 's/.*\(.[0-9]\)/\1/'`
  first_portion=`echo $1 | sed 's/\(.*\).[0-9]/\1/'`
  ((patch_version++))
  echo $first_portion$patch_version
}

function get_latest_version_tag () {
#  local latest_version_tag=`git tag -l v*`
  local latest_version_tag=$(git describe --tags `git rev-list --tags --max-count=1`)
  echo $latest_version_tag
}

current_version_tag=$(get_latest_version_tag)
increase_patch_number $current_version_tag
