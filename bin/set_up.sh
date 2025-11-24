#!/bin/bash
# Chạy trực tiếp trên gitbash  để được full quyền.

python -m venv venv
activate () {
  . venv/Scripts/activate
  echo "installing requirements to virtual environment"
  pip install -r requirements.txt
}
activate