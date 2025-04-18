import cv2

# Paths to model files
faceProto = 'models/opencv_face_detector.pbtxt'
faceModel = 'models/opencv_face_detector_uint8.pb'
genderProto = 'models/gender_deploy.prototxt'
genderModel = 'models/gender_net.caffemodel'

# Load the models
try:
    faceNet = cv2.dnn.readNet(faceModel, faceProto)
    genderNet = cv2.dnn.readNet(genderModel, genderProto)
    print("Models loaded successfully.") 
except Exception as e:
    print(f"Error loading models: {e}")

def detectFace(net, frame, confidence_threshold=0.7):
    frameOpencvDNN = frame.copy()
    frameHeight = frameOpencvDNN.shape[0]
    frameWidth = frameOpencvDNN.shape[1]
    blob = cv2.dnn.blobFromImage(frameOpencvDNN, 1.0, (227, 227), [124.96, 115.97, 106.13], swapRB=True, crop=False)
    net.setInput(blob)
    detections = net.forward()
    faceBoxes = []
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > confidence_threshold:
            x1 = int(detections[0, 0, i, 3] * frameWidth)
            y1 = int(detections[0, 0, i, 4] * frameHeight)
            x2 = int(detections[0, 0, i, 5] * frameWidth)
            y2 = int(detections[0, 0, i, 6] * frameHeight)
            faceBoxes.append([x1, y1, x2, y2])
            cv2.rectangle(frameOpencvDNN, (x1, y1), (x2, y2), (0, 255, 0), int(round(frameHeight / 150)), 8)
    return frameOpencvDNN, faceBoxes


# Use the `faceNet` in webcam loop
video = cv2.VideoCapture(0)
padding = 20
while cv2.waitKey(1) < 0:
    hasFrame, frame = video.read()
    if not hasFrame:
        print("No frame captured from webcam!")
        break

    resultImg, faceBoxes = detectFace(faceNet, frame)

    if not faceBoxes:
        print("No face detected")

    for faceBox in faceBoxes:
        face = frame[max(0, faceBox[1] - padding):min(faceBox[3] + padding, frame.shape[0] - 1),
                     max(0, faceBox[0] - padding):min(faceBox[2] + padding, frame.shape[1] - 1)]
        blob = cv2.dnn.blobFromImage(face, 1.0, (227, 227), [124.96, 115.97, 106.13], swapRB=True, crop=False)
        genderNet.setInput(blob)
        genderPreds = genderNet.forward()
        gender = ['Male', 'Female'][genderPreds[0].argmax()]

        cv2.putText(resultImg, f'{gender}', (faceBox[0], faceBox[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA)
        cv2.imshow("Gender Detection", resultImg)

    if cv2.waitKey(33) & 0xFF == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
