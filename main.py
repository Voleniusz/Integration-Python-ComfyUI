import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
import io
import os
import time
import random

COMFY_API_URL = "http://127.0.0.1:8000"

class ComfyUIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ComfyUI Prompt Generator")
        self.geometry("700x900")
        self.prompt_var = tk.StringVar()
        self.negative_prompt_var = tk.StringVar()
        self.model_var = tk.StringVar()
        self.width_var = tk.IntVar(value=512)
        self.height_var = tk.IntVar(value=512)
        self.seed_var = tk.StringVar()
        self.steps_var = tk.IntVar(value=20)
        self.cfg_var = tk.DoubleVar(value=8.0)
        self.image_label = None
        self.models = self.get_models()
        if self.models:
            self.model_var.set(self.models[0])
        self.model_download_url = tk.StringVar()
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)
        self.create_image_tab()
        self.create_video_tab()
        self.create_models_tab()

    def get_models(self):
        models_dir = os.path.join(os.path.expanduser("~"), "Documents", "ComfyUI", "models", "checkpoints")
        if not os.path.exists(models_dir):
            models_dir = os.path.join(os.getcwd(), "models", "checkpoints")
        if not os.path.exists(models_dir):
            return []
        return [f for f in os.listdir(models_dir) if f.endswith(".safetensors")]

    def refresh_models(self):
        self.models = self.get_models()
        if self.models:
            self.model_var.set(self.models[0])
        else:
            self.model_var.set("")
        if hasattr(self, 'model_combo'):
            self.model_combo['values'] = self.models

    def create_image_tab(self):
        image_tab = ttk.Frame(self.notebook)
        self.notebook.add(image_tab, text="Obraz")
        row = 0
        ttk.Label(image_tab, text="Prompt:").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        prompt_entry = ttk.Entry(image_tab, textvariable=self.prompt_var, width=70)
        prompt_entry.grid(row=row, column=1, padx=10, pady=5)
        row += 1
        ttk.Label(image_tab, text="Negatywny prompt:").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        negative_entry = ttk.Entry(image_tab, textvariable=self.negative_prompt_var, width=70)
        negative_entry.grid(row=row, column=1, padx=10, pady=5)
        row += 1
        ttk.Label(image_tab, text="Model:").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        self.model_combo = ttk.Combobox(image_tab, textvariable=self.model_var, values=self.models, width=67, state="readonly")
        self.model_combo.grid(row=row, column=1, padx=10, pady=5)
        row += 1
        ttk.Label(image_tab, text="Szerokość:").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        width_entry = ttk.Entry(image_tab, textvariable=self.width_var, width=10)
        width_entry.grid(row=row, column=1, sticky="w", padx=10, pady=5)
        row += 1
        ttk.Label(image_tab, text="Wysokość:").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        height_entry = ttk.Entry(image_tab, textvariable=self.height_var, width=10)
        height_entry.grid(row=row, column=1, sticky="w", padx=10, pady=5)
        row += 1
        ttk.Label(image_tab, text="Seed (puste = losowy):").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        seed_entry = ttk.Entry(image_tab, textvariable=self.seed_var, width=20)
        seed_entry.grid(row=row, column=1, sticky="w", padx=10, pady=5)
        row += 1
        ttk.Label(image_tab, text="Steps:").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        steps_entry = ttk.Entry(image_tab, textvariable=self.steps_var, width=10)
        steps_entry.grid(row=row, column=1, sticky="w", padx=10, pady=5)
        row += 1
        ttk.Label(image_tab, text="CFG:").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        cfg_entry = ttk.Entry(image_tab, textvariable=self.cfg_var, width=10)
        cfg_entry.grid(row=row, column=1, sticky="w", padx=10, pady=5)
        row += 1
        generate_btn = ttk.Button(image_tab, text="Generuj obraz", command=self.generate_image)
        generate_btn.grid(row=row, column=0, columnspan=2, pady=15)
        row += 1
        self.image_label = ttk.Label(image_tab)
        self.image_label.grid(row=row, column=0, columnspan=2, pady=20)

    def create_video_tab(self):
        video_tab = ttk.Frame(self.notebook)
        self.notebook.add(video_tab, text="Wideo")
        ttk.Label(video_tab, text="Generowanie wideo - wkrótce").pack(pady=50)

    def create_models_tab(self):
        models_tab = ttk.Frame(self.notebook)
        self.notebook.add(models_tab, text="Modele")
        row = 0
        ttk.Label(models_tab, text="Link do pliku .safetensors:").grid(row=row, column=0, sticky="w", padx=10, pady=10)
        url_entry = ttk.Entry(models_tab, textvariable=self.model_download_url, width=70)
        url_entry.grid(row=row, column=1, padx=10, pady=10)
        row += 1
        download_btn = ttk.Button(models_tab, text="Pobierz model", command=self.download_model)
        download_btn.grid(row=row, column=0, columnspan=2, pady=10)
        row += 1
        self.models_listbox = tk.Listbox(models_tab, width=80, height=10)
        self.models_listbox.grid(row=row, column=0, columnspan=2, padx=10, pady=10)
        self.refresh_models_listbox()

    def refresh_models_listbox(self):
        self.refresh_models()
        if hasattr(self, 'models_listbox'):
            self.models_listbox.delete(0, tk.END)
            for m in self.models:
                self.models_listbox.insert(tk.END, m)

    def download_model(self):
        url = self.model_download_url.get().strip()
        if not url or not url.endswith('.safetensors'):
            messagebox.showerror("Błąd", "Podaj poprawny link do pliku .safetensors")
            return
        models_dir = os.path.join(os.path.expanduser("~"), "Documents", "ComfyUI", "models", "checkpoints")
        if not os.path.exists(models_dir):
            os.makedirs(models_dir)
        filename = os.path.basename(url)
        dest_path = os.path.join(models_dir, filename)
        try:
            r = requests.get(url, stream=True)
            r.raise_for_status()
            with open(dest_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            messagebox.showinfo("Sukces", f"Model pobrany: {filename}")
            self.refresh_models_listbox()
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się pobrać modelu: {e}")

    def generate_image(self):
        prompt = self.prompt_var.get().strip()
        negative_prompt = self.negative_prompt_var.get().strip()
        model = self.model_var.get().strip()
        width = self.width_var.get()
        height = self.height_var.get()
        steps = self.steps_var.get()
        cfg = self.cfg_var.get()
        seed = self.seed_var.get().strip()
        if not prompt:
            messagebox.showerror("Błąd", "Wpisz prompt!")
            return
        if not model:
            messagebox.showerror("Błąd", "Wybierz model!")
            return
        try:
            image_path = self.send_prompt_to_comfyui(prompt, negative_prompt, model, width, height, steps, cfg, seed)
            if image_path:
                self.display_image(image_path)
            else:
                messagebox.showerror("Błąd", "Nie udało się wygenerować obrazu.")
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd: {e}")

    def send_prompt_to_comfyui(self, prompt, negative_prompt, model, width, height, steps, cfg, seed):
        if not seed:
            seed = random.randint(0, 2**32-1)
        else:
            try:
                seed = int(seed)
            except ValueError:
                seed = random.randint(0, 2**32-1)
        workflow = {
            "3": {
                "inputs": {
                    "seed": seed,
                    "steps": steps,
                    "cfg": cfg,
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
                    "ckpt_name": model
                },
                "class_type": "CheckpointLoaderSimple",
                "_meta": {"title": "Load Checkpoint"}
            },
            "5": {
                "inputs": {
                    "width": width,
                    "height": height,
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
                    "text": negative_prompt if negative_prompt else "text, watermark",
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
        for _ in range(60):
            status = requests.get(f"{COMFY_API_URL}/history/{prompt_id}")
            status.raise_for_status()
            data = status.json()
            if prompt_id in data and "outputs" in data[prompt_id]:
                outputs = data[prompt_id]["outputs"]
                for node in outputs:
                    images = outputs[node].get("images", [])
                    for output in images:
                        image_path = output.get("filename")
                        if image_path:
                            home = os.path.expanduser("~")
                            documents = os.path.join(os.path.expanduser("~"), "Documents")
                            comfyui_output = os.path.join(documents, "ComfyUI", "output")
                            possible_dirs = [
                                os.path.join(home, "ComfyUI", "output"),
                                os.path.join(os.getcwd(), "output"),
                                comfyui_output,
                            ]
                            for d in possible_dirs:
                                full_path = os.path.join(d, image_path)
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