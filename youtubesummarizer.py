import cv2
from pytube import Search
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector
import easyocr
from PIL import Image, ImageDraw
import imageio
import os

def download_video(search_query):
    search = Search(search_query)
    max_results = 10  # Limit to top 10 results
    count = 0

    for video in search.results:
        if count >= max_results:
            break  # Stop processing after the top 10 results
        if video.length < 600:  # less than 10 minutes
            try:
                video_to_download = video.streams.filter(progressive=True, file_extension='mp4').first()
                if video_to_download:
                    video_to_download.download(filename='video.mp4')
                    return 'video.mp4'
            except Exception as e:
                print(f"Failed to download {video.title}: {str(e)}")
        count += 1

    return None

def find_scenes(video_path):
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector())
    video_manager.set_downscale_factor()
    video_manager.start()

    scene_manager.detect_scenes(frame_source=video_manager)
    scene_list = scene_manager.get_scene_list(video_manager.get_base_timecode())
    video_manager.release()
    return scene_list

def extract_frames(video_path, scene_list):
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
    reader = easyocr.Reader(['en'])
    for frame in frames:
        img = Image.open(frame)
        results = reader.readtext(frame)
        extracted_text = " ".join([result[1] for result in results])
        print(f"Text found in {frame}: {extracted_text}")  # Print detected text to console
        
        draw = ImageDraw.Draw(img)
        width, height = img.size
        draw.text((width - 110, height - 30), watermark_text, fill=(255,255,255))  # Add watermark
        img.save(frame)

def create_gif(frames):
    images = [Image.open(frame) for frame in frames]
    imageio.mimsave('summary.gif', images, duration=0.2)

def main():
    subject = input("Please enter a subject for the video: ")
    video_path = download_video(subject)
    if video_path:
        scene_list = find_scenes(video_path)
        frames = extract_frames(video_path, scene_list)
        add_watermark_and_extract_text(frames, "Dapne Messing")
        create_gif(frames)
        os.system('summary.gif')  # To open the GIF; this might need adjustment based on the OS

if __name__ == "__main__":
    main()