#!/usr/bin/env bash

set -eo pipefail

# disable TTY allocation
TTY=""
if [[ ! -t 1 ]]; then
  TTY="-T"
fi

DC="${DC:-run}"

function _docker_compose {
  docker compose "${DC}" ${TTY} "${@}"
}

function build {
  : "Build docker compose file"
  docker compose build
}

function build:no-cache {
  : "Build docker compose file (no cache used)"
  docker compose build --no-cache
}

function file_linters {
  : "Run file_linter docker container with docker compose, and runs any command in arguments"
  _docker_compose file_linters "${@}"
}

function format {
  : "Execute File Linters, which are Black, isort, and Flake8"
  printf "\n---Running isort Import Sorter---\n"
  file_linters isort .

  printf "\n---Running Black Code Formatting---\n"
  file_linters black .

  printf "\n---Running flake8 Inspector---\n"
  file_linters flake8 .
}

END_TIME_FORMAT=$"\n\Execution completed in %3lR"

time "${@:-help}"