#!/bin/bash

# Cập nhật hệ thống
apt update && apt upgrade -y

# Kích hoạt kiến trúc 32-bit
dpkg --add-architecture i386

# Thêm kho lưu trữ WineHQ
mkdir -pm755 /etc/apt/keyrings
wget -O /etc/apt/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key

# Thêm kho lưu trữ cho Ubuntu 24.04
wget -NP /etc/apt/sources.list.d/ https://dl.winehq.org/wine-builds/ubuntu/dists/noble/winehq-noble.sources

# Cập nhật lại danh sách gói
apt update

# Cài đặt Wine
apt install --install-recommends winehq-stable -y

# Xác minh cài đặt
wine --version

# Thiết lập biến môi trường WINEPREFIX
export WINEPREFIX=~/.wine

# Khởi tạo tiền tố Wine
wineboot --init

# Cài đặt winetricks
apt install winetricks -y

# Cài đặt một số thư viện phổ biến (tùy chọn, có thể mất nhiều thời gian)
winetricks corefonts vcrun6 vcrun2005 vcrun2008 vcrun2010 vcrun2012 vcrun2013 vcrun2015 vcrun2017 vcrun2019 dotnet48

echo "Cài đặt Wine hoàn tất."
echo "Để chạy một ứng dụng Windows, sử dụng lệnh: wine /đường/dẫn/đến/ứng_dụng.exe"