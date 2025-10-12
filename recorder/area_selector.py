"""
Area selection widget for choosing custom recording areas
"""
from PySide6.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, Signal, QRect, QPoint
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QPixmap, QScreen
import mss
import sys


class AreaSelector(QWidget):
    """Overlay widget for selecting screen recording area"""
    
    area_selected = Signal(dict)  # Emits the selected area coordinates
    
    def __init__(self):
        super().__init__()
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.selecting = False
        self.selection_rect = QRect()
        
        # Get virtual desktop geometry (all screens combined)
        self.virtual_geometry = self.get_virtual_desktop_geometry()
        
        # Make window cover all screens
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Set geometry to cover all screens
        self.setGeometry(self.virtual_geometry)
        
        # Set up the UI
        self.setup_ui()
        
        # Get screenshot as background
        self.screenshot = self.capture_screenshot()
    
    def get_virtual_desktop_geometry(self):
        """Get the combined geometry of all screens"""
        app = QApplication.instance()
        if not app:
            return QRect(0, 0, 1920, 1080)  # Fallback
        
        # Get all screens using QGuiApplication
        from PySide6.QtGui import QGuiApplication
        screens = QGuiApplication.screens()
        if not screens:
            return QRect(0, 0, 1920, 1080)  # Fallback
        
        # Start with the first screen's geometry
        combined_geometry = screens[0].geometry()
        
        # Extend to include all other screens
        for screen in screens[1:]:
            combined_geometry = combined_geometry.united(screen.geometry())
        
        print(f"Virtual desktop geometry: {combined_geometry}")
        return combined_geometry
        
    def setup_ui(self):
        """Set up the user interface"""
        # Instructions label
        self.instructions = QLabel()
        self.instructions.setText(
            "Click and drag to select recording area\n"
            "Press ESC to cancel, ENTER to confirm selection"
        )
        self.instructions.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 180);
                color: white;
                padding: 15px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        self.instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.confirm_btn = QPushButton("Confirm Selection")
        self.confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.confirm_btn.clicked.connect(self.confirm_selection)
        self.confirm_btn.setEnabled(False)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.cancel_btn.clicked.connect(self.cancel_selection)
        
        button_layout.addWidget(self.confirm_btn)
        button_layout.addWidget(self.cancel_btn)
        
        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(self.instructions, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch()
        layout.addLayout(button_layout)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.setLayout(layout)
    
    def capture_screenshot(self):
        """Capture screenshot of all screens"""
        try:
            # Use Qt's built-in screen capture instead of mss for the overlay
            screen = QApplication.primaryScreen()
            if screen:
                pixmap = screen.grabWindow(0)  # Capture entire desktop
                return pixmap
        except Exception as e:
            print(f"Error capturing screenshot: {e}")
        return QPixmap()
    
    def paintEvent(self, event):
        """Paint the overlay"""
        painter = QPainter(self)
        
        # Draw screenshot background with overlay
        if not self.screenshot.isNull():
            # Darken the entire screen
            painter.fillRect(self.rect(), QColor(0, 0, 0, 100))
            
            # If we have a selection, show the selected area clearly
            if not self.selection_rect.isEmpty():
                # Draw the selected area without darkening
                painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
                painter.drawPixmap(self.selection_rect, self.screenshot, self.selection_rect)
                
                # Draw selection rectangle border
                pen = QPen(QColor(255, 0, 0), 3, Qt.PenStyle.SolidLine)
                painter.setPen(pen)
                painter.drawRect(self.selection_rect)
                
                # Draw corner handles
                self.draw_corner_handles(painter)
                
                # Show dimensions
                self.draw_dimensions(painter)
    
    def draw_corner_handles(self, painter):
        """Draw corner handles for the selection rectangle"""
        if self.selection_rect.isEmpty():
            return
            
        handle_size = 8
        brush = QBrush(QColor(255, 0, 0))
        painter.setBrush(brush)
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        
        rect = self.selection_rect
        
        # Top-left
        painter.drawEllipse(rect.topLeft().x() - handle_size//2, 
                          rect.topLeft().y() - handle_size//2, 
                          handle_size, handle_size)
        
        # Top-right
        painter.drawEllipse(rect.topRight().x() - handle_size//2, 
                          rect.topRight().y() - handle_size//2, 
                          handle_size, handle_size)
        
        # Bottom-left
        painter.drawEllipse(rect.bottomLeft().x() - handle_size//2, 
                          rect.bottomLeft().y() - handle_size//2, 
                          handle_size, handle_size)
        
        # Bottom-right
        painter.drawEllipse(rect.bottomRight().x() - handle_size//2, 
                          rect.bottomRight().y() - handle_size//2, 
                          handle_size, handle_size)
    
    def draw_dimensions(self, painter):
        """Draw dimensions text"""
        if self.selection_rect.isEmpty():
            return
            
        width = self.selection_rect.width()
        height = self.selection_rect.height()
        
        # Draw dimensions text
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setBrush(QBrush(QColor(0, 0, 0, 180)))
        
        text = f"{width} × {height}"
        font_metrics = painter.fontMetrics()
        text_width = font_metrics.horizontalAdvance(text)
        text_height = font_metrics.height()
        
        # Position text above the selection rectangle
        text_x = self.selection_rect.center().x() - text_width // 2
        text_y = self.selection_rect.top() - 10
        
        # Draw background for text
        text_rect = QRect(text_x - 5, text_y - text_height, text_width + 10, text_height + 5)
        painter.drawRect(text_rect)
        
        # Draw text
        painter.setPen(QPen(QColor(255, 255, 255)))
        painter.drawText(text_x, text_y, text)
    
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_point = event.position().toPoint()
            self.selecting = True
            self.confirm_btn.setEnabled(False)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events"""
        if self.selecting:
            self.end_point = event.position().toPoint()
            
            # Update selection rectangle
            self.selection_rect = QRect(self.start_point, self.end_point).normalized()
            
            # Enable confirm button if we have a reasonable selection
            if self.selection_rect.width() > 10 and self.selection_rect.height() > 10:
                self.confirm_btn.setEnabled(True)
            
            self.update()  # Trigger repaint
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events"""
        if event.button() == Qt.MouseButton.LeftButton and self.selecting:
            self.selecting = False
            self.end_point = event.position().toPoint()
            self.selection_rect = QRect(self.start_point, self.end_point).normalized()
            
            # Enable confirm button if we have a valid selection
            if self.selection_rect.width() > 10 and self.selection_rect.height() > 10:
                self.confirm_btn.setEnabled(True)
            
            self.update()
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Escape:
            self.cancel_selection()
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if self.confirm_btn.isEnabled():
                self.confirm_selection()
    
    def confirm_selection(self):
        """Confirm the selected area"""
        if not self.selection_rect.isEmpty():
            area = {
                'left': self.selection_rect.left(),
                'top': self.selection_rect.top(),
                'width': self.selection_rect.width(),
                'height': self.selection_rect.height()
            }
            self.area_selected.emit(area)
        self.close()
    
    def cancel_selection(self):
        """Cancel area selection"""
        self.close()


def show_area_selector():
    """Show the area selector and return the selected area - DEPRECATED"""
    # This function is no longer used - AreaSelector should be created directly
    # in the main application to avoid event loop conflicts
    raise NotImplementedError("Use AreaSelector() directly instead of this function")


if __name__ == "__main__":
    # Test the area selector
    app = QApplication(sys.argv)
    
    selector = AreaSelector()
    
    def on_area_selected(area):
        print(f"Selected area: {area}")
        app.quit()
    
    def on_selector_closed():
        print("Selection cancelled")
        app.quit()
    
    selector.area_selected.connect(on_area_selected)
    selector.destroyed.connect(on_selector_closed)
    
    selector.show()
    app.exec()