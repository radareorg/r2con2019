from PySide2.QtCore import Qt, QObject, SIGNAL, Signal
from PySide2.QtWidgets import QWidget, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QVBoxLayout, QButtonGroup, QHBoxLayout, QPushButton
from PySide2.QtGui import QImage, QPixmap, qRgb

SPRITE_SIZE = 8

COLORS = {
	0: qRgb(255, 255, 255),
	1: qRgb(170, 170, 180),
	2: qRgb(85, 85, 85),
	3: qRgb(0, 0, 0)
}


class SpriteFormatException(Exception):
	pass


class SpriteGraphicsItem(QGraphicsPixmapItem):
	def __init__(self, sprite_view):
		super().__init__()
		self._sprite_view = sprite_view

	def _paint_event(self, event):
		x = int(event.pos().x())
		y = int(event.pos().y())
		if x < 0 or x >= SPRITE_SIZE or y < 0 or y >= SPRITE_SIZE:
			return
		self._sprite_view.paint_pixel(x, y)

	def mousePressEvent(self, event):
		super().mousePressEvent(event)
		self._paint_event(event)
		event.accept()

	def mouseMoveEvent(self, event):
		super().mouseMoveEvent(event)
		self._paint_event(event)


class SpriteView(QWidget):
	sprite_edited = Signal()

	def __init__(self, parent):
		super().__init__(parent)
		self._scene = QGraphicsScene(self)
		self._graphics_view = QGraphicsView(self._scene, self)

		layout = QVBoxLayout(self)
		layout.addWidget(self._graphics_view)

		self._pixmap_item = SpriteGraphicsItem(self)
		self._scene.addItem(self._pixmap_item)

		self._image = QImage(SPRITE_SIZE, SPRITE_SIZE, QImage.Format_ARGB32)
		self.sprite = [[0] * SPRITE_SIZE] * SPRITE_SIZE

		button_layout = QHBoxLayout(self)
		layout.addLayout(button_layout)
		self._color_button_group = QButtonGroup(self)
		for color in COLORS:
			button = QPushButton(self)
			button.setCheckable(True)
			button.setText(f"{color}")
			self._color_button_group.addButton(button, color)
			button_layout.addWidget(button)

		self._selected_color = 0
		self._color_button_group.button(self._selected_color).setChecked(True)
		QObject.connect(self._color_button_group, SIGNAL("buttonClicked(int)"), self._color_selected)

		self._update_scaling()

	@property
	def sprite(self):
		return self._sprite

	@sprite.setter
	def sprite(self, sprite):
		if len(sprite) != SPRITE_SIZE:
			raise SpriteFormatException("Invalid Row Count")
		for row in sprite:
			if len(row) != SPRITE_SIZE:
				raise SpriteFormatException("Invalid Column Count")
			for value in row:
				if value not in COLORS:
					raise SpriteFormatException(f"Invalid Color Value {value}")
		self._sprite = sprite
		self._update_image()

	def _update_image(self):
		for row in range(SPRITE_SIZE):
			for column in range(SPRITE_SIZE):
				self._image.setPixel(column, row, COLORS[self._sprite[row][column]])
		pixmap = QPixmap.fromImage(self._image)
		self._pixmap_item.setPixmap(pixmap)

	def resizeEvent(self, *args, **kwargs):
		super().resizeEvent(*args, **kwargs)
		self._update_scaling()

	def showEvent(self, *args, **kwargs):
		super().showEvent(*args, **kwargs)
		self._update_scaling()

	def _update_scaling(self):
		self._graphics_view.fitInView(self._pixmap_item, Qt.KeepAspectRatio)

	def _color_selected(self, id):
		self._selected_color = id

	def paint_pixel(self, x, y):
		if self._sprite[y][x] == self._selected_color:
			return
		self._sprite[y][x] = self._selected_color
		self._update_image()
		self.sprite_edited.emit()

