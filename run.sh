#!/bin/sh

# Đặt biến môi trường cho autossh để thử kết nối lại vô hạn
export AUTOSSH_GATETIME=0

# Tạo thư mục .ssh nếu chưa tồn tại
mkdir -p ~/.ssh

# Sao chép file cấu hình SSH đã được copy vào từ Dockerfile
cp config ~/.ssh/config

# Sao chép và thiết lập quyền cho SSH key
cp id_sf-lsd-segfault-net ~/.ssh/id_sf-lsd-segfault-net
chmod 600 ~/.ssh/id_sf-lsd-segfault-net

# Bắt đầu kết nối autossh ở chế độ nền.
# -M 0: Không dùng cổng giám sát, dựa vào ServerAliveInterval.
# -f: Chạy nền.
# -N: Không thực thi lệnh từ xa.
echo "Starting autossh connection for kali..."
autossh -M 0 -f -N kali

echo "Starting autossh connection for kali2..."
autossh -M 0 -f -N kali2

# Chạy ứng dụng web của bạn
echo "Starting web_status.py..."
python3 web_status.py