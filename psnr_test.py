import numpy as np
import cv2
import time
from PIL import Image as img
from degradeImage import dropPacketsFromImage, applyFilter

# from ultralytics import YOLO

# model = YOLO("yolov8n.pt")

init_1 = time.time()
image = cv2.imread("/home/joao/Downloads/airsimtest.png", cv2.IMREAD_UNCHANGED)
gaussian_noise = np.zeros(np.array(image).shape, np.uint8)
# cv2.randn(gaussian_noise, 0, 270)
# gaussian_noise = gaussian_noise-100 # PSNR: 8.1041 dB
cv2.randn(gaussian_noise, 0, 270)  # PSNR: 15.8578 dB
# cv2.randn(gaussian_noise, 0, 90) # PSNR: 19.1642 dB
# cv2.randn(gaussian_noise, 0, 45) # PSNR: 23.585 dB
# cv2.randn(gaussian_noise, 0, 35) # PSNR: 25.2878 dB
# cv2.randn(gaussian_noise, 0, 30) # PSNR: 26.5537 dB
# cv2.randn(gaussian_noise, 0, 25) # PSNR: 28.0667 dB
# cv2.randn(gaussian_noise, 0, 10) # PSNR: 35.9116 dB
degraded_image = cv2.add(image, gaussian_noise)
cv2.imwrite("/home/joao/Downloads/degraded_image.png", degraded_image)
end_1 = time.time()
################################################################################

init_2 = time.time()
image2 = img.open("/home/joao/Downloads/airsimtest.png")

# dropPacketsFromImage(
#     image, 0.01
# )  # PSNR: 26.3629 dB | Human detected probability: 0.48686936497688293
# dropPacketsFromImage(
#     image, 0.1
# )  # PSNR: 16.3643 dB | Human detected probability: 0.5403681993484497
# dropPacketsFromImage(
#     image, 0.25
# )  # PSNR: 12.3902 dB | Human detected probability: 0.42502260208129883
dropPacketsFromImage(
    image2, 0.5
)  # PSNR: 9.376 dB   | Human detected probability: NO DETECTION
end_2 = time.time()
# time.sleep(1)
# image = cv2.imread("/home/joao/Downloads/airsimtest.png", cv2.IMREAD_UNCHANGED)
# degraded_image = cv2.imread("/home/joao/Downloads/fromBytes.png", cv2.IMREAD_UNCHANGED)
# psnr = cv2.PSNR(image, degraded_image)

# print(f"PSNR: {round(psnr, 4)} dB")

# results = model.predict(
#     source=degraded_image, classes=0, save=True
# )  # save predictions as labels

# try:
#     print(f"Detected class: {results[0].boxes.data[0,5]}")
#     print(f"Human detected probability: {results[0].boxes.data[0,4]}")
# except:
#     print("NO DETECTION")

init_3 = time.time()
applyFilter(image, 0.5)
end_3 = time.time()

print(f"openCV_Noise = {(end_1-init_1) * 1e3} ms")
print(f"pixel_drop = {(end_2-init_2) * 1e3} ms")
print(f"pixel_filter = {(end_3-init_3) * 1e3} ms")
