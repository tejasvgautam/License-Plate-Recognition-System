# * In main we are gonna write all of our code

from ultralytics import YOLO  # YOLO is an object-detection model by ultralytics
import cv2   # Computer Vision Library (for computer vision tasks) OpenCV

""" SORT = Simple Online and Realtime Tracking. Used to assign IDs to moving objects across frames — so you can track them as they move. """
from sort.sort import *   # This line imports everything (*) from the sort.py file inside the sort/ folder.
mot_tracker = Sort()      # This creates an instance of the SORT tracker. mot_tracker will now track objects frame by frame.

from util import get_car, read_license_plate, write_csv     # Calling Functions from """" util.py """"

results = {}       # A Dictionary for write_csv function

# * load models
coco_model = YOLO('yolov8n.pt')   # Pre-trained model trained on Coco Dataset
license_plate_detector = YOLO('./models/license_plate_detector.pt')     # Model trained on 40+ epochs of license plate images

# >>>>>>>>>>>>> To see how to train YOLOv8 Model with Data Annotations:- Visit: https://www.youtube.com/watch?v=m9fH9OWn8YM&t=2972s <<<<<<<<<<<<<<<<

# * load video
cap = cv2.VideoCapture('./sample_main.mp4')
vehicles = [2, 3, 5, 7]      # Vehicles' class_id in COCO Dataset (Check coco_classes_dataset.txt)

# * read frames (Read Frames out of the video:- sample.mp4)
frame_nmr = -1
ret = True
while ret:
    frame_nmr += 1    # incrementing frame number
    ret, frame = cap.read()

    """  >>>> cap.read() returns a tuple (ret, frame). ret is True if a frame was successfully read.
         >>>> frame contains the image data (i.e. the frame itself)."""
    
    if ret:  # if ret = True

        results[frame_nmr] = {}  # just declaring a dictionary with parameterized variable dw :)
        
        # * detect vehicles
        detections = coco_model(frame)[0]    # using coco model to detect vehicle from frame. [0] is first and only prediction
        detections_ = []
        for detection in detections.boxes.data.tolist():    # looping over each detected object, where detections.boxes.data is a tensor (represents multi-dimensional array) containing detection info which is converted to a list using tolist()
            """ >>>> Each detection is typically a list like: [x1, y1, x2, y2, confidence, class_id]
             >>>> (x1, y1 = top-left corner of the box)
             >>>> (x2, y2 = bottom-right corner)
             >>>> (confidence = how sure the model is (e.g., 0.87 = 87%))
             >>>> (class_id = index of the object class (like 0 = person, 2 = car, etc.)) """
            x1, y1, x2, y2, confidence, class_id = detection
            if int(class_id) in vehicles:        # if class id in vehicles variable ([2,3,5,7] only then continue)
                detections_.append([x1, y1, x2, y2, confidence])
        
        
        # * track vehicles
        if len(detections_) > 0:
            track_ids = mot_tracker.update(np.asarray(detections_))
        else:
            track_ids = np.empty((0, 5))  # no detection: empty array with 5 columns (x1, y1, x2, y2, confidence)

        # np.asarray(detections_) :- Converts list of detections into a NumPy Array
        # mot_tracker.update(...) :- 1) Takes the current frame’s detections. 2) Matches them to previously tracked objects. 3) Returns a list of tracked boxes with IDs
        """ >>>>>> SO BASICALLY each object keeps its ID (same) across frames <<<<<< """


        # * detect license plates (Using the 'license_plate_detector' model)
        license_plates = license_plate_detector(frame)[0]    # same as vehicles detection but different model
        for license_plate in license_plates.boxes.data.tolist():
            x1, y1, x2, y2, confidence, class_id = license_plate


            # * assign license plate to car
            xcar1, ycar1, xcar2, ycar2, car_id = get_car(license_plate, track_ids)    # Function from util.py returning xcar1, ycar1, xcar2, ycar2, car_id

            if car_id != -1:      # <<<<<<< WITHOUT THIS:

                """
                Without it, Code would:
                1) Try to crop, OCR, and save data for license plates not linked to any car.

                2) Result in junk output or key errors in results[frame_nmr][car_id], since -1 is not a valid object ID.
                """

                # * crop license plate
                license_plate_crop = frame[int(y1):int(y2), int(x1):int(x2), :]     # *Not a dictionary* (Rows(height)(y-axis), Columns(width)(x-axis))

                # * process license plate
                license_plate_crop_gray = cv2.cvtColor(license_plate_crop, cv2.COLOR_BGR2GRAY)

                """
                Grayscale image has a pixel between 0 & 255, we need to convert into binary (black & white pixel only) so... 
                ...it's easier for EasyOCR to detect text on number plate """

                _, license_plate_crop_thresh = cv2.threshold(license_plate_crop_gray, 64, 255, cv2.THRESH_BINARY_INV)

                """
                i.e. cv2.threshold(src, thresh, maxval, type)
                where, 
                src: The input grayscale image (license_plate_crop_gray)
                thresh: Threshold value (64)
                maxval: Maximum pixel value to use (255)
                type: Type of thresholding (cv2.THRESH_BINARY_INV)
                
                So,
                For each pixel in the grayscale image:

                If pixel value > 64 → set it to 0 (black)
                Else → set it to 255 (white)"""

                # * read license plate number
                license_plate_text, license_plate_text_score = read_license_plate(license_plate_crop_thresh)   # Function from util.py returning license_plate_text, license_plate_text_score
                
                if license_plate_text is not None:
                    results[frame_nmr][car_id] = {'car': {'bbox': [xcar1, ycar1, xcar2, ycar2]},       # frame_nmr is outer key ('car','license_plate_text') & car_id is inner key ('bbox','text','bbox_score')
                                                'license_plate': {'bbox': [x1, y1, x2, y2],
                                                                        'text': license_plate_text,
                                                                        'bbox_score': confidence,
                                                                        'text_score': license_plate_text_score}}
                
    
# * write results
write_csv(results, './test_main.csv')   # write_csv requires a dictionary & path in the function