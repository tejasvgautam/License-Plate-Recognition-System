# License Plate Recognition System in Python

![out_main (3)](https://github.com/user-attachments/assets/f25b5a82-deb4-473f-ba5e-d6f9347efbb0)


## 📦 Models Used

- **Vehicle Detection**: [`Coco_model`](https://github.com/ultralytics/yolov5) — a pre-trained COCO dataset model.
- **License Plate Detection**: YOLOv8 custom-trained model — `license_plate_detector.pt`

---

## 🌍 Regional Support

This system has dual functionality depending on the region:

| Region                 | Script Files                                   | Description                                      |
|------------------------|------------------------------------------------|--------------------------------------------------|
| 🇬🇧 **UK (British)**     | `main.py`, `util.py`                           | Detects and reads standard British license plates |
| 🇮🇳 **Himachal Pradesh** | `main_himachal_pradesh.py`, `util_himachal_pradesh.py` | Specialized for Indian plates (HP series)        |

## Required packages:
- `Ultralytics 8.3.159`
- `pandas`
- `opencv-python`
- `numpy`
- `scipy`
- `filterpy`
- `easyocr`

- ** The sort module needs to be downloaded from** [this repository](https://github.com/abewley/sort).

  ```bash
  git clone https://github.com/abewley/sort
  ```
---
### Sample Video:
> The video should be in `mp4` format

Rename your sample video with 'sample_main' or 'sample_main.mp4'. Download sample video [here](https://drive.google.com/file/d/1bxvD2SEsm50_78wKqDU-8kdhZENoI9nx/view?usp=sharing)

### Steps:
<div align="center">
For British License Plates:
</div>

- Step 1: Clone this repository.
- Step 2: Install the required dependencies.
- Step 3: Run the `main.py` file. A `test_main.csv` file will be formed.
  ``` python
  python main.py
  ```
- Step 4: Run the `add_missing_data.py` file. A `test_interpolated_main.csv` file will be formed.
  ```python
  python add_missing_data.py
  ```
- Step 5: Finally, Run the `visualize.py` file. Output Video with detection of car & license plates will be available in your directory.
  ```python
  python visualize.py
  ```

<div align="center">
For Himachal Pradesh License Plates:
</div>

- Step 1: Clone this repository.
- Step 2: Install the required dependencies.
- Step 3: In the `main_himachal_pradesh.py` file, on `line 10`  replace:

   ```jsx
   from util import get_car, read_license_plate, write_csv
   ```
   to:

   ```jsx
   from util_himachal_pradesh import get_car, read_license_plate, write_csv
   ```
   A `test_main.csv` file will be formed.
- Step 4: Run the `add_missing_data.py` file. A `test_interpolated_main.csv` file will be formed.
  ```python
  python add_missing_data.py
  ```
- Step 5: Finally, Run the `visualize.py` file. Output Video with detection of car & license plates will be available in your directory.
  ```python
  python visualize.py
  ```
