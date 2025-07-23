import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
import io
import os
import time
import random

COMFY_API_URL = "http://127.0.0.1:8000"  # Twój port ComfyUI

class ComfyUIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ComfyUI Prompt Generator")
        self.geometry("600x700")
        self.prompt_var = tk.StringVar()
        self.image_label = None
        self.create_widgets()

    def create_widgets(self):
        prompt_label = ttk.Label(self, text="Prompt:")
        prompt_label.pack(pady=(20, 5))
        prompt_entry = ttk.Entry(self, textvariable=self.prompt_var, width=70)
        prompt_entry.pack(pady=(0, 10))
        generate_btn = ttk.Button(self, text="Generuj obraz", command=self.generate_image)
        generate_btn.pack(pady=10)
        self.image_label = ttk.Label(self)
        self.image_label.pack(pady=20)

    def generate_image(self):
        prompt = self.prompt_var.get().strip()
        if not prompt:
            messagebox.showerror("Błąd", "Wpisz prompt!")
            return
        try:
            image_path = self.send_prompt_to_comfyui(prompt)
            if image_path:
                self.display_image(image_path)
            else:
                messagebox.showerror("Błąd", "Nie udało się wygenerować obrazu.")
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd: {e}")

    def send_prompt_to_comfyui(self, prompt):
        # Workflow zgodny z Twoim ComfyUI
        workflow = {
            "3": {
                "inputs": {
                    "seed": random.randint(0, 2**32-1),
                    "steps": 20,
                    "cfg": 8,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0]
                },
                "class_type": "KSampler",
                "_meta": {"title": "KSampler"}
            },
            "4": {
                "inputs": {
                    "ckpt_name": "v1-5-pruned-emaonly-fp16.safetensors"
                },
                "class_type": "CheckpointLoaderSimple",
                "_meta": {"title": "Load Checkpoint"}
            },
            "5": {
                "inputs": {
                    "width": 512,
                    "height": 512,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage",
                "_meta": {"title": "Empty Latent Image"}
            },
            "6": {
                "inputs": {
                    "text": prompt,
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "CLIP Text Encode (Prompt)"}
            },
            "7": {
                "inputs": {
                    "text": "text, watermark",
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "CLIP Text Encode (Prompt)"}
            },
            "8": {
                "inputs": {
                    "samples": ["3", 0],
                    "vae": ["4", 2]
                },
                "class_type": "VAEDecode",
                "_meta": {"title": "VAE Decode"}
            },
            "9": {
                "inputs": {
                    "filename_prefix": "ComfyUI_GUI",
                    "images": ["8", 0]
                },
                "class_type": "SaveImage",
                "_meta": {"title": "Save Image"}
            }
        }
        payload = {"prompt": workflow, "client_id": "test"}
        response = requests.post(f"{COMFY_API_URL}/prompt", json=payload)
        response.raise_for_status()
        prompt_id = response.json().get("prompt_id")
        if not prompt_id:
            raise Exception("Brak prompt_id w odpowiedzi ComfyUI")
        # Czekamy na wygenerowanie obrazu
        for _ in range(60):  # max 60 sek
            status = requests.get(f"{COMFY_API_URL}/history/{prompt_id}")
            status.raise_for_status()
            data = status.json()
            print("API response:", data)  # DEBUG: pokaż całą odpowiedź API
            if prompt_id in data and "outputs" in data[prompt_id]:
                outputs = data[prompt_id]["outputs"]
                for node in outputs:
                    images = outputs[node].get("images", [])
                    for output in images:
                        image_path = output.get("filename")
                        if image_path:
                            home = os.path.expanduser("~")
                            # Automatycznie wykrywaj katalog output w Documents bieżącego użytkownika
                            documents = os.path.join(os.path.expanduser("~"), "Documents")
                            comfyui_output = os.path.join(documents, "ComfyUI", "output")
                            possible_dirs = [
                                os.path.join(home, "ComfyUI", "output"),
                                os.path.join(os.getcwd(), "output"),
                                comfyui_output,
                            ]
                            for d in possible_dirs:
                                full_path = os.path.join(d, image_path)
                                print("Sprawdzam:", full_path)  # DEBUG: pokaż sprawdzaną ścieżkę
                                if os.path.exists(full_path):
                                    return full_path
            time.sleep(1)
        return None

    def display_image(self, image_path):
        img = Image.open(image_path)
        img = img.resize((512, 512))
        img_tk = ImageTk.PhotoImage(img)
        self.image_label.configure(image=img_tk)
        self.image_label.image = img_tk

if __name__ == "__main__":
    app = ComfyUIApp()
    app.mainloop() 