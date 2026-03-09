import cv2
import numpy as np
import sys
from immdebug import immdebug


cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    edges_float = edges.astype(np.float32) / 255.0

    cv2.imshow('Edges', edges)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

    if key == ord('d'):
        immdebug(edges, "edges")
        immdebug(frame, "frame")
        immdebug(gray, "gray")
        immdebug(edges_float, "edges_float")
