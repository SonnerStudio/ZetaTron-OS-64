import sys
import os
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QProgressBar, QVBoxLayout, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QTimer, Property, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPixmap, QFont, QColor
import pygame  # pygame-ce

# CyberTron Boot Screen
# Displays the verified boot splash with progress and status updates.

class BootScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ZetaTron-OS Boot")
        # Fullscreen and Frameless
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.resize(1920, 1080) # Default, will maximize
        
        # 1. Background Image
        self.bg_label = QLabel(self)
        self.bg_label.setGeometry(0, 0, 1920, 1080)
        self.bg_label.setScaledContents(True)
        
        asset_path = os.path.join(os.path.dirname(__file__), "web", "bootscreen.jpg")
        if os.path.exists(asset_path):
            self.bg_label.setPixmap(QPixmap(asset_path))
        else:
            self.bg_label.setStyleSheet("background-color: #050510;")
            print(f"Warning: Bootscreen image not found at {asset_path}")

        # 2. UI Container (Bottom Center)
        self.ui_container = QWidget(self)
        self.ui_container.setGeometry(460, 900, 1000, 200) # Centered bottom roughly
        
        layout = QVBoxLayout(self.ui_container)
        
        # 3. Status Text
        self.status_label = QLabel("INITIALISIERE SYSTEM...", self.ui_container)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            color: #ffd700;
            font-family: 'Segoe UI', sans-serif;
            font-size: 18px;
            font-weight: bold;
            letter-spacing: 2px;
        """)
        # Add glow effect
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(15)
        glow.setColor(QColor("#ffd700"))
        glow.setOffset(0,0)
        self.status_label.setGraphicsEffect(glow)
        


        # 4. Progress Bar
        self.progress = QProgressBar(self.ui_container)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(6)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: rgba(20, 20, 20, 0.5);
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #ff0000, /* Infrared/Red */
                    stop:0.1 #ff4500, /* Red-Orange */
                    stop:0.2 #ff8c00, /* Dark Orange */
                    stop:0.3 #ffd700, /* Gold/Yellow */
                    stop:0.4 #adff2f, /* Green-Yellow */
                    stop:0.5 #00ff00, /* Pure Green */
                    stop:0.6 #00fa9a, /* Medium Spring Green */
                    stop:0.7 #00ffff, /* Cyan */
                    stop:0.8 #1e90ff, /* Dodger Blue */
                    stop:0.9 #0000ff, /* Blue */
                    stop:1.0 #8a2be2); /* Blue-Violet/UV */
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress)
        layout.addWidget(self.status_label)
        
        # Show the boot screen
        self.show()
        QApplication.instance().processEvents()  # Ensure the window is rendered before sound plays
        
        # Play bootup sound
        try:
            pygame.mixer.init()
            sound_path = os.path.join(os.path.dirname(__file__), 'web', 'assets', 'systemsounds', 'bootup.mp3')
            if os.path.exists(sound_path):
                pygame.mixer.music.load(sound_path)
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play()
                print("[BOOT] 🔊 Bootup sound playing")
                
                # Play only 60% of sound duration, fade out at end
                sound = pygame.mixer.Sound(sound_path)
                full_duration_ms = int(sound.get_length() * 1000)
                play_duration_ms = int(full_duration_ms * 0.6)  # 60% of total
                fadeout_start = max(0, play_duration_ms - 2000)  # Start fade 2s before 60% mark
                
                # Exponential volume decrease (30 steps over 2 seconds)
                steps = 30
                step_duration = 2000 // steps  # ~67ms per step
                
                def exponential_fade(step):
                    if step >= steps:
                        pygame.mixer.music.set_volume(0)
                        pygame.mixer.music.stop()
                        return
                    # Exponential decay to reach near-zero
                    import math
                    volume = 0.5 * math.exp(-0.206 * step)
                    pygame.mixer.music.set_volume(volume)
                    QTimer.singleShot(step_duration, lambda: exponential_fade(step + 1))
                
                # Schedule exponential fadeout at 60% mark
                QTimer.singleShot(fadeout_start, lambda: exponential_fade(0))
            else:
                print(f"[BOOT] ⚠️ Sound file not found: {sound_path}")
        except Exception as e:
            print(f"[BOOT] ❌ Sound error: {e}")
        
        # Animation Logic
        self.counter = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(30)  # Fast updates (was 800ms - too slow!)

        # Simulated Boot Sequence (Localized & Real-sounding)
        self.steps = [
            (10, "LADE KERNEL MODULE (SSL v7.0)..."),
            (30, "INITIALISIERE DATEISYSTEM..."),
            (50, "VERBINDE MIT NEURAL INTERFACE..."),
            (60, "STARTE OLLAMA AI ENGINE..."),
            (80, "LADE SICHERHEITSPROTOKOLLE..."),
            (90, "INITIALISIERE GUI SUB-SYSTEM..."),
            (100, "SYSTEM BEREIT")
        ]

    def resizeEvent(self, event):
        # Keep background full size
        self.bg_label.resize(self.width(), self.height())
        # Re-center UI
        rect = self.ui_container.geometry()
        new_x = (self.width() - rect.width()) // 2
        new_y = self.height() - 180
        self.ui_container.move(new_x, new_y)
        super().resizeEvent(event)

    def update_progress(self):
        self.counter += 1
        self.progress.setValue(self.counter)
        
        # Check steps
        for threshold, text in self.steps:
            if self.counter == threshold:
                self.status_label.setText(text)
        
        if self.counter >= 100:
            self.timer.stop()
            # Do NOT close here. Launcher handles transition.

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BootScreen()
    window.showFullScreen()
    sys.exit(app.exec())
