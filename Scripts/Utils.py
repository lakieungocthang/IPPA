import torch, cv2
from torchvision import transforms
from PIL import Image, ImageQt
import numpy as np
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
transform_classify = transforms.Compose([
    transforms.Resize(size=(224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

transform_generate = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])

de_transfrom_generate = transforms.Compose([
    transforms.Normalize(mean=[-1, -1, -1], std=[2, 2, 2]),  # reverse normalization
    transforms.ToPILImage()  # convert to PIL image
])

def transform_detector(image, input_size=640):
    # # Resize the image to the desired size (e.g., 640x640)
    # image_resized = cv2.resize(image, (input_size, input_size))

    # Normalize the image (YOLO models often normalize pixel values to the range [0, 1])
    image_normalized = image / 255.0

    image_input = np.transpose(image_normalized, (2, 0, 1))  # From HWC to CHW
    image_input = np.expand_dims(image_input, axis=0)  # Add batch dimension

    return image_input

def qpixmap_to_tensor(pixmap, transform, device):
    qimage = pixmap.toImage()

    qimage = qimage.convertToFormat(QImage.Format_RGB888)
    width, height = qimage.width(), qimage.height()
    ptr = qimage.bits()
    ptr.setsize(height * width * 3)
    img_array = np.array(ptr).reshape(height, width, 3)

    frame_pil = Image.fromarray(img_array)

    frame_tensor = transform(frame_pil).unsqueeze(0)
    frame_tensor = frame_tensor.to(device)

    return frame_tensor

def qpixmap_to_pil(pixmap):
    """Convert QPixmap to PIL Image."""
    qimage = pixmap.toImage()
    image = ImageQt.fromqimage(qimage)
    return image

def pil_to_qpixmap(pil_image):
    image = pil_image.convert("RGB")
    data = np.array(image)
    h, w, ch = data.shape
    q_image = QImage(data, w, h, ch * w, QImage.Format_RGB888)
    q_pixmap = QPixmap.fromImage(q_image)
    return q_pixmap

def qpixmap_to_cv2(pixmap):
    qimage = pixmap.toImage()
    width = qimage.width()
    height = qimage.height()
    channels = 4  # Assuming the image has an alpha channel
    buffer = qimage.bits().asstring(width * height * channels)
    image = np.frombuffer(buffer, dtype=np.uint8).reshape((height, width, channels))
    image = image[:, :, :3]
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    return image_rgb

def cv2_to_qpixmap(cv_img):
    h, w, ch = cv_img.shape
    bytes_per_line = ch * w
    convert_to_Qt_format = QImage(cv_img.data, w, h, bytes_per_line, QImage.Format_RGB888)
    p = convert_to_Qt_format.scaled(640, 480, Qt.KeepAspectRatio)
    return QPixmap.fromImage(p)