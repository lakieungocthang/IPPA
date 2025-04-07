from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt

class ImageData:
    def __init__(self):
        self.original_image = QPixmap()
        self.classify_image = QPixmap()
        self.detector_image = QPixmap()
        self.fice_image = QPixmap()
        self.lci_image = QPixmap()

        self.information = {
            "id": "",
            "path": "",
            "name": "",
            "type": "",
            "date": ""
        }
        self.original = {
            "dimension": {
                "width": 0,
                "height": 0
            }
        }
        self.classify = {
            "land-mark": ""
        }
        self.detector = {
            "num-lesion": 0,
            "lesion-data": []
        }
        self.generator = {
            "FICE": "",
            "LCI": ""
        }

    def test(self):
        return self.original_image.isNull()

    def ListAttributes(self):
        return {
            "information": self.information,
            "original": self.original,
            "classify": self.classify,
            "detector": self.detector,
            "generator": self.generator
        }
    
    def ListImages(self):
        list_image = [self.original_image,self.classify_image,self.detector_image,self.fice_image,self.lci_image]
        return [image for image in list_image]

    def find_pixmap_values(self, data=None):
        if data is None:
            data = self.to_dict()

        pixmap_values = []

        def recursive_search(d):
            for key, value in d.items():
                if key == "pixmap":
                    pixmap_values.append(value)
                elif isinstance(value, dict):
                    recursive_search(value)

        recursive_search(data)
        return pixmap_values