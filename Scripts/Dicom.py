import pydicom
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import ExplicitVRLittleEndian, generate_uid
import cv2
import numpy as np
from Scripts.Utils import *
from Scripts.Message import *

class Dicom():
    def __init__(self):
        self.ds = FileDataset("output.dcm", {}, file_meta=Dataset(), preamble=b"\0" * 128)

        self.ds.file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
        self.ds.is_little_endian = True
        self.ds.is_implicit_VR = False

    def InitializeDicomBasicData(self, p_image_data):
        list_images = p_image_data.ListImages()
        list_images = [qpixmap_to_cv2(image) for image in list_images if not image.isNull()]
        self.images = self.PadImages2SameSize(list_images)
        
        self.ds.PatientName = "Test^Patient"
        self.ds.PatientID = "123456"
        self.ds.StudyInstanceUID = generate_uid()
        self.ds.SeriesInstanceUID = generate_uid()
        self.ds.SOPInstanceUID = generate_uid()
        self.ds.SOPClassUID = generate_uid()

        self.ds.PerFrameFunctionalGroupsSequence = []
        self.ds.NumberOfFrames = len(self.images)
        self.ds.Rows = self.images[0].shape[0]
        self.ds.Columns = self.images[0].shape[1]
        self.ds.PhotometricInterpretation = "RGB"
        self.ds.SamplesPerPixel = 3
        self.ds.PlanarConfiguration = 0
        self.ds.BitsAllocated = 8
        self.ds.BitsStored = 8
        self.ds.HighBit = 7
        self.ds.PixelRepresentation = 0

        self.ds.PixelData = b""

    def PadImages2SameSize(self, p_images):
        max_height = max(image.shape[0] for image in p_images)
        max_width = max(image.shape[1] for image in p_images)

        padded_images = []
        for image in p_images:
            scaled_image = cv2.resize(image, (max_width, max_height), interpolation=cv2.INTER_CUBIC)
            padded_images.append(scaled_image)

        return np.stack(padded_images)

    def CreateCustomAttributes(self, custom_attributes):
        group = Dataset()
        base_key = custom_attributes[0]
        base_value = custom_attributes[1]
        base_element_number = 0x1000
        private_tag = pydicom.tag.Tag(0x0043, base_element_number)
        group.add_new(private_tag, 'LO', f"{base_key}:")
        for idx, (key, value) in enumerate(base_value.items()):
            private_tag = pydicom.tag.Tag(0x0043, base_element_number + idx + 1)
            group.add_new(private_tag, 'LO', f"{key}: {value}")
        
        return group

    def SetCustomAttributes(self, p_image_data):
        custom_attributes_list = p_image_data.ListAttributes()
        for image in self.images:
            self.ds.PixelData += image.tobytes()
        for custom_attributes in custom_attributes_list.items():
            functional_group = self.CreateCustomAttributes(custom_attributes)
            self.ds.PerFrameFunctionalGroupsSequence.append(functional_group)
            

    def SaveDicomFile(self, p_file_name, p_image_data):
        self.InitializeDicomBasicData(p_image_data)
        self.SetCustomAttributes(p_image_data)
        self.ds.save_as(f"{p_file_name}.dcm")
        Inform("Information:", "Saved file successfully!")