# ==========================================
# APPLICATION METADATA
# Author: Elangovan M / ES Infotech
# Co-Author: Developed in collaboration with AI
# Project: Hikvision Stream Viewer & OEM Configurator
# Made with pride with my AI Collaborator
# Version: 1.3.0 (Clean Viewport & Floating Dialog UI)
# ==========================================

import sys
import os
from urllib.parse import quote

import cv2

from PyQt6.QtCore import QThread, pyqtSignal, Qt, QUrl, QSize
from PyQt6.QtGui import QImage, QPixmap, QFont
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QListWidget, 
    QStackedWidget, QFormLayout, QComboBox, QDialog
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEngineHttpRequest


# ============================================================
# CAMERA RTSP THREAD
# ============================================================
class CameraThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    connection_failed_signal = pyqtSignal(str)

    def __init__(self, ip, port, username, password, channel, parent=None):
        super().__init__(parent)
        self.ip = ip.strip()
        self.port = str(port).strip()
        self.username = username
        self.password = password
        self.channel = str(channel).strip()
        self._run_flag = True
        self._error_emitted = False

    def run(self):
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"
        username = quote(self.username, safe="")
        password = quote(self.password, safe="")

        rtsp_url = (
            f"rtsp://{username}:{password}"
            f"@{self.ip}:{self.port}"
            f"/Streaming/Channels/{self.channel}"
        )

        cap = None
        try:
            cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
            try:
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            except Exception:
                pass

            if not cap.isOpened():
                self._emit_error(
                    "Unable to open the RTSP stream.\n\n"
                    "Please check network connections, credentials, ports, and channel configuration."
                )
                return

            while self._run_flag:
                ret, frame = cap.read()
                if not self._run_flag:
                    break
                if not ret or frame is None:
                    self._emit_error("The RTSP video connection was interrupted.")
                    break

                try:
                    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    height, width, channels = rgb_image.shape
                    bytes_per_line = channels * width
                    
                    qt_image = QImage(
                        rgb_image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888
                    ).copy()

                    self.change_pixmap_signal.emit(qt_image)
                except Exception as frame_error:
                    self._emit_error(f"Video frame processing error:\n\n{frame_error}")
                    break

        except Exception as error:
            self._emit_error(f"RTSP initialization error:\n\n{error}")
        finally:
            if cap is not None:
                try:
                    cap.release()
                except Exception:
                    pass

    def _emit_error(self, message):
        if not self._error_emitted:
            self._error_emitted = True
            self.connection_failed_signal.emit(message)

    def stop(self):
        self._run_flag = False
        if self.isRunning():
            self.wait(3000)


# ============================================================
# FIXED-SCALE WEB ENGINE VIEW
# ============================================================
class FixedZoomWebEngineView(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setZoomFactor(1.0)
        page = self.page()
        if page is not None:
            page.setZoomFactor(1.0)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            event.accept()
            self.setZoomFactor(1.0)
            return
        super().wheelEvent(event)

    def keyPressEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.key() in (Qt.Key.Key_Plus, Qt.Key.Key_Equal, Qt.Key.Key_Minus, Qt.Key.Key_0):
                event.accept()
                self.setZoomFactor(1.0)
                return
        super().keyPressEvent(event)


# ============================================================
# FLOATING SETTINGS DIALOG
# ============================================================
class CameraSettingsDialog(QDialog):
    def __init__(self, app_state, parent=None):
        super().__init__(parent)
        self.app_state = app_state
        self.setWindowTitle("Camera RTSP Settings")
        self.setFixedSize(360, 320)
        
        # Dialog Specific Styling Framework
        self.setStyleSheet("""
            QDialog {
                background-color: #1c1c22;
                border: 1px solid #282830;
            }
            QLabel {
                color: #a0a0b0;
                font-weight: 500;
            }
            QLineEdit, QComboBox {
                background-color: #141418;
                border: 1px solid #2e2e3a;
                border-radius: 6px;
                padding: 8px 10px;
                color: #ffffff;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #2ec4b6;
                background-color: #16161c;
            }
            QPushButton {
                background-color: #2ec4b6;
                color: #121215;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 10px 15px;
            }
            QPushButton:hover {
                background-color: #3ee4d6;
            }
            QPushButton#btnCancel {
                background-color: #2e2e3a;
                color: #ffffff;
            }
            QPushButton#btnCancel:hover {
                background-color: #3a3a4a;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        self.input_ip = QLineEdit(self.app_state.get('ip', '192.168.4.72'))
        self.input_port = QLineEdit(self.app_state.get('port', '554'))
        self.input_user = QLineEdit(self.app_state.get('user', 'admin'))
        self.input_pass = QLineEdit(self.app_state.get('password', ''))
        self.input_pass.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.combo_stream_profile = QComboBox()
        self.combo_stream_profile.addItem("Main Stream (1080p/4K High Res)", "101")
        self.combo_stream_profile.addItem("Sub Stream (Lower Res Fluent)", "102")
        self.combo_stream_profile.addItem("Third Stream (Mobile Optimized)", "103")
        
        # Restore stream combo index
        saved_chan = self.app_state.get('channel', '101')
        idx = self.combo_stream_profile.findData(saved_chan)
        if idx != -1:
            self.combo_stream_profile.setCurrentIndex(idx)
            
        form_layout.addRow("Camera IP", self.input_ip)
        form_layout.addRow("RTSP Port", self.input_port)
        form_layout.addRow("Username", self.input_user)
        form_layout.addRow("Password", self.input_pass)
        form_layout.addRow("Stream Profile", self.combo_stream_profile)
        layout.addLayout(form_layout)
        
        # Action Buttons Layout Row
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setObjectName("btnCancel")
        btn_cancel.clicked.connect(self.reject)
        
        btn_save = QPushButton("Apply & Save")
        btn_save.clicked.connect(self.save_and_close)
        
        buttons_layout.addWidget(btn_cancel)
        buttons_layout.addWidget(btn_save)
        layout.addLayout(buttons_layout)
        
    def save_and_close(self):
        self.app_state['ip'] = self.input_ip.text()
        self.app_state['port'] = self.input_port.text()
        self.app_state['user'] = self.input_user.text()
        self.app_state['password'] = self.input_pass.text()
        self.app_state['channel'] = self.combo_stream_profile.currentData()
        self.accept()


# ============================================================
# MAIN APPLICATION
# ============================================================
class CCTVApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OEM CCTV Management Center")
        self.resize(1280, 800)
        
        self.camera_thread = None
        self.raw_latest_frame = None  
        
        # Global Persistent Credentials/Settings State Cache
        self.camera_config = {
            'ip': '192.168.4.72',
            'port': '554',
            'user': 'admin',
            'password': '',
            'channel': '101'
        }
        
        # Complete UI Theme Stylesheet Matrix
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121215;
            }
            QWidget {
                color: #e2e2e7;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
            }
            QLineEdit {
                background-color: #141418;
                border: 1px solid #2e2e3a;
                border-radius: 6px;
                padding: 8px 10px;
                color: #ffffff;
            }
            QLineEdit:focus {
                border: 1px solid #2ec4b6;
            }
            QPushButton {
                background-color: #2ec4b6;
                color: #121215;
                font-weight: bold;
                font-size: 13px;
                border: none;
                border-radius: 6px;
                padding: 10px 15px;
            }
            QPushButton:hover {
                background-color: #3ee4d6;
            }
            QPushButton:pressed {
                background-color: #1fa396;
            }
            
            /* Modern Utility Icons Header Panel Controls */
            QPushButton#btnSettingsGear {
                background-color: #1c1c22;
                border: 1px solid #282830;
                color: #a0a0b0;
                font-size: 16px;
                padding: 8px;
                border-radius: 6px;
            }
            QPushButton#btnSettingsGear:hover {
                background-color: #25252e;
                color: #2ec4b6;
                border: 1px solid #2ec4b6;
            }
            
            QPushButton#btnStreamToggle {
                background-color: #2ec4b6;
                color: #121215;
            }
            QPushButton#btnStreamToggle[running="true"] {
                background-color: #e63946;
                color: #ffffff;
            }
            QPushButton#btnStreamToggle[running="true"]:hover {
                background-color: #ff4d5a;
            }
        """)

        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ----------------------------------------------------
        # SIDEBAR MENU NAVIGATION
        # ----------------------------------------------------
        self.menu_list = QListWidget()
        self.menu_list.setFixedWidth(240)
        self.menu_list.setStyleSheet("""
            QListWidget {
                background-color: #18181c;
                border-right: 1px solid #222228;
                padding-top: 15px;
            }
            QListWidget::item {
                padding: 14px 20px;
                color: #8e8e9a;
                font-weight: 600;
                border-left: 4px solid transparent;
                margin-bottom: 2px;
            }
            QListWidget::item:selected {
                background-color: #1c1c22;
                color: #2ec4b6;
                border-left: 4px solid #2ec4b6;
            }
            QListWidget::item:hover:!selected {
                background-color: #1f1f25;
                color: #ffffff;
            }
        """)
        self.menu_list.addItems(["📺 Live Video Stream", "⚙️ Web Configuration"])
        main_layout.addWidget(self.menu_list)

        # ----------------------------------------------------
        # STACKED PAGES INTERFACE
        # ----------------------------------------------------
        self.pages_container = QStackedWidget()
        main_layout.addWidget(self.pages_container)

        self.create_live_view_page()
        self.create_web_config_page()

        self.menu_list.currentRowChanged.connect(self.pages_container.setCurrentIndex)
        self.menu_list.setCurrentRow(0)

    def create_live_view_page(self):
        page_widget = QWidget()
        layout = QVBoxLayout(page_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Top Control Navbar Utility Row Header
        top_bar_layout = QHBoxLayout()
        
        self.btn_toggle_stream = QPushButton("▶  Connect Stream")
        self.btn_toggle_stream.setObjectName("btnStreamToggle")
        self.btn_toggle_stream.setProperty("running", "false")
        self.btn_toggle_stream.clicked.connect(self.handle_stream_toggle_action)
        
        btn_open_settings = QPushButton("⚙")
        btn_open_settings.setObjectName("btnSettingsGear")
        btn_open_settings.setToolTip("Configure Connection Parameters")
        btn_open_settings.clicked.connect(self.open_settings_modal_dialog)
        
        top_bar_layout.addWidget(self.btn_toggle_stream)
        top_bar_layout.addStretch()
        top_bar_layout.addWidget(btn_open_settings)
        layout.addLayout(top_bar_layout)

        # Main Large Viewport Box Canvas Panel Container Area
        self.video_display_screen = QLabel("No active video feed connected.")
        self.video_display_screen.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_display_screen.setStyleSheet("""
            QLabel {
                background-color: #0b0b0d;
                border: 1px solid #1c1c22;
                border-radius: 12px;
                color: #525262;
                font-weight: bold;
                font-size: 14px;
            }
        """)

        layout.addWidget(self.video_display_screen, stretch=1)
        self.pages_container.addWidget(page_widget)

    def create_web_config_page(self):
        page_widget = QWidget()
        layout = QVBoxLayout(page_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        nav_bar = QHBoxLayout()
        self.web_address_bar = QLineEdit("http://192.168.1.64")
        btn_load_web = QPushButton("🌐 Access Web Config")
        btn_load_web.clicked.connect(self.load_camera_web_portal)
        
        nav_bar.addWidget(self.web_address_bar, stretch=1)
        nav_bar.addWidget(btn_load_web)
        layout.addLayout(nav_bar)

        self.browser_viewport = FixedZoomWebEngineView()
        self.browser_viewport.setStyleSheet(
            "border: 1px solid #1c1c22; border-radius: 12px; background-color: #0b0b0d;"
        )

        page = self.browser_viewport.page()
        settings = page.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.ErrorPageEnabled, True)

        profile = page.profile()
        profile.setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        self.browser_viewport.loadFinished.connect(self._reset_web_zoom)
        layout.addWidget(self.browser_viewport, stretch=1)
        self.pages_container.addWidget(page_widget)

    # ========================================================
    # CONTROLLER CONTROLS ACTION IMPLEMENTATION LOGIC
    # ========================================================
    def open_settings_modal_dialog(self):
        dialog = CameraSettingsDialog(self.camera_config, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.web_address_bar.setText(f"http://{self.camera_config['ip']}")
            if self.camera_thread and self.camera_thread.isRunning():
                self.stop_video_stream()
                self.start_video_stream()

    def handle_stream_toggle_action(self):
        if self.camera_thread and self.camera_thread.isRunning():
            self.stop_video_stream()
        else:
            self.start_video_stream()

    def start_video_stream(self):
        cfg = self.camera_config
        if not cfg['ip'] or not cfg['user'] or not cfg['password']:
            QMessageBox.warning(self, "Configuration Incomplete", 
                                "Please open the Settings panel (⚙) and set IP, Username, and Password fields first.")
            return

        self.btn_toggle_stream.setText("⏹  Stop Stream")
        self.btn_toggle_stream.setProperty("running", "true")
        self.btn_toggle_stream.style().unpolish(self.btn_toggle_stream)
        self.btn_toggle_stream.style().polish(self.btn_toggle_stream)
        
        self.video_display_screen.setText("Negotiating handshake with RTSP Endpoint...")

        self.camera_thread = CameraThread(cfg['ip'], cfg['port'], cfg['user'], cfg['password'], cfg['channel'])
        self.camera_thread.change_pixmap_signal.connect(self.update_video_frame)
        self.camera_thread.connection_failed_signal.connect(self.handle_stream_exception)
        self.camera_thread.start()

    def update_video_frame(self, qt_image):
        self.raw_latest_frame = qt_image  
        self.repaint_scaled_video()

    def repaint_scaled_video(self):
        if self.raw_latest_frame is None:
            return

        target_size = self.video_display_screen.contentsRect().size()
        if target_size.width() <= 0 or target_size.height() <= 0:
            return

        source_pixmap = QPixmap.fromImage(self.raw_latest_frame)
        scaled_pixmap = source_pixmap.scaled(
            target_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.video_display_screen.setPixmap(scaled_pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.repaint_scaled_video()

    def handle_stream_exception(self, message):
        self.stop_video_stream()
        QMessageBox.critical(self, "Streaming Error Encountered", message)

    def stop_video_stream(self):
        if self.camera_thread:
            self.camera_thread.stop()
            self.camera_thread = None
        
        self.raw_latest_frame = None
        self.video_display_screen.clear()
        self.video_display_screen.setText("No active video feed connected.")
        
        self.btn_toggle_stream.setText("▶  Connect Stream")
        self.btn_toggle_stream.setProperty("running", "false")
        self.btn_toggle_stream.style().unpolish(self.btn_toggle_stream)
        self.btn_toggle_stream.style().polish(self.btn_toggle_stream)

    def _reset_web_zoom(self, ok):
        self.browser_viewport.setZoomFactor(1.0)
        page = self.browser_viewport.page()
        if page is not None:
            page.setZoomFactor(1.0)

    def load_camera_web_portal(self):
        target_url = self.web_address_bar.text().strip()
        if not target_url:
            QMessageBox.warning(self, "Web Access", "Please enter the IP camera address.")
            return

        if not target_url.startswith(("http://", "https://")):
            target_url = "http://" + target_url

        self.web_address_bar.setText(target_url)
        self.browser_viewport.stop()
        self.browser_viewport.setZoomFactor(1.0)

        request = QWebEngineHttpRequest(QUrl(target_url))
        request.setHeader(
            b"User-Agent",
            b"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        self.browser_viewport.load(request)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CCTVApp()
    window.show()
    sys.exit(app.exec())
