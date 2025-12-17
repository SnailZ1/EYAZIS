import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import speech_recognition as sr
import pyttsx3
import threading
import os
import pythoncom
import edge_tts
import asyncio
import pygame
import time


class EnglishVoiceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("English Voice System (STT & TTS)")
        self.root.geometry("900x800")

        # --- Инициализация систем ---
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        self.is_listening = False
        self.stop_tts_flag = threading.Event()

        try:
            pythoncom.CoInitialize()
            self.offline_engine = pyttsx3.init()
        except:
            self.offline_engine = None

        self.setup_engines()
        self.build_ui()

    def setup_engines(self):
        """Настройка голосов с учетом пола"""
        self.voice_map = {}
        self.voice_names = []

        # 1. Offline Voices (SAPI5) - Названия зависят от системы
        try:
            voices = self.offline_engine.getProperty('voices')
            for v in voices:
                v_id_low = v.id.lower()
                v_name_low = v.name.lower()
                if "english" in v_name_low or ("en" in v_id_low and "ru" not in v_id_low):
                    gender = "Male" if "david" in v_name_low else "Female" if "zira" in v_name_low else "Voice"
                    name = f"[Offline] {v.name} ({gender})"
                    self.voice_names.append(name)
                    self.voice_map[name] = {"type": "offline", "id": v.id}
        except:
            pass

        # 2. Online Voices (Edge TTS)
        edge_variants = [
            ("US Male (Guy)", "en-US-GuyNeural"),
            ("US Female (Aria)", "en-US-AriaNeural"),
            ("UK Male (Ryan)", "en-GB-RyanNeural"),
            ("UK Female (Sonia)", "en-GB-SoniaNeural"),
            ("AU Male (William)", "en-AU-WilliamNeural"),
        ]
        for label, voice_id in edge_variants:
            key = f"[Online] {label}"
            self.voice_names.append(key)
            self.voice_map[key] = {"type": "edge", "voice": voice_id}

    def build_ui(self):
        # --- СЕКЦИЯ РАСПОЗНАВАНИЯ (STT) ---
        stt_frame = ttk.LabelFrame(self.root, text="English Speech Recognition")
        stt_frame.pack(fill="x", padx=10, pady=5)

        self.btn_record = ttk.Button(stt_frame, text="🎙️ Start Listening", command=self.toggle_recording)
        self.btn_record.pack(side="left", padx=10, pady=10)

        self.btn_file = ttk.Button(stt_frame, text="📁 Open WAV File", command=self.recognize_from_file)
        self.btn_file.pack(side="left", padx=5)

        # --- ТЕКСТОВОЕ ПОЛЕ ---
        self.text_area = tk.Text(self.root, wrap="word", font=("Segoe UI", 11), height=15)
        self.text_area.pack(fill="both", expand=True, padx=10, pady=5)

        # --- СЕКЦИЯ СИНТЕЗА (TTS) ---
        tts_frame = ttk.LabelFrame(self.root, text="English Text to Speech Settings")
        tts_frame.pack(fill="x", padx=10, pady=5)

        # Выбор голоса
        ttk.Label(tts_frame, text="Select Voice Model:").grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.voice_combo = ttk.Combobox(tts_frame, values=self.voice_names, state="readonly", width=50)
        if self.voice_names: self.voice_combo.current(0)
        self.voice_combo.grid(row=0, column=1, columnspan=3, padx=5, pady=10, sticky="w")

        # Скорость
        ttk.Label(tts_frame, text="Speed (Rate):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.rate_scale = ttk.Scale(tts_frame, from_=50, to=250, orient="horizontal")
        self.rate_scale.set(150)
        self.rate_scale.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Громкость
        ttk.Label(tts_frame, text="Volume:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.vol_scale = ttk.Scale(tts_frame, from_=0.0, to=1.0, orient="horizontal")
        self.vol_scale.set(1.0)
        self.vol_scale.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

        # Кнопки управления
        btn_box = ttk.Frame(tts_frame)
        btn_box.grid(row=2, column=0, columnspan=4, pady=15)

        self.btn_play = ttk.Button(btn_box, text="▶ Play Text", command=self.on_play)
        self.btn_play.pack(side="left", padx=10)
        self.btn_stop = ttk.Button(btn_box, text="⏹ Stop Audio", command=self.on_stop_tts)
        self.btn_stop.pack(side="left", padx=10)

        # Статус-бар
        self.status_var = tk.StringVar(value="System Ready (English Only)")
        ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w").pack(fill="x", side="bottom")

    # --- ЛОГИКА РАСПОЗНАВАНИЯ ---
    def toggle_recording(self):
        if not self.is_listening:
            self.is_listening = True
            self.btn_record.config(text="⏹ Stop Listening")
            threading.Thread(target=self.listen_loop, daemon=True).start()
        else:
            self.is_listening = False
            self.btn_record.config(text="🎙️ Start Listening")

    def listen_loop(self):
        try:
            with self.mic as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                while self.is_listening:
                    self.status_var.set("Listening to English speech...")
                    try:
                        audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=10)
                        text = self.recognizer.recognize_google(audio, language="en-US")
                        self.root.after(0, lambda t=text: self.text_area.insert(tk.END, t + " "))
                    except sr.UnknownValueError:
                        continue
                    except Exception:
                        break
        finally:
            self.status_var.set("Ready")

    def recognize_from_file(self):
        path = filedialog.askopenfilename(filetypes=[("Audio", "*.wav")])
        if not path: return

        def _proc():
            try:
                self.status_var.set("Processing file...")
                with sr.AudioFile(path) as s:
                    a = self.recognizer.record(s)
                t = self.recognizer.recognize_google(a, language="en-US")
                self.root.after(0, lambda: self.text_area.insert(tk.END, f"\n{t}\n"))
            except Exception as e:
                messagebox.showerror("Error", f"Could not process file: {e}")
            self.status_var.set("Ready")

        threading.Thread(target=_proc).start()

    # --- ЛОГИКА СИНТЕЗА ---
    def on_play(self):
        text = self.text_area.get("1.0", tk.END).strip()
        if not text: return

        self.stop_tts_flag.clear()
        selected_voice = self.voice_combo.get()
        voice_data = self.voice_map.get(selected_voice)
        rate = int(self.rate_scale.get())
        vol = self.vol_scale.get()

        if voice_data['type'] == 'offline':
            threading.Thread(target=self.run_offline, args=(text, voice_data['id'], rate, vol), daemon=True).start()
        elif voice_data['type'] == 'edge':
            threading.Thread(target=self.run_edge_tts, args=(text, voice_data['voice'], rate, vol), daemon=True).start()

    def run_offline(self, text, v_id, rate, vol):
        f_name = "offline_temp.wav"
        try:
            self.status_var.set("Generating Offline TTS...")

            pythoncom.CoInitialize()
            local_engine = pyttsx3.init()

            local_engine.setProperty('voice', v_id)
            local_engine.setProperty('rate', int(rate))
            local_engine.setProperty('volume', float(vol))

            if os.path.exists(f_name):
                try:
                    os.remove(f_name)
                except:
                    pass

            local_engine.save_to_file(text, f_name)
            local_engine.runAndWait()

            pygame.mixer.music.load(f_name)
            pygame.mixer.music.set_volume(float(vol))
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                if self.stop_tts_flag.is_set():
                    pygame.mixer.music.stop()
                    break
                time.sleep(0.1)

        except Exception as e:
            messagebox.showerror("Offline Error", f"Error: {e}")
        finally:
            self.status_var.set("Ready")
            pythoncom.CoUninitialize()

    def run_edge_tts(self, text, voice, rate, vol):
        f_name = "english_temp.mp3"
        try:
            self.status_var.set(f"Generating Edge TTS ({voice})...")

            speed_percent = int(rate - 150)
            speed_str = f"{speed_percent:+d}%"

            communicate = edge_tts.Communicate(text, voice, rate=speed_str)
            asyncio.run(communicate.save(f_name))

            pygame.mixer.music.load(f_name)
            pygame.mixer.music.set_volume(float(vol))
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                if self.stop_tts_flag.is_set():
                    pygame.mixer.music.stop()
                    break
                time.sleep(0.1)
        except Exception as e:
            messagebox.showerror("Error", f"Edge TTS Error: {e}")
        finally:
            self.status_var.set("Ready")

    def on_stop_tts(self):
        self.stop_tts_flag.set()
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()


if __name__ == "__main__":
    root = tk.Tk()
    app = EnglishVoiceApp(root)
    root.mainloop()