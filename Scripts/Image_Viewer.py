import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class ImageViewer(QGraphicsView):
    updatedImageSignal = pyqtSignal(QPixmap)
    sizeSignal = pyqtSignal(int, int)
    def __init__(self):
        super().__init__()

        self.image = QPixmap()
        self.edited_image = QPixmap()

        self.SetupScene()
        self.SetupItem()
        self.SetupZoom()
        self.SetupDraw()
        self.SetupPen()

# ==========================================Setup=======================================================

    def SetupScene(self):
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setMouseTracking(True)
        self.setInteractive(True)

    def SetupItem(self):
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)

    def SetupZoom(self):
        self.zoom_scale = 0
        self.scale(1, 1)
        self.pan = False
        self.pan_start_x = 0
        self.pan_start_y = 0

    def ResetZoom(self):
        self.fitInView(self.pixmap_item, Qt.KeepAspectRatio)

    def SetupDraw(self):
        self.draw_flag = False
        self.drawing = False
        self.alt_flag = False
        self.free_flag = False
        self.ellipse_flag = False
        self.rectangle_flag = False
        self.crop_flag = False
        self.draw_mode = ""
        self.ResetDraw()

    def ResetDraw(self):
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.draw_point1 = QPoint()
        self.draw_point2 = QPoint()

    def SetupPen(self):
        self.color = Qt.red
        self.thickness = 3
        self.pen_style = Qt.SolidLine

# ==========================================Key/Mouse events=======================================================

    def altPressedEvent(self, p_signal):
        if p_signal:
            self.alt_flag = True
            self.setDragMode(QGraphicsView.ScrollHandDrag)
        else:
            self.alt_flag = False
            self.setDragMode(QGraphicsView.NoDrag)

    def wheelEvent(self, event):
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
            self.zoom_scale += 1
        else:
            zoom_factor = zoom_out_factor
            self.zoom_scale -= 1

        if self.zoom_scale > 10:
            self.zoom_scale = 10
            return
        elif self.zoom_scale < -10:
            self.zoom_scale = -10
            return

        self.scale(zoom_factor, zoom_factor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.pan = True
            self.pan_start_x = event.x()
            self.pan_start_y = event.y()

        if event.button() == Qt.LeftButton:
            self.drawing = True
            if self.drawing and self.draw_flag and not self.alt_flag:
                if self.draw_mode == "free_style":
                    if self.start_point.isNull():
                        self.start_point = self.mapToScene(event.pos()).toPoint()
                    if self.draw_point1.isNull():
                        self.draw_point1 = self.mapToScene(event.pos()).toPoint()
                    else:
                        self.draw_point2 = self.mapToScene(event.pos()).toPoint()
                        self.DrawLine(self.draw_point1, self.draw_point2)
                elif self.draw_mode == "ellipse":
                    if self.start_point.isNull():
                        self.start_point = self.mapToScene(event.pos()).toPoint()
                elif self.draw_mode == "rectangle":
                    if self.start_point.isNull():
                        self.start_point = self.mapToScene(event.pos()).toPoint()
                elif self.draw_mode == "crop":
                    if self.start_point.isNull():
                        self.start_point = self.mapToScene(event.pos()).toPoint()

        if event.button() == Qt.RightButton:
            self.ResetDraw()

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.pan = False

        if event.button() == Qt.LeftButton:
            self.drawing = False
            if self.draw_mode == "ellipse":
                self.UpdateEllipse(p_finish=True)
                self.ResetDraw()
            elif self.draw_mode == "rectangle":
                self.UpdateRectangle(p_finish=True)
                self.ResetDraw()
            elif self.draw_mode == "crop":
                self.UpdateCrop(p_finish=True)
                self.ResetDraw()
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self.pan:
            delta_x = event.x() - self.pan_start_x
            delta_y = event.y() - self.pan_start_y
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta_x)
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta_y)
            self.pan_start_x = event.x()
            self.pan_start_y = event.y()

        if self.drawing and self.draw_flag and not self.alt_flag:
            match self.draw_mode:
                case "free_style":
                    self.DrawLine(self.draw_point1, self.mapToScene(event.pos()).toPoint())
                case "ellipse":
                    self.end_point = self.mapToScene(event.pos()).toPoint()
                    self.UpdateEllipse()
                case "rectangle":
                    self.end_point = self.mapToScene(event.pos()).toPoint()
                    self.UpdateRectangle()
                case "crop":
                    self.end_point = self.mapToScene(event.pos()).toPoint()
                    self.UpdateCrop()
        super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.DrawLine(self.draw_point2, self.start_point)
            self.ResetDraw()

# ==========================================Body=======================================================

    def SetImage(self, p_image):
        self.image = p_image
        self.edited_image = p_image
        self.SetupZoom()

    def SetDrawMode(self, p_mode):
        if p_mode == None:
            self.DisableDrawing()
            self.DisplayImage()
            self.GetSize(self.edited_image)
        else:
            self.draw_mode = p_mode
            self.EnableDrawing()

    def SetColor(self, p_color):
        self.color = p_color

    def SetThickness(self, p_thickness):
        self.thickness = p_thickness

    def SetPenStyle(self, p_pen_style):
        self.pen_style = p_pen_style

    def DisplayImage(self):
        self.pixmap_item.setPixmap(self.edited_image)
        self.setSceneRect(self.pixmap_item.boundingRect())
        self.ResetZoom()

    def GetSize(self, p_image):
        self.sizeSignal.emit(p_image.width(), p_image.height())

    def SaveImage(self):
        self.image = self.edited_image
        self.updatedImageSignal.emit(self.image)

    def EnableDrawing(self):
        self.draw_flag = True

    def DisableDrawing(self):
        self.draw_flag = False
        self.ResetDraw()

# ---------------------------------------------Transform-----------------------------------------------------

    def Crop(self):
        self.edited_image = self.edited_image.copy(self.rect)
        self.rect = QRect()
        self.DisplayImage()
        self.GetSize(self.edited_image)

    def ApplyMask(self, p_mask):
        mask = p_mask.scaled(self.edited_image.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        bitmap_mask = mask.createMaskFromColor(QColor(0, 0, 0), Qt.MaskInColor)
        self.edited_image.setMask(bitmap_mask)

    def ResizeIgnoreRatio(self, p_size):
        self.edited_image = self.edited_image.scaled(p_size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        self.DisplayImage()
        self.GetSize(self.edited_image)

    def ResizeToWidth(self, p_width):
        self.edited_image = self.edited_image.scaledToWidth(p_width, Qt.SmoothTransformation)
        self.DisplayImage()
        self.GetSize(self.edited_image)

    def ResizeToHeight(self, p_height):
        self.edited_image = self.edited_image.scaledToHeight(p_height, Qt.SmoothTransformation)
        self.DisplayImage()
        self.GetSize(self.edited_image)

    def RotateClockWise(self):
        self.edited_image = self.edited_image.transformed(QTransform().rotate(90))

    def RotateAntiClockWise(self):
        self.edited_image = self.edited_image.transformed(QTransform().rotate(-90))

    def FlipHorizontal(self):
        self.edited_image = self.edited_image.transformed(QTransform().scale(-1, 1))

    def FlipVertical(self):
        self.edited_image = self.edited_image.transformed(QTransform().scale(1, -1))

# ----------------------------------------------------------Edit--------------------------------------------------

    def DrawLine(self, point1, point2):
        painter = QPainter(self.edited_image)
        pen = QPen(self.color, self.thickness, self.pen_style)
        painter.setPen(pen)
        painter.drawLine(point1, point2)
        self.draw_point1 = point2
        self.pixmap_item.setPixmap(self.edited_image)

    def UpdateCrop(self, p_finish=False):
        temp = self.edited_image.copy()
        painter = QPainter(temp)
        pen = QPen(Qt.black, 3, Qt.DashLine)
        painter.setPen(pen)
        if self.start_point and self.end_point:
            self.rect = QRect(self.start_point, self.end_point).normalized()
            painter.drawRect(self.rect)
            if p_finish:
                self.GetSize(self.rect)
        painter.end()
        self.pixmap_item.setPixmap(temp)

    def UpdateRectangle(self, p_finish=False):
        temp = self.edited_image.copy()
        painter = QPainter(temp)
        pen = QPen(self.color, self.thickness, self.pen_style)
        painter.setPen(pen)
        if self.start_point and self.end_point:
            rectF = QRectF(self.start_point, self.end_point).normalized()
            painter.drawRect(rectF)
        painter.end()

        self.pixmap_item.setPixmap(temp)
        if p_finish:
            self.edited_image = temp

    def UpdateEllipse(self, p_finish=False):
        temp = self.edited_image.copy()
        painter = QPainter(temp)
        pen = QPen(self.color, self.thickness, self.pen_style)
        painter.setPen(pen)
        if self.start_point and self.end_point:
            rectF = QRectF(self.start_point, self.end_point).normalized()
            painter.drawEllipse(rectF)
        painter.end()

        self.pixmap_item.setPixmap(temp)
        if p_finish:
            self.edited_image = temp
    
    def DrawBox(self, point1, point2, label_text=""):
        temp = self.edited_image.copy()
        painter = QPainter(temp)
        
        # Define pen for the box
        color = Qt.green
        thickness = 5
        pen_style = Qt.SolidLine
        pen = QPen(color, thickness, pen_style)
        painter.setPen(pen)

        # Draw the rectangle
        if point1 and point2:
            rect = QRectF(QPointF(point1[0], point1[1]), QPointF(point2[0], point2[1])).normalized()
            painter.drawRect(rect)
            
            # Set font for the label text
            font = QFont("Arial", 18, QFont.Bold)
            painter.setFont(font)
            # painter.setPen(QPen(Qt.black))  # Text color

            # Calculate text position (top-left corner of the box)
            text_rect = painter.boundingRect(rect, Qt.AlignCenter, label_text)
            text_x = rect.left() + (rect.width() - text_rect.width()) / 2
            text_y = rect.top()  - text_rect.height() - 2

            # Draw the text
            painter.drawText(QPointF(text_x, text_y + text_rect.height() / 2), label_text)

        painter.end()

        self.pixmap_item.setPixmap(temp)
        self.edited_image = temp