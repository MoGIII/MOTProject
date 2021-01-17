import MOT_Functions as Funcs

# Initializing tracker based on OpenCV version
# For newer versions CSRT tracker is used
# For older versions MIL tracker is used
(major_ver, minor_ver, subminor_ver) = Funcs.cv2.__version__.split('.')
print(Funcs.cv2.__version__)
if int(major_ver) < 4 and int(minor_ver) < 3:
    tracker = Funcs.cv2.Tracker_create('MIL')
else:
    tracker = Funcs.cv2.TrackerCSRT_create()


# Initializing state booleans and other variables
tracking = False
allMovement = False
relativeToObjects = False
socialDistanceViolations = 0
cameraDistance = 0

# Opening Video
video = Funcs.cv2.VideoCapture("videos/Pedestrians.mp4")

# Reading the first two frames of the video
_, frame1 = video.read()
# flag, frame2 = video.read()
flag, frame2 = video.read()

# Video loop
while 1:
    if not flag:
        break

    # Press T to start tracking
    if Funcs.cv2.waitKey(1) == ord('t') and not tracking:
        # Initiating camera distance
        copy = frame1.copy()
        Funcs.cv2.putText(copy, 'Please enter distance from camera to closest object ', (10, 20),
                          Funcs.cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        Funcs.cv2.putText(copy, 'Click any button to initiate dialog in console... ', (10, 40),
                          Funcs.cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        Funcs.cv2.imshow('MOT Project', copy)
        Funcs.cv2.waitKey()
        print('Before starting the program we must gauge the distance from camera to the closest object')
        cameraDistance = int(input('Enter the distance here (in meters): '))
        print('You may go back to the program window and choose the tracking mode')

        # Choosing program mode
        copy = frame1.copy()
        Funcs.cv2.putText(copy, 'Press \'O\' to track movement relative to an object ', (10, 20),
                          Funcs.cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        Funcs.cv2.putText(copy, 'Press \'A\' to track all movement ', (10, 40),
                          Funcs.cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        Funcs.cv2.imshow('MOT Project', copy)

        key = Funcs.cv2.waitKey()

        if key == ord('o'):
            tracking = True
            relativeToObjects = True
            Funcs.objectSelection(tracker, frame1)
        elif key == ord('a'):
            tracking = True
            allMovement = True
            Funcs.cv2.putText(frame1, 'Tracking all movement... ', (10, 20),
                              Funcs.cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    if tracking:
        if relativeToObjects and tracker:
            ok, boundingBox = tracker.update(frame1)
            contours = Funcs.calcContours(relativeToObjects, frame1, frame2, boundingBox)
            boundingRectangles = Funcs.calcBoudningRectangles(contours)
            # Tracking success
            if ok:
                violations = Funcs.drawBoundingRectangles(True, boundingRectangles, frame1, objectRectangle=boundingBox,
                                                          cameraDistance=cameraDistance)
                if violations > socialDistanceViolations:
                    socialDistanceViolations = violations
                # Drawing a dot in the middle of object tracker box
                pCenter = (int(boundingBox[0] + boundingBox[2] / 2), int(boundingBox[1] + boundingBox[3] / 2))
                Funcs.cv2.circle(frame1, pCenter, 3, (0, 0, 255), 2, 1)

                # Writing object name and ID on the object
                Funcs.cv2.putText(frame1, 'Target ', (int(boundingBox[0]), int(boundingBox[1]) - 10),
                                  Funcs.cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        elif allMovement:
            contours = Funcs.calcContours(False, frame1, frame2)
            boundingRectangles = Funcs.calcBoudningRectangles(contours)
            violations = Funcs.drawBoundingRectangles(False, boundingRectangles, frame1, cameraDistance=cameraDistance)
            if violations > socialDistanceViolations:
                socialDistanceViolations = violations

    # Showing user current program state and environment/target info in the top left of the frame
    if not tracking:
        Funcs.cv2.putText(frame1, 'Press \'T\' to start tracking ', (10, 20),
                          Funcs.cv2.FONT_HERSHEY_SIMPLEX, 0.6, (36, 255, 12), 2)
    elif relativeToObjects:
        Funcs.cv2.putText(frame1, 'Tracking Object...',
                          (10, 20), Funcs.cv2.FONT_HERSHEY_SIMPLEX, 0.6, (50, 20, 255), 2)
        if socialDistanceViolations < 2:
            Funcs.cv2.putText(frame1, 'Target is Safe',
                              (10, 40), Funcs.cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        elif 2 <= socialDistanceViolations < 4:
            Funcs.cv2.putText(frame1, 'Target is Unsafe',
                              (10, 40), Funcs.cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        else:
            Funcs.cv2.putText(frame1, 'Target is in Danger',
                              (10, 40), Funcs.cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    elif allMovement:
        Funcs.cv2.putText(frame1, 'Tracking all movement..',
                          (10, 20), Funcs.cv2.FONT_HERSHEY_SIMPLEX, 0.6, (50, 20, 255), 2)
        if socialDistanceViolations < 10:
            Funcs.cv2.putText(frame1, 'Environment is Safe',
                              (10, 40), Funcs.cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        elif 10 <= socialDistanceViolations < 45:
            Funcs.cv2.putText(frame1, 'Environment is Unsafe',
                              (10, 40), Funcs.cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        elif socialDistanceViolations >= 45:
            Funcs.cv2.putText(frame1, 'Environment is Dangerous',
                              (10, 40), Funcs.cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    # Exit if Esc key is pressed
    if Funcs.cv2.waitKey(1) == 27:
        break

    # Capping frame rate unless tracking algorithm is invoked
    # In which case there is no point because the frame rate is hit already
    if not relativeToObjects:
        Funcs.time.sleep(1. / 25)

    Funcs.cv2.imshow('MOT Project', frame1)
    frame1 = frame2
    flag, frame2 = video.read()

# Thanks!
print('\nThank you for using our program!')
video.release()
Funcs.cv2.destroyAllWindows()
