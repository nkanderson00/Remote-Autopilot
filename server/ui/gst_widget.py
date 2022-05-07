import sys

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

import gi

gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import Gst, GObject, GstVideo

Gst.init(None)


class VideoWidget(QWidget):

	def __init__(self, flags, *args, **kwargs):
		QMainWindow.__init__(self)
		super().__init__(flags, *args, **kwargs)
		self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)
		self.setGeometry(0, 0, 640, 480)
		self.windowId = self.winId()
		self.setup_pipeline()
		self.start_pipeline()

	def setup_pipeline(self):
		self.pipeline = Gst.Pipeline()
		self.pipeline = "udpsrc port=8000 ! application/x-rtp,encoding-name=(string)JPEG ! rtpjpegdepay ! decodebin ! autovideosink"
		self.pipeline = Gst.parse_launch(self.pipeline)
		bus = self.pipeline.get_bus()
		bus.add_signal_watch()
		bus.enable_sync_message_emission()
		bus.connect('sync-message::element', self.on_sync_message)

	def on_sync_message(self, bus, msg):
		message_name = msg.get_structure().get_name()
		if message_name == 'prepare-window-handle':
			assert self.windowId
			msg.src.set_window_handle(self.windowId)

	def start_pipeline(self):
		self.pipeline.set_state(Gst.State.PLAYING)

	def stop_pipeline(self):
		self.pipeline.set_state(Gst.State.NULL)

	def closeEvent(self, event):
		self.stop_pipeline()
		event.accept()

if __name__ == '__main__':
	app = QApplication(sys.argv)
	win = VideoWidget(Qt.WindowFlags())
	win.show()
	sys.exit(app.exec())
