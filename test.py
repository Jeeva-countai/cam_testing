import cv2

# Replace the device path with the actual device path if necessary
camera_device = "/dev/v4l/by-path/pci-0000:00:14.0-usb-0:4:1.0-video-index0"

# Open the camera
cap = cv2.VideoCapture(camera_device)

if not cap.isOpened():
    print("Error: Could not open video device")
    exit()

# Set the desired properties (optional)
cap.set(cv2.CAP_PROP_EXPOSURE, -1)  # You can set exposure or other properties here
cap.set(cv2.CAP_PROP_GAIN, 0)  # Set gain to 0 if needed

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Display the resulting frame
    cv2.imshow("Camera Feed", frame)

    # Press 'q' to exit the loop and close the window
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close any OpenCV windows
cap.release()
cv2.destroyAllWindows()
