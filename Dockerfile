FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Ho_Chi_Minh

RUN apt-get update && apt-get install -y \
    openssh-server \
    openssh-client \
    autossh \
    python3 \
    python3-pip \
    python3-venv \
    python3-flask \
    wget \
    ffmpeg \
    curl \
    nano \
    git \
    neofetch \
    htop \
    screen \
    ffmpeg \
    tzdata \
    tmate \
    # speedtest-cli \
    build-essential \
    automake \
    pkg-config \
    libevent-dev \
    libncurses5-dev \
    bison \
    # iputils-ping \
    lynx \
    zip \
    unzip \
    # unrar \
    # genisoimage \
    xz-utils \
    # qemu-system-x86 \
    tor \
    torsocks \
    # ruby-full \
    zlib1g-dev \
    # nodejs \
    # npm \
    # nginx \
    gpg \
    # imagemagick \
    # webp \
    curl \
    libssl-dev \
    libreadline-dev \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && dpkg-reconfigure -f noninteractive tzdata

# Install latest tmux
RUN wget https://github.com/tmux/tmux/releases/download/3.4/tmux-3.4.tar.gz \
    && tar xf tmux-3.4.tar.gz \
    && cd tmux-3.4 \
    && ./configure && make \
    && make install \
    && cd .. \
    && rm -rf tmux-3.4 tmux-3.4.tar.gz

# Create a virtual environment and install Flask
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# RUN pip3 install flask Flask-Caching Werkzeug psutil schedule Pillow requests aiohttp numpy moviepy opencv-python-headless python-dotenv discord.py deep_translator pexpect cryptography qrcode openpyxl stem configparser cloudscraper selenium webdriver_manager playwright beautifulsoup4 fake-useragent PySocks pyppeteer pyppeteer_stealth pycryptodome pyfiglet pyDes gtts pydub SpeechRecognition pysrt undetected-chromedriver mistralai aider-chat aiofiles matplotlib

#RUN playwright install chromium
# Cài đặt ngrok
# RUN curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && \
#     echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | tee /etc/apt/sources.list.d/ngrok.list && \
#     apt-get update && apt-get install -y ngrok

# RUN mkdir -p /root/.config/ngrok && echo "version: \"2\"" > /root/.config/ngrok/ngrok.yml

# RUN mkdir -p /home/ubuntu/.config/ngrok && echo "version: \"2\"" > /root/.config/ngrok/ngrok.yml

COPY web_status.py .
#COPY wine.sh .
COPY run.sh .

COPY id_sf-lsd-segfault-net .
COPY config .

#RUN bash wine.sh
RUN python3 -m venv /root/venv

RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Cấp quyền thực thi cho tệp kịch bản khởi động
RUN chmod +x run.sh

# Mở cổng 80 để truy cập web
EXPOSE 80

# Chạy kịch bản khởi động khi container bắt đầu
CMD ["./run.sh"]

#CMD ["python3", "web_status.py"]