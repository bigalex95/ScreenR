
from PySide6.QtWidgets import QApplication, QMainWindow, QButtonGroup, QMessageBox, QFileDialog
import sys
from PySide6.QtCore import QTextStream, QFile, QIODevice, QTimer, QThread, Signal
from PySide6.QtGui import QIcon
from ui.ui_screen_recorder import Ui_MainWindow
import resources.resources_rc
from recorder import RecorderManager
from pathlib import Path


class ScreenRecorder(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Initialize the recorder manager
        self.recorder = RecorderManager()
        self.setup_recorder_callbacks()

        # Create button groups (this is where the magic happens!)
        self.setup_button_groups()

        # Initialize recording state
        self.is_recording = False
        self.is_paused = False

        # Connect main buttons
        self.ui.recordButton.clicked.connect(self.toggle_recording)
        self.ui.pauseButton.clicked.connect(self.toggle_pause)

        # Set initial selections
        self.set_initial_selections()

        # Update button states
        self.update_button_states()

        # Set up status updates
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_recording_status)
        
        # Initialize preview label
        self.ui.previewLabel.setText("Ready to record\nClick 'Start Recording' to begin")

        # 👇 Load style from external .qss file bundled via resources
        self.load_style_from_resource()

    def setup_recorder_callbacks(self):
        """Set up callbacks for recorder status updates"""
        self.recorder.set_status_callback(self.on_recorder_status)
        self.recorder.set_progress_callback(self.on_recorder_progress)

    def on_recorder_status(self, status: str):
        """Handle recorder status updates"""
        print(f"Recorder status: {status}")
        # Update preview label with status
        self.ui.previewLabel.setText(status)

    def on_recorder_progress(self, stats: dict):
        """Handle recorder progress updates"""
        duration = stats.get('recording_duration', 0)
        frames = stats.get('frames_captured', 0)
        dropped = stats.get('frames_dropped', 0)
        
        status_text = f"Recording: {duration:.1f}s\nFrames: {frames} (dropped: {dropped})"
        self.ui.previewLabel.setText(status_text)

    def load_style_from_resource(self):
        """Load QSS from Qt resource system (e.g., :/styles/dark_theme.qss)"""
        file = QFile(":/styles/dark_theme.qss")
        if not file.exists():
            print("❌ Style file not found in resources!")
            return

        if not file.open(QIODevice.OpenModeFlag.ReadOnly | QIODevice.OpenModeFlag.Text):
            print("❌ Could not open style file!")
            return

        stream = QTextStream(file)
        style = stream.readAll()
        file.close()

        self.setStyleSheet(style)
        print("✅ Style loaded successfully from resource")

    def setup_button_groups(self):
        """Create logical button groups for exclusive selection"""

        # Audio Input Group
        self.audio_group = QButtonGroup(self)
        self.audio_group.addButton(self.ui.systemAudioButton)
        self.audio_group.addButton(self.ui.microphoneButton)
        self.audio_group.addButton(self.ui.noneAudioButton)

        # Recording Area Group
        self.area_group = QButtonGroup(self)
        self.area_group.addButton(self.ui.fullScreenButton)
        self.area_group.addButton(self.ui.selectAreaButton)

        # Recording Quality Group (if you have these buttons)
        self.quality_group = QButtonGroup(self)
        self.quality_group.addButton(self.ui.lowQualityButton)
        self.quality_group.addButton(self.ui.mediumQualityButton)
        self.quality_group.addButton(self.ui.highQualityButton)

        # Countdown Timer Group (if you have these buttons)
        self.timer_group = QButtonGroup(self)
        self.timer_group.addButton(self.ui.threeSecondsButton)
        self.timer_group.addButton(self.ui.fiveSecondsButton)
        self.timer_group.addButton(self.ui.tenSecondsButton)
        self.timer_group.addButton(self.ui.noneTimerButton)

        # Make all buttons checkable (so they can be "selected")
        self.make_buttons_checkable()

        # Set exclusive selection for each group
        self.audio_group.setExclusive(True)
        self.area_group.setExclusive(True)
        self.quality_group.setExclusive(True)
        self.timer_group.setExclusive(True)

        # Connect signals to handle selections
        self.audio_group.buttonClicked.connect(self.handle_audio_selection)
        self.area_group.buttonClicked.connect(self.handle_area_selection)
        self.quality_group.buttonClicked.connect(self.handle_quality_selection)
        self.timer_group.buttonClicked.connect(self.handle_timer_selection)

    def make_buttons_checkable(self):
        """Make all toggle buttons checkable"""
        buttons = [
            self.ui.systemAudioButton, self.ui.microphoneButton, self.ui.noneAudioButton,
            self.ui.fullScreenButton, self.ui.selectAreaButton,
            self.ui.lowQualityButton, self.ui.mediumQualityButton, self.ui.highQualityButton,
            self.ui.threeSecondsButton, self.ui.fiveSecondsButton,
            self.ui.tenSecondsButton, self.ui.noneTimerButton
        ]

        for button in buttons:
            button.setCheckable(True)

    def set_initial_selections(self):
        """Set default selected buttons"""
        self.ui.microphoneButton.setChecked(True)
        self.ui.selectAreaButton.setChecked(True)
        self.ui.highQualityButton.setChecked(True)
        self.ui.fiveSecondsButton.setChecked(True)

    def handle_audio_selection(self, button):
        """Called when any audio button is clicked"""
        print(f"Audio selected: {button.text()}")
        # Store the selection for later use
        self.selected_audio = button.text()

    def handle_area_selection(self, button):
        """Called when any area button is clicked"""
        print(f"Area selected: {button.text()}")
        self.selected_area = button.text()

    def handle_quality_selection(self, button):
        """Called when any quality button is clicked"""
        print(f"Quality selected: {button.text()}")
        self.selected_quality = button.text()

    def handle_timer_selection(self, button):
        """Called when any timer button is clicked"""
        print(f"Timer selected: {button.text()}")
        self.selected_timer = button.text()

    def get_preview_style(self, is_recording=False, is_paused=False):
        # Get current palette for more accurate theme detection
        palette = self.palette()
        bg_color = palette.color(self.backgroundRole()).name().lower()

        # Try to detect dark theme based on multiple criteria
        is_dark_theme = False
        if bg_color in ["#1e1e2e", "#24243a", "#2b2b3d", "#121212", "#2d2d2d"]:
            is_dark_theme = True
        else:
            # Check if it's a very light color
            try:
                r, g, b = int(bg_color[1:3], 16), int(bg_color[3:5], 16), int(bg_color[5:7], 16)
                brightness = (r + g + b) / 3
                is_dark_theme = brightness < 100  # Adjust threshold as needed
            except (ValueError, IndexError):
                # Fallback to checking if it starts with dark colors
                is_dark_theme = bg_color.startswith('#1') or bg_color.startswith('#2')

        if is_dark_theme:
            base_bg = "#1e1e2e"
            idle_border = "#45475a"
            active_border = "#89b4fa"
            text_color = "#89b4fa"
        else:  # Light theme
            base_bg = "white"
            idle_border = "#dee2e6"
            active_border = "#3d8bfd"
            text_color = "#3d8bfd"

        if is_paused:
            border_style = f"2px dashed #f3c969"
        elif is_recording:
            border_style = f"2px solid {active_border}"
        else:
            border_style = f"2px solid {idle_border}"

        return f"""
            QLabel#previewLabel {{
                color: {text_color};
                font-size: 16px;
                font-weight: bold;
                qproperty-alignment: AlignCenter;
                background-color: {base_bg};
                border: {border_style};
                border-radius: 8px;
                padding: 16px;
                min-height: 200px;
                min-width: 320px;
            }}
        """

    def update_button_states(self):
        if not self.is_recording:
            self.ui.recordButton.setText("Start Recording")
            self.ui.recordButton.setIcon(QIcon(":/icons/start.svg"))
            self.ui.pauseButton.setEnabled(False)
            self.ui.previewLabel.setStyleSheet(
                self.get_preview_style(is_recording=False, is_paused=False)
            )
        elif self.is_recording and not self.is_paused:
            self.ui.recordButton.setText("Stop Recording")
            self.ui.recordButton.setIcon(QIcon(":/icons/stop.svg"))
            self.ui.pauseButton.setEnabled(True)
            self.ui.pauseButton.setText("Pause")
            self.ui.pauseButton.setIcon(QIcon(":/icons/pause.svg"))
            self.ui.previewLabel.setStyleSheet(
                self.get_preview_style(is_recording=True, is_paused=False)
            )
        else:  # paused
            self.ui.recordButton.setText("Stop Recording")
            self.ui.recordButton.setIcon(QIcon(":/icons/stop.svg"))
            self.ui.pauseButton.setEnabled(True)
            self.ui.pauseButton.setText("Resume")
            self.ui.pauseButton.setIcon(QIcon(":/icons/resume.svg"))
            self.ui.previewLabel.setStyleSheet(
                self.get_preview_style(is_recording=True, is_paused=True)
            )

        # Force update of the preview label
        self.ui.previewLabel.update()

    def update_recording_status(self):
        """Update recording status display"""
        if self.recorder.is_recording():
            stats = self.recorder.get_recording_stats()
            duration = stats.get('recording_duration', 0)
            frames = stats.get('frames_captured', 0)
            dropped = stats.get('frames_dropped', 0)
            
            status_text = f"Recording: {duration:.1f}s\nFrames: {frames}"
            if dropped > 0:
                status_text += f" (dropped: {dropped})"
            
            self.ui.previewLabel.setText(status_text)

    def apply_recording_settings(self):
        """Apply current UI settings to the recorder"""
        # Audio settings
        audio_enabled = not hasattr(self, 'selected_audio') or self.selected_audio != "None"
        
        # Recording area
        area_type = 'fullscreen' if hasattr(self, 'selected_area') and self.selected_area == "Full Screen" else 'custom'
        
        # Quality settings
        quality_map = {
            "Low": "low",
            "Medium": "medium", 
            "High": "high"
        }
        quality = quality_map.get(getattr(self, 'selected_quality', 'High'), 'high')
        
        # Apply settings
        self.recorder.set_settings(
            audio_enabled=audio_enabled,
            area_type=area_type,
            quality=quality,
            output_directory=str(Path.home() / 'Videos' / 'ScreenR')
        )

    def toggle_recording(self):
        if not self.is_recording:
            # Start recording
            self.apply_recording_settings()
            
            if self.recorder.start_recording():
                self.is_recording = True
                self.is_paused = False
                self.status_timer.start(1000)  # Update every second
                print("Recording started...")
            else:
                QMessageBox.warning(self, "Recording Error", "Failed to start recording. Check permissions and try again.")
        else:
            # Stop recording
            self.recorder.stop_recording()
            self.is_recording = False
            self.is_paused = False
            self.status_timer.stop()
            self.ui.previewLabel.setText("Recording saved!\nReady for next recording")
            print("Recording stopped...")
        
        self.update_button_states()

    def toggle_pause(self):
        if self.is_recording:
            if not self.is_paused:
                self.recorder.pause_recording()
                self.is_paused = True
                print("Recording paused...")
            else:
                self.recorder.resume_recording()
                self.is_paused = False
                print("Recording resumed...")
            
            self.update_button_states()

    def closeEvent(self, event):
        """Handle application close event"""
        if self.is_recording:
            reply = QMessageBox.question(
                self, 
                'Recording in Progress',
                'Recording is in progress. Do you want to stop recording and exit?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.recorder.stop_recording()
                self.recorder.cleanup()
                event.accept()
            else:
                event.ignore()
        else:
            self.recorder.cleanup()
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScreenRecorder()
    window.show()
    sys.exit(app.exec())