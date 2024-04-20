import cv2
from pytube import Search, YouTube
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector
from pytube.exceptions import AgeRestrictedError
import easyocr
from PIL import Image, ImageDraw
import imageio
import os
import subprocess
import platform
import numpy as np


def download_video(search_query):
    search = Search(search_query)
    max_results = 10
    count = 0

    for video in search.results:
        if count >= max_results:
            break
        try:
            yt = YouTube(video.watch_url)
            if yt.length < 600 and "live" not in yt.title.lower():
                video_to_download = yt.streams.filter(progressive=True, file_extension='mp4').first()
                if video_to_download:
                    video_to_download.download(filename='video.mp4')
                    return 'video.mp4'
        except AgeRestrictedError:
            print(f"Skipping age-restricted video: {yt.title}")
        except Exception as e:
            print(f"Failed to download {yt.title}: {e}")
        count += 1
    return None

def find_scenes(video_path):
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    
    # Set up the content detector with a threshold value.
    detector = ContentDetector(threshold=30)
    scene_manager.add_detector(detector)

    video_manager.set_downscale_factor()
    video_manager.start()

    try:
        scene_manager.detect_scenes(frame_source=video_manager)
        scene_list = scene_manager.get_scene_list(video_manager.get_base_timecode())
    finally:
        video_manager.release()

    if not scene_list:
        print("No scenes detected.")
    return scene_list

def extract_frames(video_path, scene_list):
    if not scene_list:
        return []  # If no scenes are detected, return an empty list.

    cap = cv2.VideoCapture(video_path)
    frames = []
    for start, end in scene_list:
        midpoint = (start.get_seconds() + end.get_seconds()) / 2
        cap.set(cv2.CAP_PROP_POS_MSEC, midpoint * 1000)
        ret, frame = cap.read()
        if ret:
            frame_path = f"frame_{start.get_frames()}.jpg"
            cv2.imwrite(frame_path, frame)
            frames.append(frame_path)
    cap.release()
    return frames

def add_watermark_and_extract_text(frames, watermark_text):
    reader = easyocr.Reader(['en'])  # Ensure the 'en' model is available.
    all_texts = []
    for frame in frames:
        img = Image.open(frame)
        results = reader.readtext(frame)
        extracted_text = " ".join([result[1] for result in results])
        # Normalize spaces within the extracted text.
        extracted_text = ' '.join(extracted_text.split())
        if extracted_text:
            print(f"Text found in {frame}: {extracted_text}")  # Print text found in the current frame.
            all_texts.append(extracted_text)  # Store the extracted text for later concatenation.
        else:
             all_texts.append("")  # Append an empty string if no text was found.
        draw = ImageDraw.Draw(img)
        width, height = img.size
        draw.text((width - 110, height - 30), watermark_text, fill=(255, 255, 255))
        img.save(frame)
    return all_texts


def create_gif(frames):
    if not frames:  # Check if there are any frames
        print("No frames available to create a GIF.")
        return

    max_duration = 10  # The GIF should last no more than 10 seconds.
    max_frame_duration = 1  # Maximum duration each frame can be displayed.
    min_frame_duration = 0.1  # Minimum duration each frame can be displayed.

    number_of_frames = len(frames)
    duration_per_frame = max_duration / number_of_frames

    if duration_per_frame < min_frame_duration:
        # Compute histograms and differences only if needed
        histograms = []
        differences = []
        for frame in frames:
            img = Image.open(frame).convert('RGB')
            hist = np.histogram(img, bins=256)[0]
            histograms.append(hist)
            if len(histograms) > 1:
                # Calculate histogram difference
                diff = np.sum(np.abs(histograms[-1] - histograms[-2]))
                differences.append(diff)

        # Sort frames based on the amount of change they represent
        if differences:
            sorted_indices = np.argsort(differences)[::-1]  # Indices of frames sorted by largest change
            selected_indices = sorted_indices[:int(max_duration / min_frame_duration)]  # Adjust number based on min duration
            selected_frames = [frames[i] for i in sorted(selected_indices)]  # Select frames
        else:
            selected_frames = frames[:int(max_duration / max_frame_duration)]  # Fallback to a simpler selection
        duration_per_frame = min_frame_duration
    else:
        selected_frames = frames  # Use all frames if duration per frame is acceptable

    images = [Image.open(frame) for frame in selected_frames]
    imageio.mimsave('summary.gif', images, duration=duration_per_frame)

    print(f"GIF created with {len(selected_frames)} frames, each displayed for {duration_per_frame:.2f} seconds, total duration approximately {len(selected_frames) * duration_per_frame:.2f} seconds.")


def open_gif(gif_path):
    if os.path.exists(gif_path):
        if platform.system() == 'Windows':
            os.startfile(gif_path)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.call(['open', gif_path])
        elif platform.system() == 'Linux':
            subprocess.call(['xdg-open', gif_path])
    else:
        print(f"File not found: {gif_path}")

def main():
    subject = input("Please enter a subject for the video: ")
    video_path = download_video(subject)
    if video_path:
        scene_list = find_scenes(video_path)
        frames = extract_frames(video_path, scene_list)
        if frames:
            extracted_texts = add_watermark_and_extract_text(frames, "Daphne Messing")
            full_text = " ".join([text.strip() for text in extracted_texts if text])  # Concatenate text, avoiding empty entries.
            print("Combined Text from All Frames:", full_text)  # Print the concatenated text from all frames.

            create_gif(frames)
            open_gif('summary.gif')
        else:
            print("No frames were extracted. Cannot proceed with GIF creation.")
    else:
        print("Video download failed or no suitable video found.")

if __name__ == "__main__":
    main()