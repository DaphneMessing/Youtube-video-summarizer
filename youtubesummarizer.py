import cv2
from pytube import Search
from scenedetect import VideoManager
from scenedetect import SceneManager
from scenedetect.detectors import ContentDetector
import easyocr
from PIL import Image, ImageDraw
import imageio
import os

def download_video(search_query):
    search = Search(search_query)
    for video in search.results:
        if video.length < 600:  # less than 10 minutes
            try:
                video.streams.filter(file_extension='mp4').first().download(filename='video.mp4')
                return 'video.mp4'


            except Exception as e:
                print(f"Failed to download {video.title}: {str(e)}")
    return None
def find_scenes(video_path):
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector())
    base_timecode = video_manager.get_base_timecode()

    video_manager.set_downscale_factor()
    video_manager.start()

    scene_manager.detect_scenes(frame_source=video_manager)
    scene_list = scene_manager.get_scene_list(base_timecode)
    return scene_list

def extract_frames(video_path, scene_list):
    cap = cv2.VideoCapture(video_path)
    frames = []
    for start, end in scene_list:
        cap.set(cv2.CAP_PROP_POS_MSEC, (start.get_seconds() + 0.5 * (end.get_seconds() - start.get_seconds())) * 1000)
        ret, frame = cap.read()
        if ret:
            frame_path = f"frame_{start.get_frames()}.jpg"
            cv2.imwrite(frame_path, frame)
            frames.append(frame_path)
    cap.release()
    return frames

def add_watermark_and_extract_text(frames, watermark_text):
    reader = easyocr.Reader(['en'])
    extracted_texts = []
    for frame in frames:
        img = Image.open(frame)
        draw = ImageDraw.Draw(img)
        width, height = img.size
        # Assuming a fixed size for the text as a workaround
        textwidth, textheight = (100, 20)  # Example fixed dimensions
        draw.text((width - textwidth - 10, height - textheight - 10), watermark_text, fill=(255,255,255))
        img.save(frame)

        results = reader.readtext(frame)
        extracted_text = " ".join([result[1] for result in results])
        extracted_texts.append(extracted_text)
    return extracted_texts

def create_gif(frames):
    images = [Image.open(frame) for frame in frames]
    imageio.mimsave('summary.gif', images, duration=0.2)

def main():
    subject = input("Please enter a subject for the video: ")
    video_path = download_video(subject)
    if video_path:
        scene_list = find_scenes(video_path)
        frames = extract_frames(video_path, scene_list)
        extracted_texts = add_watermark_and_extract_text(frames, "Your Name")
        create_gif(frames)
        print(" ".join(extracted_texts))
        os.system('summary.gif')  # This may vary depending on the OS

if __name__ == "__main__":
    main()