from ultralytics import YOLO
import subprocess
import cv2
import time


'''

This script captures an RTSP stream, processes it with a YOLOv8 model for object detection,
and streams the processed video back to an RTSP server using FFmpeg. This is done
inside the internet node (which is a docker container) of the ns3 simulation.
This scriipt wull be copied to the docker container and executed there.

It automatically reconnects to the RTSP stream if it is lost and handles FFmpeg errors gracefully.
'''

rtsp_url = "rtsp://10.1.1.2:8554/mystream"
model = YOLO("yolov8n.pt")

ffmpeg_command = [
    "ffmpeg",
    "-probesize", "4M",
    "-analyzeduration", "500000",
    "-framerate", "10",
    "-video_size", "1280x720",
    "-f", "rawvideo",
    "-pix_fmt", "bgr24",
    "-i", "-",
    "-c:v", "libx264",
    "-preset", "ultrafast",
    "-rtbufsize", "10M",
    "-x264-params", "keyint=10:min-keyint=10",
    "-tune", "zerolatency",
    "-f", "rtsp",
    "rtsp://localhost:8554/mystream",
]


import signal
import sys

def signal_handler(sig, frame):
    print("Signal received, terminating...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def get_stream():
    while True:
        cap = cv2.VideoCapture(rtsp_url)
        if cap.isOpened():
            print("Connected to RTSP stream.")
            return cap
        print("Waiting for RTSP stream to be available...")
        cap.release()
        time.sleep(1)

def process_stream():
    while True:
        cap = get_stream()
        ffmpeg = subprocess.Popen(
            ffmpeg_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                print("Stream lost. Reconnecting...")
                cap.release()
                ffmpeg.stdin.close()
                ffmpeg.terminate()
                time.sleep(1)
                break

            results = model(frame)
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = box.conf[0]
                    cls = int(box.cls[0])
                    label = f"{model.names[cls]} {conf:.2f}"
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    cv2.putText(
                        frame,
                        label,
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (255, 0, 0),
                        2,
                    )
            try:
                ffmpeg.stdin.write(frame.tobytes())
                ffmpeg.stdin.flush()
            except Exception as e:
                print("FFmpeg error:", e)
                cap.release()
                ffmpeg.stdin.close()
                ffmpeg.terminate()
                time.sleep(1)
                break

process_stream()
