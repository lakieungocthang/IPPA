import open3d as o3d
import numpy as np
import cv2
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer

class PointCloudViewer(QWidget):
    def __init__(self):
        super().__init__()
    
    def Initialize(self):
        self.vis = o3d.visualization.Visualizer()
        self.vis.create_window(window_name="3D Point Cloud Viewer", width=800, height=600, visible=True)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_vis)
        self.timer.start(1)

    def load_and_plot_point_cloud(self, rgb_image, depth_image):
        depth_image = cv2.resize(depth_image, rgb_image.shape[1::-1])
        fx = 500.0
        fy = 500.0
        cx = depth_image.shape[1] // 2
        cy = depth_image.shape[0] // 2

        rows, cols = depth_image.shape
        c, r = np.meshgrid(np.arange(cols), np.arange(rows), sparse=True)
        z = depth_image

        x = (c - cx) * z / fx
        y = (r - cy) * z / fy

        points = np.stack((x, y, z), axis=-1).reshape(-1, 3)
        colors = rgb_image.reshape(-1, 3) / 255.0

        mask = z > 0
        points = points[mask.reshape(-1)]
        colors = colors[mask.reshape(-1)]

        # Tạo point cloud
        pc = o3d.geometry.PointCloud()
        pc.points = o3d.utility.Vector3dVector(points)
        pc.colors = o3d.utility.Vector3dVector(colors)

        self.vis.add_geometry(pc)

    def update_vis(self):
        if self.vis.poll_events():
            self.vis.update_renderer()
        else:
            self.timer.stop()
            self.close()

    def clear(self):
        self.vis.clear_geometries()

    def close(self):
        self.vis.destroy_window()
