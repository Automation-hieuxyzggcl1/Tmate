#!/bin/sh

# Tạo thư mục .ssh nếu chưa tồn tại
mkdir -p ~/.ssh

# Sao chép file cấu hình SSH đã được copy vào từ Dockerfile
cp config ~/.ssh/config

# Sao chép và thiết lập quyền cho SSH key
cp id_sf-lsd-segfault-net ~/.ssh/id_sf-lsd-segfault-net
chmod 600 ~/.ssh/id_sf-lsd-segfault-net

# Bắt đầu kết nối SSH ở chế độ nền
ssh -N kali &
ssh -N kali2 &

python3 web_status.py