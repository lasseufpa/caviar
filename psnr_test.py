import numpy as np
import cv2


image = cv2.imread("/home/joaoborges/codes/caviar/runs/detect/predict/image0.jpg")
gaussian_noise = np.zeros(np.array(image).shape, np.uint8)


# cv2.randn(gaussian_noise, 0, 270) # PSNR: 17.2753 dB
cv2.randn(gaussian_noise, 0, 90) # PSNR: 20.0811 dB
# cv2.randn(gaussian_noise, 0, 45) # PSNR: 23.8298 dB


degraded_image = cv2.add(image, gaussian_noise)
psnr = cv2.PSNR(image, degraded_image)


print(f'PSNR: {round(psnr, 4)} dB')
