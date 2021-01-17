import cv2
import time
import math


# Selecting the different objects for the program to track (If any)
def objectSelection(tracker, frame):
    # 'T' was pressed in the main function
    key = ord('t')
    cv2.putText(frame, 'Select an object to track and confirm with \'Space\' key.',
                (10, 20), cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 255, 255), 2)

    # Tracker will be initialized according to provided ROI
    boundingBox = cv2.selectROI('MOT Project', frame, False, False)
    tracker.init(frame, boundingBox)


# Outlining the contours of the objects
def calcContours(objectTracking, originalFrame1, originalFrame2, boundingBox = None):
    # Calculating frame difference to isolate the objects in motion
    if objectTracking:
        # To eliminate the tracked object from appearing a second time as a contour
        noObject1 = originalFrame1.copy()
        noObject2 = originalFrame2.copy()
        noObject1[int(boundingBox[1]):int(boundingBox[1] + boundingBox[3]), int(boundingBox[0]):int(boundingBox[0] + boundingBox[2]), :] = 0
        noObject2[int(boundingBox[1]):int(boundingBox[1] + boundingBox[3]), int(boundingBox[0]):int(boundingBox[0] + boundingBox[2]), :] = 0
        frameDifference = cv2.absdiff(noObject1, noObject2)
    else:
        frameDifference = cv2.absdiff(originalFrame1, originalFrame2)

    # Converting the image to gray scale to prep for blurring
    grayScale = cv2.cvtColor(frameDifference, cv2.COLOR_BGR2GRAY)

    # Blurring the image with Gaussian Filter to reduce noise and isolate contours more effectively
    blurredImg = cv2.GaussianBlur(grayScale, (5, 5), 0)

    # Applying Threshold to the image to brighten the contours
    _, thresholdImg = cv2.threshold(blurredImg, 20, 255, cv2.THRESH_BINARY)

    # Dilating the image to smooth imprefections in contours and merge smaller contours to bigger ones
    dilatedImg = cv2.dilate(thresholdImg, None, iterations=3)

    # Functions differs in newer OpenCV versions
    # Getting contours from the image
    (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
    if int(major_ver) < 4 and int(minor_ver) < 3:
        _, newContours, _ = cv2.findContours(dilatedImg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    else:
        newContours, _ = cv2.findContours(dilatedImg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return newContours

cv2.cvtColor
# Making a list of contour bounding rectangles
def calcBoudningRectangles(contours):
    rectangles = list()
    for contour in contours:
        # Ignoring small contours
        if cv2.contourArea(contour) < 1000:
            continue

        # Bounding the contour with a rectangle and adding it to the rectangle list
        rectangle = cv2.boundingRect(contour)
        rectangles.append(rectangle)
    return rectangles


# Drawing bounding rectangles on the frame
def drawBoundingRectangles(objectTracking, rectangles, frame, objectRectangle=None, cameraDistance = None):
    # Each frame starts with 0 violations
    violations = 0

    # In Object Tracking Mode: Calculating each detected person's proximity to target
    # All Motion Tracking Mode: Calculating proximity of each person to another
    for rectangle1 in rectangles:
        if not objectTracking:
            for rectangle2 in rectangles:
                # Calculating center of bounding rectangles
                p1 = (int(rectangle1[0] + rectangle1[2] / 2), int(rectangle1[1] + rectangle1[3] / 2))
                p2 = (int(rectangle2[0] + rectangle2[2] / 2), int(rectangle2[1] + rectangle2[3] / 2))

                # Distance between the two center points acts as proximity value
                distance = math.sqrt(((p1[0] - p2[0]) ** 2) + ((p1[1] - p2[1]) ** 2))

                # Acceptable proximity is marked as a green rectangle
                # Very small distances are most likely multiple contours of the same object so they are ignored
                if distance > 400/cameraDistance or distance < 10:
                    cv2.rectangle(frame, (rectangle1[0], rectangle1[1]),
                                  (rectangle1[0] + rectangle1[2], rectangle1[1] + rectangle1[3]), (0, 255, 0), 2)
                # Close proximity is marked as a violation,
                # Center points are marked and line is drawn between them, bounding rectangle is red
                else:
                    violations += 1
                    cv2.circle(frame, p1, 3, (0, 0, 255), 2, 1)
                    cv2.circle(frame, p2, 3, (0, 0, 255), 2, 1)
                    cv2.line(frame, p1, p2, (0, 0, 255), thickness=3, lineType=8)
                    cv2.rectangle(frame, (rectangle1[0], rectangle1[1]),
                                  (rectangle1[0] + rectangle1[2], rectangle1[1] + rectangle1[3]), (0, 0, 255), 2)
                    cv2.rectangle(frame, (rectangle2[0], rectangle2[1]),
                                  (rectangle2[0] + rectangle2[2], rectangle2[1] + rectangle2[3]), (0, 0, 255), 2)
        elif objectTracking:
            p1 = (int(rectangle1[0] + rectangle1[2] / 2), int(rectangle1[1] + rectangle1[3] / 2))
            p2 = (int(objectRectangle[0] + objectRectangle[2] / 2), int(objectRectangle[1] + objectRectangle[3] / 2))
            distance = math.sqrt(((p1[0] - p2[0]) ** 2) + ((p1[1] - p2[1]) ** 2))

            if distance > 400/cameraDistance or distance < 10:
                cv2.rectangle(frame, (rectangle1[0], rectangle1[1]),
                              (rectangle1[0] + rectangle1[2], rectangle1[1] + rectangle1[3]), (0, 255, 0), 2)
                cv2.rectangle(frame, (int(objectRectangle[0]), int(objectRectangle[1])),
                              (int(objectRectangle[0] + objectRectangle[2]),
                               int(objectRectangle[1] + objectRectangle[3])), (255, 0, 0), 2)
            else:
                violations += 1
                cv2.circle(frame, p1, 3, (0, 0, 255), 2, 1)
                cv2.circle(frame, p2, 3, (0, 0, 255), 2, 1)
                cv2.line(frame, p1, p2, (0, 0, 255), thickness=3, lineType=8)
                cv2.rectangle(frame, (rectangle1[0], rectangle1[1]),
                              (rectangle1[0] + rectangle1[2], rectangle1[1] + rectangle1[3]), (0, 0, 255), 2)
                cv2.rectangle(frame, (int(objectRectangle[0]), int(objectRectangle[1])),
                              (int(objectRectangle[0] + objectRectangle[2]),
                               int(objectRectangle[1] + objectRectangle[3])), (0, 0, 255), 2)
    return violations
