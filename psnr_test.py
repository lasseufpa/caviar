import numpy as np
import cv2
import time
from PIL import Image as img
from degradeImage import dropPacketsFromImage

from ultralytics import YOLO
model = YOLO("yolov8n.pt")

# image = cv2.imread("/home/joaoborges/Downloads/airsimtest.png")
# gaussian_noise = np.zeros(np.array(image).shape, np.uint8)
# cv2.randn(gaussian_noise, 0, 270) 
# gaussian_noise = gaussian_noise-100 # PSNR: 8.1041 dB
# cv2.randn(gaussian_noise, 0, 270) # PSNR: 15.8578 dB
# cv2.randn(gaussian_noise, 0, 90) # PSNR: 19.1642 dB
# cv2.randn(gaussian_noise, 0, 45) # PSNR: 23.585 dB
# cv2.randn(gaussian_noise, 0, 35) # PSNR: 25.2878 dB
# cv2.randn(gaussian_noise, 0, 30) # PSNR: 26.5537 dB
# cv2.randn(gaussian_noise, 0, 25) # PSNR: 28.0667 dB
# cv2.randn(gaussian_noise, 0, 10) # PSNR: 35.9116 dB
# degraded_image = cv2.add(image, gaussian_noise)
# cv2.imwrite("degraded_image.jpg", degraded_image)

image = img.open("/home/joaoborges/Downloads/airsimtest.png")

# dropPacketsFromImage(image, 0.01)# PSNR: 26.3629 dB | Human detected probability: 0.48686936497688293
# dropPacketsFromImage(image, 0.1) # PSNR: 16.3643 dB | Human detected probability: 0.5403681993484497
# dropPacketsFromImage(image, 0.25)# PSNR: 12.3902 dB | Human detected probability: 0.42502260208129883
# dropPacketsFromImage(image, 0.5)# PSNR: 9.376 dB | Human detected probability: NO DETECTION

time.sleep(1)
image = cv2.imread("/home/joaoborges/Downloads/airsimtest.png")
degraded_image = cv2.imread("/home/joaoborges/Downloads/fromBytes.png")
psnr = cv2.PSNR(image, degraded_image)

print(f'PSNR: {round(psnr, 4)} dB')

results = model.predict(source=degraded_image, classes=0, save=True)  # save predictions as labels

try:
    print(f'Detected class: {results[0].boxes.data[0,5]}')
    print(f'Human detected probability: {results[0].boxes.data[0,4]}')
except:
    print("NO DETECTION")