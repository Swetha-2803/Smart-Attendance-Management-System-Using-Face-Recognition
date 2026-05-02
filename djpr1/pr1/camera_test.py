import cv2

cap = None
for i in range(10):
    temp_cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
    if temp_cap.isOpened():
        cap = temp_cap
        print(f"✅ Camera opened at index {i}")
        break
    temp_cap.release()

if cap is None:
    print("❌ No camera detected. Check drivers or port.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to grab frame")
        break
    cv2.imshow("Camera Test", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
