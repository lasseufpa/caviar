import numpy as np
import cv2

from ultralytics import YOLO
model = YOLO("yolov8n.pt")

image = cv2.imread("/home/joaoborges/Downloads/airsimtest.png")
gaussian_noise = np.zeros(np.array(image).shape, np.uint8)

# cv2.randn(gaussian_noise, 0, 270) 
# gaussian_noise = gaussian_noise-100 # PSNR: 8.1041 dB
# cv2.randn(gaussian_noise, 0, 270) # PSNR: 15.8578 dB
# cv2.randn(gaussian_noise, 0, 90) # PSNR: 19.1642 dB
# cv2.randn(gaussian_noise, 0, 45) # PSNR: 23.585 dB
# cv2.randn(gaussian_noise, 0, 35) # PSNR: 25.2878 dB
cv2.randn(gaussian_noise, 0, 30) # PSNR: 26.5537 dB
# cv2.randn(gaussian_noise, 0, 25) # PSNR: 28.0667 dB
# cv2.randn(gaussian_noise, 0, 10) # PSNR: 35.9116 dB


degraded_image = cv2.add(image, gaussian_noise)
psnr = cv2.PSNR(image, degraded_image)

cv2.imwrite("degraded_image.jpg", degraded_image)

print(f'PSNR: {round(psnr, 4)} dB')

results = model.predict(source=degraded_image, classes=0, save=True)  # save predictions as labels

try:
    print(f'Detected class: {results[0].boxes.data[0,5]}')
    print(f'Human detected probability: {results[0].boxes.data[0,4]}')
except:
    print("NO DETECTION")