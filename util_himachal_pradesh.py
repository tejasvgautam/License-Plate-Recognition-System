# all the functions used in main are gonna be written here

#####################           FUNCTIONS THAT WE USE FROM GITHUB REPO           #######################

import string
import easyocr    #(((( EasyOCR is a Python library that can read text from images ))))

# Initialize the OCR reader
reader = easyocr.Reader(['en'], gpu=False)

# Mapping dictionaries for character conversion
dict_char_to_int = {'O': '0',
                    'I': '1',
                    'J': '3',
                    'A': '4',
                    'G': '6',
                    'S': '5'}

dict_int_to_char = {'0': 'O',
                    '1': 'I',
                    '3': 'J',
                    '4': 'A',
                    '6': 'G',
                    '5': 'S'}



def write_csv(results, output_path):
    """
    Write the results to a CSV file.  (Something like an excel file)

    Args:
        results (dict): Dictionary containing the results.
        output_path (str): Path to the output CSV file.
    """
    with open(output_path, 'w') as f:
        f.write('{},{},{},{},{},{},{}\n'.format('frame_nmr', 'car_id', 'car_bbox',
                                                'license_plate_bbox', 'license_plate_bbox_score', 'license_number',
                                                'license_number_score'))

        for frame_nmr in results.keys():
            for car_id in results[frame_nmr].keys():
                print(results[frame_nmr][car_id])
                if 'car' in results[frame_nmr][car_id].keys() and \
                   'license_plate' in results[frame_nmr][car_id].keys() and \
                   'text' in results[frame_nmr][car_id]['license_plate'].keys():
                    f.write('{},{},{},{},{},{},{}\n'.format(frame_nmr,
                                                            car_id,
                                                            '[{} {} {} {}]'.format(
                                                                results[frame_nmr][car_id]['car']['bbox'][0],
                                                                results[frame_nmr][car_id]['car']['bbox'][1],
                                                                results[frame_nmr][car_id]['car']['bbox'][2],
                                                                results[frame_nmr][car_id]['car']['bbox'][3]),
                                                            '[{} {} {} {}]'.format(
                                                                results[frame_nmr][car_id]['license_plate']['bbox'][0],
                                                                results[frame_nmr][car_id]['license_plate']['bbox'][1],
                                                                results[frame_nmr][car_id]['license_plate']['bbox'][2],
                                                                results[frame_nmr][car_id]['license_plate']['bbox'][3]),
                                                            results[frame_nmr][car_id]['license_plate']['bbox_score'],
                                                            results[frame_nmr][car_id]['license_plate']['text'],
                                                            results[frame_nmr][car_id]['license_plate']['text_score'])
                            )
        f.close()



def license_complies_format(text):     # Jis Country ki license plate ka jaisa format hai. Eg:- HP 39E 4444 = (2 Letter, 2 Num, 1 Letter, 4 Num)
    """
    Check if the license plate text complies with the required format.   <<<< This Format is for Himachal Pradesh Cars
    
    Args:
        text (str): License plate text.

    Returns:
        bool: True if the license plate complies with the format, False otherwise.
    """
    if len(text) != 9:
        return False

    if (text[0] in string.ascii_uppercase or text[0] in dict_int_to_char.keys()) and \
       (text[1] in string.ascii_uppercase or text[1] in dict_int_to_char.keys()) and \
       (text[2] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[2] in dict_char_to_int.keys()) and \
       (text[3] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[3] in dict_char_to_int.keys()) and \
       (text[4] in string.ascii_uppercase or text[4] in dict_int_to_char.keys()) and \
       (text[5] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[5] in dict_char_to_int.keys()) and \
       (text[6] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[6] in dict_char_to_int.keys()) and \
       (text[7] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[7] in dict_char_to_int.keys()) and \
       (text[8] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[8] in dict_char_to_int.keys()):
        return True
    else:
        return False


def format_license(text):      # Sometimes EasyOCR might get confused between Number 5 and Letter S, So this function solves that problem
    # It does that by: Let's say We have JK 51S 4444, we know 51 is going to be a number from 'license_complies_format' function.
    # So, if by chance it detects 51's 5 as S, it automatically converts it to 5, because we know 51 can't have a letter
    """
    Format the license plate text by converting characters using the mapping dictionaries.

    Args:
        text (str): License plate text.

    Returns:
        str: Formatted license plate text.
    """
    license_plate_ = ''
    mapping = {
        0: dict_int_to_char,   # First letter
        1: dict_int_to_char,   # Second letter
        2: dict_char_to_int,   # First digit
        3: dict_char_to_int,   # Second digit
        4: dict_int_to_char,   # Series letter
        5: dict_char_to_int,   # First digit of number
        6: dict_char_to_int,   # Second digit
        7: dict_char_to_int,   # Third digit
        8: dict_char_to_int    # Fourth digit
    }

    for j in range(len(text)):
        if j in mapping.keys() and text[j] in mapping[j].keys():
            license_plate_ += mapping[j][text[j]]
        else:
            license_plate_ += text[j]

    return license_plate_



######################          FUNCTIONS THAT WE WRITE             #############################

def get_car(license_plate, vehicle_track_ids):
    
    """
    Retrieve the vehicle coordinates and ID based on the license plate coordinates.

    Args:
        license_plate (tuple): Tuple containing the coordinates of the license plate (x1, y1, x2, y2, score, class_id).
        vehicle_track_ids (list): List of vehicle track IDs and their corresponding coordinates.

    Returns:
        tuple: Tuple containing the vehicle coordinates (x1, y1, x2, y2) and ID.
    """

    x1, y1, x2, y2, confidence, class_id = license_plate

    foundIT = False
    for j in range(len(vehicle_track_ids)):       # for every detected vehicle in video we are going to check if it contains a license plate
        xcar1, ycar1, xcar2, ycar2, car_id = vehicle_track_ids[j]

        if x1 > xcar1 and y1 > ycar1 and x2 < xcar2 and y2 < ycar2:    # checking if upper left and bottom right corner of license plate bounding box is greater than and lesser than bounding box of vehicle respectively
            car_indx = j
            foundIT = True
            break
    if foundIT:
        return vehicle_track_ids[car_indx]   # If License Plate found in vehicle, so only then return bounding box of car
    
    return -1, -1, -1, -1 ,-1

def read_license_plate(license_plate_crop):
    """
    Read the license plate text from the given cropped image.

    Args:
        license_plate_crop (PIL.Image.Image): Cropped image containing the license plate.

    Returns:
        tuple: Tuple containing the formatted license plate text and its confidence score.
    """

    detections = reader.readtext(license_plate_crop)    # Read text in license_plate_crop

    for detection in detections:
        bbox, text, confidence = detection

        text = text.upper().replace(' ', '')     # Removes whitespaces from text

        if license_complies_format(text):    # If the new text is compiled to the required format of license plate, then return corrected license text using 'format_license'
            return format_license(text), confidence #(/score)
    return None, None