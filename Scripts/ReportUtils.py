import os
import yaml
import docx
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import docx.opc.constants
import sys
import numpy as np
import cv2
import shutil
from datetime import datetime

type_locations = ["Hầu họng", "Thực quản", "Tâm vị", "Thân vị", "Phình vị",
                  "Hang vị", "Bờ cong lớn", "Bờ cong nhỏ", "Hành tá tràng", "Tá tràng"]
type_diseases = ["Viêm thực quản trào ngược", "Ung thư thực quản",
                 "Viêm dạ dày", "Ung thư dạ dày", "Loét hành tá tràng", "Ton thuong"]
label_det_dict = {
    "Viêm thực quản": "Viêm thực quản trào ngược",
    "Viêm thực quản trào ngược": "Viêm thực quản trào ngược",
    "Viêm dạ dày HP": "Viêm dạ dày",
    "Viêm dạ dày": "Viêm dạ dày",
    "Ung thư dạ dày": "Ung thư dạ dày",
    "Ung thư thực quản": "Ung thư thực quản",
    "Loét hoành tá tràng": "Loét hành tá tràng",
    "Hoành tá tràng": "Hành tá tràng",
    "Ton thuong": "Ton thuong"
}
class Patient:
    def __init__(self, id, name, doctor, start_time, end_time, info, gender, birth_year):
        self.id = id
        self.name = name
        self.doctor = doctor
        self.start_time = start_time.strftime('%Y-%m-%d %H:%M:%S') if len(str(start_time))>0 else start_time
        self.end_time = end_time.strftime('%Y-%m-%d %H:%M:%S') if len(str(end_time))>0 else end_time
        self.info = info
        self.gender = gender
        self.birth_year = birth_year
        
class Folder:
    def __init__(self, path, name, created_date, file_count, size):
        self.path = path
        self.name = name
        self.created_date = created_date
        self.file_count = file_count
        self.size = size
        self.images = []
        self.patient = None

    def __repr__(self):
        return (f"Folder(name={self.name!r}, created_date={self.created_date!r}, "
                f"file_count={self.file_count}, size={self.size}, images len {len(self.images)})")

    def parse_report(self):
        session_file = os.path.join(self.path, 'session.yaml')
        if os.path.exists(session_file):
            session = yaml.safe_load(open(session_file, encoding="utf8"))
            
            self.patient = Patient(
                get_value(session, 'patient_id',''),
                get_value(session, 'patient_name',''),
                get_value(session, 'doctor_name',''),
                get_value(session, 'start_time',''),
                get_value(session, 'end_time',''),
                get_value(session, 'info',''),
                get_value(session, 'gender',''),
                get_value(session, 'birth_year','')
            )

            

def get_value(obj, key_path, default=None):
    """
    Retrieve a value from a nested dictionary-like object using a path.

    :param obj: The dictionary-like object to retrieve the value from.
    :param key_path: A string representing the path to the value, separated by '/'.
    :return: The value at the specified path or None if the path is invalid.
    """
    try:
        # Split the key path into components
        keys = key_path.split('/')
        
        # Traverse the dictionary using the keys
        for key in keys:
            obj = obj[key]
        
        return obj
    except (KeyError, TypeError):
        # Handle cases where the key does not exist or obj is not a dictionary
        return default

class ReportImage:
    def __init__(self, file_path):
        self.file_path = file_path
        self.base_name = os.path.basename(file_path)
        self.yaml_path = file_path.replace('.jpg','.yaml')
        self.boxes = []
        self.selected = False
        self.region = None
        self.regionProbability = 0
        self.label_dict = {}
        self.frame = None
        
    def __repr__(self):
        return (f"Image(base_name={self.base_name!r}")

    def get_short_label(self):
        res = []
        for key, val in self.label_dict.items():
            arr = key.upper().strip().split(' ')
            code = ''.join([item[0] for item in arr]) + ( f'({str(len(val))})' if len(val) > 1 else '' )
            res.append(code)
        return '; '.join(res)

    def parse_yaml(self):
        self.boxes = []
        self.label_dict = {}
        self.regionProbability = 0
        if os.path.exists(self.yaml_path):
            frame = yaml.safe_load(open(self.yaml_path, encoding="utf8"))
            self.frame = frame
            self.region = get_value(frame,'region_clf/result/label' , '')
            self.selected = get_value(frame,'selected' , False)
            if self.region in label_det_dict:
                self.region = label_det_dict[self.region]
            self.regionProbability = get_value(frame,'region_clf/result/probability', 0)
            boxes = get_value(frame,'lesion_det/result', [])
            if boxes is not None:
                for box in boxes:
                    label = get_value(box, 'label')
                    if label in label_det_dict:
                        label = label_det_dict[label]
                    x = float(get_value(box, 'bbox/x'))
                    conf = float(get_value(box, 'confidence'))
                    y = float(get_value(box, 'bbox/y'))
                    width = float(get_value(box, 'bbox/width'))
                    height = float(get_value(box, 'bbox/height'))
                    box_obj = Box(label,conf, x, y, width, height)
                    self.boxes.append(box_obj)
                    if label not in self.label_dict:
                        self.label_dict[label] = []
                    self.label_dict[label].append(box_obj)
    def save_yaml(self):
        if self.selected:
            self.frame['selected'] = True
        with open(self.yaml_path, 'w', encoding="utf8") as file:
            yaml.dump(self.frame, file, default_flow_style=False, sort_keys=False)
class Box:
    def __init__(self, label, conf, x, y, width, height):
        self.label = label.strip()
        self.conf = conf
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)
        self.x2 = self.x + self.width
        self.y2 = self.y + self.height
        self.pt1 = [self.x, self.y]
        self.pt2 = [self.x2, self.y2]

def get_folder_size(folder_path):
    """
    Calculate the total size of all files within the folder.

    Parameters:
    - folder_path (str): Path to the folder.

    Returns:
    - int: Total size of the folder in bytes.
    """
    total_size = 0
    for dirpath, _, filenames in os.walk(folder_path):
        for f in filenames:
            file_path = os.path.join(dirpath, f)
            total_size += os.path.getsize(file_path)
    return total_size

def sort_folders(base_folder_path, sort_by='name'):
    """
    Sort folders in the given directory based on the sorting option.

    Parameters:
    - base_folder_path (str): Path to the directory containing folders.
    - sort_by (str): Criteria for sorting. Options are 'name', 'created_date', 'file_count', or 'size'.

    Returns:
    - List of Folder objects: Each object contains the folder name, creation date, file count, and folder size.
    """

    def get_folder_info(folder_name):
        folder_full_path = os.path.join(base_folder_path, folder_name)
        # Retrieve folder creation time
        created_timestamp = os.path.getctime(folder_full_path)
        created_date = datetime.fromtimestamp(created_timestamp)
        files = os.listdir(folder_full_path)
        # Retrieve number of files in the folder
        num_files = len([f for f in files if os.path.isfile(os.path.join(folder_full_path, f))])
        
        # Retrieve folder size
        folder_size = get_folder_size(folder_full_path)
        
        folder_obj =  Folder(folder_full_path,folder_name, created_date, num_files, folder_size)
        for f in files:
            f_name = f.split('.')[0]
            path = os.path.join(folder_full_path, f)
            yaml_path = os.path.join(folder_full_path, f_name+'.yaml')
            if path.endswith('jpg') and os.path.exists(yaml_path):
                folder_obj.images.append(ReportImage(path))
        # folder_obj.parse_report()

        return folder_obj
    
    # Get list of folders
    try:
        folders = [f for f in os.listdir(base_folder_path) if os.path.isdir(os.path.join(base_folder_path, f))]
    except FileNotFoundError:
        raise ValueError(f"The directory {base_folder_path} does not exist.")
    
    # Retrieve metadata for each folder
    folder_info = [get_folder_info(folder) for folder in folders]
    
    if sort_by == 'name':
        sorted_folders = sorted(folder_info, key=lambda x: x.name)
    elif sort_by == 'created_date':
        sorted_folders = sorted(folder_info, key=lambda x: x.created_date)
    elif sort_by == 'file_count':
        sorted_folders = sorted(folder_info, key=lambda x: x.file_count)
    elif sort_by == 'size':
        sorted_folders = sorted(folder_info, key=lambda x: x.size)
    else:
        raise ValueError("Invalid sort_by value. Choose from 'name', 'created_date', 'file_count', or 'size'.")
    
    # Return sorted folder objects
    return sorted_folders

def convert_size(size):
    """
    Convert a number of bytes into a human-readable format (KB, MB, GB, etc.).
    
    :param size: Size in bytes (integer).
    :return: Human-readable size as a string.
    """
    if size == 0:
        return "0 Bytes"
    
    # Define size units
    units = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    
    # Calculate the appropriate unit
    i = 0
    while size >= 1024 and i < len(units) - 1:
        size /= 1024
        i += 1
    
    # Format the result
    return f"{size:.2f} {units[i]}"

import cv2
import numpy as np

def compute_hsv_histogram(image, size=(256, 256)):
    thumbnail = cv2.resize(image, size)
    # Convert to HSV
    hsv_image = cv2.cvtColor(thumbnail, cv2.COLOR_BGR2HSV)
    # Compute histogram
    hist = cv2.calcHist([hsv_image], [0, 1, 2], None, [16, 16, 16], [0, 180, 0, 256, 0, 256])
    hist = cv2.normalize(hist, hist).flatten()
    return hist

def bhattacharyya_distance(hist1, hist2):
    return cv2.compareHist(hist1, hist2, cv2.HISTCMP_BHATTACHARYYA)


def select_top_k_images(images, k, threshold):
    # item format: [path, box.conf, w, h, histogram, selected]
    # Compute histograms for all images
    # histograms = [compute_hsv_histogram(path) for path in image_paths]
    
    # # Create a list of tuples (score, path, histogram)
    # images = list(zip(scores, image_paths, histograms))
    # # Sort images by score in descending order
    images.sort(reverse=True, key=lambda x: x[-1]*100 + x[1])
    
    selected_images = []
    used_histograms = []
    
    for item in images:
        path, score, w, h, hist, selected = item
        if len(selected_images) >= k:
            break
        if all(bhattacharyya_distance(hist, used_hist) > threshold for used_hist in used_histograms):
            selected_images.append(item)
            used_histograms.append(hist)
    # print ('len images', len(images), len(selected_images))
    return selected_images
