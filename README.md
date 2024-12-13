
# YouTube Video Summarizer

### Overview

🎥 [Watch Demo Video](https://drive.google.com/file/d/1Ktcn_xK149ritA6cAn718-NNYsrQHypL/view?usp=drive_link)

This project is a Python program that summarizes YouTube videos on a given subject by extracting key frames, analyzing text from those frames, and creating an animated slideshow. It demonstrates the use of multiple Python libraries for video analysis, text extraction, and image processing.

### Features

1. **YouTube Video Search and Download**:
   - Prompts the user to enter a subject (e.g., "Super Mario Movie").
   - Searches YouTube for the subject using `pytube` and downloads the top result under 10 minutes in length.

2. **Scene Detection**:
   - Uses `PySceneDetect` to detect and extract key scenes from the downloaded video.
   - Saves these key frames as images for further processing.

3. **Text Extraction with OCR**:
   - Uses `EasyOCR` to extract English text from the saved images.
   - Prints the extracted text to the console.

4. **Image Watermarking**:
   - Adds a text watermark (your full name) to the bottom-right corner of each image.

5. **Animated GIF Creation**:
   - Creates a 10-second animated GIF using the extracted frames.
   - Displays the GIF and prints a concatenated string of all the extracted text.

### Technologies Used

- **Python Libraries**:
  - `pytube`: For searching and downloading YouTube videos.
  - `PySceneDetect`: For scene detection in videos.
  - `EasyOCR`: For optical character recognition (OCR) on images.
  - `Pillow`: For image processing and adding watermarks.
  - `imageio`: For creating animated GIFs.

### Installation Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/DaphneMessing/Youtube-video-summarizer.git
   ```
2. Install the required Python libraries:
   ```bash
   pip install pytube scenedetect easyocr pillow imageio
   ```
3. Place the font file (`arial.ttf`) in the same directory as the script to enable watermarking.

### How to Run

1. Run the Python program:
   ```bash
   python youtubesummarizer.py
   ```
2. Enter a subject when prompted (e.g., "Super Mario Movie") and press Enter.
3. The program will:
   - Search for the top YouTube video on the subject.
   - Download the video if it's under 10 minutes long.
   - Detect and extract key frames from the video.
   - Extract text from the frames and add a watermark.
   - Create and display an animated GIF with the extracted frames.
   - Print all the extracted text to the console.

### File Structure

- **youtubesummarizer.py**: The main script for the program.
- **arial.ttf**: Font file used for adding watermarks.



