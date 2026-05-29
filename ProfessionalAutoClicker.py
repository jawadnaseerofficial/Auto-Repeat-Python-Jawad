import time
import threading
import json
import customtkinter as ctk
from pynput import mouse, keyboard
from pynput.keyboard import Controller as KController, Key
from pynput.mouse import Button, Controller as MController

class ProfessionalAutoClicker:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Auto Repeat by Jawad Naseer")
        self.root.geometry("400x350")
        
        # State Variables
        self.is_recording = False
        self.is_playing = False
        self.recorded_data = []
        self.start_time = 0
        self.speed_modifier = 1.0
        
        self.mouse_ctrl = MController()
        self.kb_ctrl = KController()
        
        self.setup_ui()
        self.setup_listeners()

    def setup_ui(self):
        ctk.set_appearance_mode("dark")
        
        self.status_label = ctk.CTkLabel(self.root, text="Status: Ready", font=("Arial", 16, "bold"))
        self.status_label.pack(pady=20)

        # Speed Slider
        ctk.CTkLabel(self.root, text="Playback Speed (0.5x - 5x)").pack()
        self.speed_slider = ctk.CTkSlider(self.root, from_=0.5, to=5.0, command=self.update_speed)
        self.speed_slider.set(1.0)
        self.speed_slider.pack(pady=10)

        # Instructions
        info_text = (
            "Hotkeys:\n"
            "F8: Start/Stop Recording\n"
            "F9: Play Recorded Actions (Looping)\n"
            "ESC: Emergency Stop"
        )
        self.info_label = ctk.CTkLabel(self.root, text=info_text, justify="left")
        self.info_label.pack(pady=20)

    def update_speed(self, value):
        self.speed_modifier = float(value)

    def on_press(self, key):
        # Hotkey Management
        if key == Key.f8:
            self.toggle_record()
        elif key == Key.f9:
            self.start_playback_thread()
        elif key == Key.esc:
            self.is_playing = False
            self.is_recording = False 

        # Record Keyboard if recording
        if self.is_recording:
            # Avoid recording the hotkeys themselves
            if key not in [Key.f8, Key.f9, Key.esc]:
                self.record_event('kb_press', key=key)

    def on_release(self, key):
        if self.is_recording:
            if key not in [Key.f8, Key.f9, Key.esc]:
                self.record_event('kb_release', key=key)

    def on_click(self, x, y, button, pressed):
        if self.is_recording:
            self.record_event('mouse_click', x=x, y=y, button=button, pressed=pressed)

    def record_event(self, type, **kwargs):
        event_time = time.time() - self.start_time
        event = {'type': type, 'time': event_time}
        event.update(kwargs)
        self.recorded_data.append(event)

    def toggle_record(self):
        self.is_recording = not self.is_recording
        if self.is_recording:
            self.recorded_data = []
            self.start_time = time.time()
            self.status_label.configure(text="Status: RECORDING...", text_color="red")
        else:
            self.status_label.configure(text="Status: Saved", text_color="green")

    def start_playback_thread(self):
        if not self.is_playing and self.recorded_data:
            threading.Thread(target=self.play_back, daemon=True).start()

    def play_back(self):
        self.is_playing = True
        self.status_label.configure(text="Status: PLAYING (LOOP)", text_color="cyan")
        
        while self.is_playing:
            last_time = 0
            for event in self.recorded_data:
                if not self.is_playing: 
                    break
                
                # Adjust for Speed
                sleep_time = (event['time'] - last_time) / self.speed_modifier
                time.sleep(max(0, sleep_time))
                last_time = event['time']

                if event['type'] == 'mouse_click':
                    self.mouse_ctrl.position = (event['x'], event['y'])
                    if event['pressed']:
                        self.mouse_ctrl.press(event['button'])
                    else:
                        self.mouse_ctrl.release(event['button'])
                
                elif event['type'] == 'kb_press':
                    self.kb_ctrl.press(event['key'])
                elif event['type'] == 'kb_release':
                    self.kb_ctrl.release(event['key'])
            
            # Short pause before starting the next loop iteration
            time.sleep(0.01)

        self.status_label.configure(text="Status: Ready", text_color="white")

    def setup_listeners(self):
        self.key_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.key_listener.start()
        self.mouse_listener.start()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ProfessionalAutoClicker()
    app.run()