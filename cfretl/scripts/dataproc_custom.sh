#!/bin/bash

set -exo pipefail

function install_pip() {
  if command -v pip >/dev/null; then
    echo "pip is already installed."
    return 0
  fi

  if command -v easy_install >/dev/null; then
    echo "Installing pip with easy_install..."
    easy_install pip
    return 0
  fi

  echo "Installing python-pip..."
  apt update
  apt install python-pip -y
}

function main() {
    install_pip
    pip install --upgrade scikit-learn==0.22 google-cloud-bigquery==1.21.0 pandas==0.25.3 numpy==1.17.3 sklearn-porter==0.7.4  ipython==7.9.0 ipython-genutils==0.2.0 matplotlib==3.1.2
}

main
