import os
from PIL import Image, ImageTk
import supervision as sv
from inference import get_model
from dotenv import load_dotenv
import json
import tkinter as tk
from tkinter import filedialog, messagebox, Scrollbar, Canvas, Frame
import sys

if getattr(sys, 'frozen', False):
  # If running in PyInstaller, use the folder where the executable is located
  base_path = sys._MEIPASS
else:
  # Otherwise, use the current working directory
  base_path = os.path.dirname(__file__)

dotenv_path = os.path.join(base_path, '.env')
load_dotenv(dotenv_path)

api_key = os.getenv("API_KEY")

model = get_model(model_id="annulation-region-detection/1", api_key=api_key)

def log_message(message):
  log_text.insert(tk.END, message + '\n')
  log_text.see(tk.END)
  root.update()

def select_folder():
  selected_folder = filedialog.askdirectory()
  if selected_folder:
    folder_label.config(text=f"Selected folder: {selected_folder}")
  else:
    messagebox.showinfo("Info", "No folder selected")

def deselect_folder():
  folder_label.config(text="No folder selected")

def select_file():
  selected_file = filedialog.askopenfilename(filetypes=[("Image Files", ".png .jpg .jpeg")])
  if selected_file:
    file_label.config(text=f"Selected file: {selected_file}")
  else:
    messagebox.showinfo("Info", "No file selected")

def deselect_file():
  file_label.config(text="No file selected")

def annulation_region_process(path, file, confidence_threshold):
  polygon_annotator = sv.PolygonAnnotator()

  image = Image.open(path)
  results = model.infer(image=path)[0]
  predictions_json = results.json()
  
  predictions = json.loads(predictions_json)["predictions"]
  detections = sv.Detections.from_inference(results)

  if len(predictions) > 0 and predictions[0]["confidence"] > confidence_threshold:
    annotated_image = polygon_annotator.annotate(scene=image.copy(), detections=detections)

    print(f"Annotated Image: {annotated_image}")
    img = Image.open(annotated_image) if isinstance(annotated_image, str) else annotated_image
    print(f"Image loaded: {img}")

    img.thumbnail((300, 300))
    img = ImageTk.PhotoImage(img)

    processed_images.append((file, annotated_image))
    
    label = tk.Label(image_frame, image=img)
    label.image = img
    label.pack(side=tk.TOP, padx=5, pady=5)

    print(f"Processed {file}")
    log_message(f"Processed {file}")

    canvas.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))
  else:
    print(f"No confident prediction for {file}")
    log_message(f"No confident prediction for {file}. Confidence of region for this image is {predictions[0]['confidence'] if len(predictions) > 0 else 0}.")

def detect_annulation_region(option):
  global processed_images
  directory = folder_label.cget("text").replace("Selected folder: ", "")  
  confidence_threshold = confidence_slider.get()

  processed_images = []

  for widget in image_frame.winfo_children():
    widget.destroy()

  if option == 1:
    for dirpath, dirnames, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                path = os.path.join(dirpath, file)
                annulation_region_process(path, file, confidence_threshold)
    log_message("Finished processing folder.")
                
  else:
    path = file_label.cget("text").replace("Selected file: ", "")  
    file = os.path.basename(path)
    annulation_region_process(path, file, confidence_threshold)


def save_images():
    save_directory = filedialog.askdirectory()
    if save_directory:
        for file_name, pil_img in processed_images:
            save_path = os.path.join(save_directory, f"processed_{file_name}")
            pil_img.save(save_path)
        messagebox.showinfo("Info", "Images saved successfully!")

def restart():
  deselect_file()
  deselect_folder()
  processed_images = []
  for widget in image_frame.winfo_children():
    widget.destroy()

root = tk.Tk()
root.title("Tooth Annulation Annotation")
root.geometry("800x600")

# Canvas and scrollbar setup
canvas = tk.Canvas(root)
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)
canvas.config(yscrollcommand=scrollbar.set)

# Frame inside the canvas for images
image_frame = tk.Frame(canvas)
canvas.create_window((0, 0), window=image_frame, anchor="nw")

# Bind resize event to adjust canvas scroll region
def on_canvas_configure(event):
    canvas.config(scrollregion=canvas.bbox("all"))

canvas.bind("<Configure>", on_canvas_configure)


folder_button_frame = tk.Frame(root)
folder_button_frame.pack(pady=10)  

folder_btn = tk.Button(folder_button_frame, text="Select Folder", command=select_folder)
folder_btn.pack(side=tk.LEFT, padx=5)

deselect_folder_btn = tk.Button(folder_button_frame, text="Clear Folder", command=deselect_folder)
deselect_folder_btn.pack(side=tk.LEFT, padx=5)

folder_label = tk.Label(root, text="No folder selected")
folder_label.pack(pady=5)

file_button_frame = tk.Frame(root)
file_button_frame.pack(pady=10)

file_btn = tk.Button(file_button_frame, text="Select File", command=select_file)
file_btn.pack(side=tk.LEFT, padx=10)

deselect_file_btn = tk.Button(file_button_frame, text="Clear File", command=deselect_file)
deselect_file_btn.pack(side=tk.LEFT, padx=10)

file_label = tk.Label(root, text="No file selected")
file_label.pack(pady=5)

confidence_slider = tk.Scale(root, from_=0.5, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, label="Confidence Threshold")
confidence_slider.set(0.9)
confidence_slider.pack(pady=10)

process_folder_btn = tk.Button(root, text="Process Folder", command=lambda: detect_annulation_region(1))
process_folder_btn.pack(pady=10)

process_file_btn = tk.Button(root, text="Process File", command=lambda: detect_annulation_region(0))
process_file_btn.pack(pady=10)

menu = tk.Frame(root)
menu.pack(pady=10)

save_btn = tk.Button(menu, text="Save Images", command=save_images)
save_btn.pack(side=tk.LEFT, padx=10)

restart_btn = tk.Button(menu, text="Restart", command=restart)
restart_btn.pack(side=tk.LEFT, padx=10)

log_text = tk.Text(root, height=10, wrap=tk.WORD)
log_text.pack(pady=10)

root.mainloop()