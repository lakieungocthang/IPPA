# Hướng dẫn cài đặt dự án trên máy local

## **Yêu cầu**  
- Python **3.10**
- `pip` mới nhất  
- `git` để clone các thư viện từ GitHub 

## **Cài đặt thư viện**  

Sau khi đã có Python 3.10, chạy lệnh sau để cài đặt tất cả thư viện trong requirements.txt bên dưới:

```bash
pip install --upgrade pip  
pip install -r requirements.txt
```
Dưới đây là nội dung file requirements.txt:
```txt
addict==2.4.0
asttokens==3.0.0
attrs==25.1.0
beautifulsoup4==4.13.3
blinker==1.9.0
boxmot @ git+https://github.com/mikel-brostrom/BoxMOT.git@b2950d285e699d177d37f527ef85665bbe6a6091
certifi==2025.1.31
charset-normalizer==3.4.1
click==8.1.8
comm==0.2.2
ConfigArgParse==1.7
contourpy==1.3.1
cycler==0.12.1
darkdetect==0.7.1
dash==2.18.2
dash-core-components==2.0.0
dash-html-components==2.0.0
dash-table==5.0.0
decorator==5.2.1
exceptiongroup==1.2.2
executing==2.2.0
fastjsonschema==2.21.1
filelock==3.17.0
filterpy==1.4.5
Flask==3.0.3
fonttools==4.56.0
fsspec==2025.2.0
ftfy==6.3.1
gdown==5.2.0
gitdb==4.0.12
GitPython==3.1.44
idna==3.10
importlib_metadata==8.6.1
ipython==8.33.0
ipywidgets==8.1.5
itsdangerous==2.2.0
jedi==0.19.2
Jinja2==3.1.5
joblib==1.4.2
jsonschema==4.23.0
jsonschema-specifications==2024.10.1
jupyter_core==5.7.2
jupyterlab_widgets==3.0.13
kiwisolver==1.4.8
lapx==0.5.11.post1
loguru==0.7.3
lxml==5.3.1
MarkupSafe==3.0.2
matplotlib==3.10.1
matplotlib-inline==0.1.7
mpmath==1.3.0
narwhals==1.28.0
nbformat==5.10.4
nest-asyncio==1.6.0
networkx==3.4.2
numpy==1.26.4
nvidia-cublas-cu12==12.1.3.1
nvidia-cuda-cupti-cu12==12.1.105
nvidia-cuda-nvrtc-cu12==12.1.105
nvidia-cuda-runtime-cu12==12.1.105
nvidia-cudnn-cu12==8.9.2.26
nvidia-cufft-cu12==11.0.2.54
nvidia-curand-cu12==10.3.2.106
nvidia-cusolver-cu12==11.4.5.107
nvidia-cusparse-cu12==12.1.0.106
nvidia-nccl-cu12==2.19.3
nvidia-nvjitlink-cu12==12.8.61
nvidia-nvtx-cu12==12.1.105
open3d==0.19.0
opencv-python==4.10.0.84
packaging==24.2
pandas==2.2.3
parso==0.8.4
pexpect==4.9.0
pillow==10.4.0
platformdirs==4.3.6
plotly==6.0.0
prompt_toolkit==3.0.50
psutil==7.0.0
ptyprocess==0.7.0
pure_eval==0.2.3
py-cpuinfo==9.0.0
pydicom==2.4.4
Pygments==2.19.1
pyparsing==3.2.1
PyQt5==5.15.11
PyQt5-Qt5==5.15.16
PyQt5_sip==12.17.0
pyqtdarktheme==2.1.0
pyquaternion==0.9.9
PySocks==1.7.1
python-dateutil==2.9.0.post0
python-docx==1.1.2
pytz==2025.1
PyYAML==6.0.2
referencing==0.36.2
regex==2024.11.6
requests==2.32.3
retrying==1.3.4
rpds-py==0.23.1
scikit-learn==1.6.1
scipy==1.15.2
seaborn==0.13.2
six==1.17.0
smmap==5.0.2
soupsieve==2.6
stack-data==0.6.3
sympy==1.13.3
threadpoolctl==3.5.0
torch==2.2.2
torchvision==0.17.2
tqdm==4.67.1
traitlets==5.14.3
triton==2.2.0
typing_extensions==4.12.2
tzdata==2025.1
ultralytics==8.2.66
ultralytics-thop==2.0.14
urllib3==2.3.0
wcwidth==0.2.13
Werkzeug==3.0.6
widgetsnbextension==4.0.13
yacs==0.1.8
zipp==3.21.0
```

## **Fix bug hiện có trong dự án**
Vào file **./Ai/Track/StrongSort.py** thự hiện comment dòng 8 **from boxmot.utils import PerClassDecorator** và xóa annotation **@PerClassDecorator** ở hàm **update()**. Sau đó thực hiện gỡ các comment ở chức năng tracking trong file **./Scripts/App.py**


# Hướng dẫn sử dụng Docker cho Dự án

Cần cài đặt NVIDIA Container Toolkit trước.

## Dockerfile

```dockerfile
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
```
## Cách build Docker Image

```bash
docker build -t ippa .
```

# Cho phép truy cập X server

```bash
xhost +local:root
```

## Chạy container trên GPU (nếu có NVIDIA GPU)

```bash
docker run --rm -it \
    --gpus all \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    ippa
```