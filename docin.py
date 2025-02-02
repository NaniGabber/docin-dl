import os
import urllib.request
from PIL import Image
from pathlib import Path
import time
import sys
import re 
import textwrap
import pytesseract
import cv2


def show_progress(block_num, block_size, total_size):
    global start_time
    if block_num == 0:
        start_time = time.time()
        return
    duration = time.time() - start_time
    progress_size = int(block_num * block_size)
    speed = (progress_size / (1024* duration))
    downloaded = block_num * block_size
    if downloaded < total_size:
        print(f"\r {round(speed, 2)} KB/s | {int(downloaded/total_size * 100)} %",end = " ", flush = True);
        sys.stdout.flush()

def download_images(pid, output_dir):
    images = []
    i = 1
    while True:
        try:
            file_name = f"{i}.png"
            file_path = os.path.join(output_dir, file_name)
            url = f"http://211.147.220.164/index.jsp?file={pid}&pageno={i}"
            
            opener = urllib.request.build_opener()
            opener.addheaders = [('Connection', 'Close'), ('User-agent', 'Mozilla/5.0')]
            urllib.request.install_opener(opener)

            urllib.request.urlretrieve(url, file_path, show_progress)
            
            print(f" Page {i} downloaded.")
            images.append(file_path)
            i += 1
        except urllib.error.HTTPError:
            print("Download completed or no more pages to fetch.")
            return images

def font_recognize(img):
    url = "https://api.myfonts.net/v2/identify"
    response = requests.post(url, files=img)

    if response.status_code == 200:
        print("font:", response.json())
    else:
        print("font. Error:", response.status_code)

def text_recognize(img):
    data = pytesseract.image_to_data(img, lang="en") 
    boxes = len(data['level'])
    for i in range(boxes):
        (x, y, w, h, text) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i], data['text'][i])
        draw.text((x, y), text, fill="white", font=font_recognize(img))

def images_to_pdf(images, output_dir):
    pdf_path = os.path.join(output_dir, "document.pdf")
    image_list = [Image.open(image).convert('RGB') for image in images]
    if image_list:
        image_list[0].save(pdf_path, save_all=True, append_images=image_list[1:])
        print(f"PDF saved at {pdf_path}")


if __name__ == "__main__":
    if "--help" in sys.argv or not [param for param in sys.argv if re.match(r"^--", param)]:
        print("Usage: docin-dl --pid PID --output OUTPUT")
        exit()
    if "--default" in sys.argv:
        pid = 2064621039
        output_dir = "Downloads"
    else:
        if "--pid" in sys.argv:
            pid = sys.argv[sys.argv.index("--pid") + 1]
        else:
            print("Warning: Default PID will be used!")
            pid =  2064621039 
        if "--output" in sys.argv:
            output_dir = Path(sys.argv[sys.argv.index("--output") + 1 ]).expanduser().resolve()
        else:
            print("Warning: Default output destination will be used!")
            output_dir = "Downloads"


    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    images = download_images(pid, "Downloads")
    
    if images:
        text_recognize(images[0])
        images_to_pdf(images, output_dir)
