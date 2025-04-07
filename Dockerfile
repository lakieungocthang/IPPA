FROM nvidia/cuda:12.2.0-devel-ubuntu22.04
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Ho_Chi_Minh
RUN apt update && apt install -y \
    python3.10 python3-pip git \
    libgl1-mesa-glx tzdata libxkbcommon-x11-0 x11-utils x11-xserver-utils \
    libxcb-xinerama0 libxcb-cursor0 libxcb-xinput0 \
    libxcb-shape0 libxcb-shm0 libxcb-glx0 libxcb-xfixes0 \
    libglib2.0-0 libx11-xcb1 libfontconfig1 \
    libxcb-icccm4 libxcb-util1 libxcb-render0 libxcb-randr0 \
    mesa-utils x11-apps \
    qtbase5-dev qtchooser qt5-qmake qttools5-dev-tools \
    && rm -rf /var/lib/apt/lists/*
RUN ln -sf /usr/bin/python3.10 /usr/bin/python
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip && pip install -r requirements.txt
ENV QT_QPA_PLATFORM=xcb
CMD ["python", "main.py"]