#!/usr/bin/env python3
"""
Test the area selector functionality
"""
import sys
import os
# Dynamically add the project root to sys.path for portability
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtWidgets import QApplication
from recorder.area_selector import AreaSelector

def test_area_selector():
    app = QApplication(sys.argv)
    
    print("🖱️  Testing area selector...")
    print("Instructions:")
    print("1. Click and drag to select an area")
    print("2. Press ENTER to confirm or ESC to cancel")
    print("3. Or use the buttons")
    
    selector = AreaSelector()
    
    def on_area_selected(area):
        print(f"✅ Area selected: {area}")
        app.quit()
    
    def on_selector_closed():
        print("❌ Area selection cancelled")
        app.quit()
    
    selector.area_selected.connect(on_area_selected)
    selector.destroyed.connect(on_selector_closed)
    
    selector.show()
    selector.raise_()
    selector.activateWindow()
    
    return app.exec()

if __name__ == "__main__":
    test_area_selector()