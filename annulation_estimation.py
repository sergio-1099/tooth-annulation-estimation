import tkinter as tk
from tkinter import filedialog, messagebox, Scrollbar, Canvas, Frame
import os
from tensorflow.keras.models import load_model
import supervision as sv
from inference import get_model
from dotenv import load_dotenv
from PIL import Image, ImageTk
import numpy as np
import csv
import json
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

model_path = os.path.join(base_path, 'model', 'model-only-redone-images.h5')

model = load_model(model_path)
region_confidence_model = get_model(model_id="annulation-region-detection/1", api_key=api_key)

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

def process_image(path):
  new_size = (500, 500)
  image = Image.open(path)
  resized_image = image.resize(new_size)
  image_array = np.array(resized_image)
  image_array = np.expand_dims(image_array, axis=0)

  prediction = model.predict(image_array)

  results = region_confidence_model.infer(image=path)[0]
  predictions_json = results.json()
  
  region_predictions = json.loads(predictions_json)["predictions"]

  return [prediction[0][0], region_predictions[0]["confidence"] if len(region_predictions) > 0 else 0]

def predict_annulations(option):
  if option == 1:
    save_directory = filedialog.askdirectory()
    csv_file = os.path.join(save_directory, 'annulation_predictions.csv')
    file_exists = os.path.isfile(csv_file)

    with open(csv_file, mode='a', newline='') as file:
      writer = csv.writer(file)

      if not file_exists:
        writer.writerow(['File Name', 'Predicted Annulation Count', 'Region Confidence'])

      directory = folder_label.cget("text").replace("Selected folder: ", "")
      
      for dirpath, dirnames, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
              path = os.path.join(dirpath, file)
              annulation_prediction, region_confidence = process_image(path)

              writer.writerow([file, annulation_prediction, region_confidence])
              log_message(f"Processed {file}. Annulation count: {annulation_prediction}")
      log_message("Processed all files in folder.")
  else: 
    path = file_label.cget("text").replace("Selected file: ", "")
    annulation_prediction, region_confidence = process_image(path)

    log_message(f"Processed {os.path.basename(path)}")
    log_message(f"Predicted number of annulations: {annulation_prediction}")
    log_message(f"Confidence of Region Detection: {region_confidence}")

root = tk.Tk()
root.title("Tooth Annulation Estimation")
root.geometry("800x600")

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

predict_button_frame = tk.Frame(root)
predict_button_frame.pack(pady=10)  

predict_folder_btn = tk.Button(predict_button_frame, text="Predict Folder Annulations", command=lambda: predict_annulations(1))
predict_folder_btn.pack(side=tk.LEFT, padx=5)

predict_file_btn = tk.Button(predict_button_frame, text="Predict File Annulations", command=lambda: predict_annulations(0))
predict_file_btn.pack(side=tk.LEFT, padx=5)

log_text = tk.Text(root, height=10, wrap=tk.WORD)
log_text.pack(pady=10)

root.mainloop()