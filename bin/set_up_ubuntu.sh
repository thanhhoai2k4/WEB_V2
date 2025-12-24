#!/bin/bash

# Tạo môi trường ảo bằng python3
python3 -m venv venv

# Hàm kích hoạt và cài đặt
activate () {

#  sudo apt update
#  sudo apt install python3-dev libpq-dev

  # Đường dẫn đúng trên Ubuntu/Linux là bin/activate
  source venv/bin/activate

  echo "Installing requirements to virtual environment..."
  pip install --upgrade pip
  pip install -r requirements.txt
}

activate