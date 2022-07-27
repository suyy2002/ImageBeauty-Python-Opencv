
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QWheelEvent
from PyQt5.QtWidgets import QGraphicsView

class GraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(self.AnchorUnderMouse)

    def wheelEvent(self, e: QWheelEvent):
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        if e.angleDelta().y() > 0:
            self.scale(1.1, 1.1)
        else:
            self.scale(1 / 1.1, 1 / 1.1)
        self.setTransformationAnchor(self.AnchorUnderMouse)
