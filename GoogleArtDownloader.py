import os
import platform
import shutil
import time as t
import tkinter as tk
import webbrowser
from threading import Thread
from tkinter import filedialog
import selenium.common.exceptions
from PIL import Image, ImageChops
from selenium import webdriver


IMG_XPATH = ".//html/body/div[3]/div[3]/div/div/div/div[3]/div"
ZOOM_BTN_XPATH = ".//html/body/div[3]/div[3]/div/div/div[2]/div[1]/div[2]/div[1]/div"
OPEN_IMAGE_BTN_XPATH = ".//html/body/div[3]/div[3]/div/div/div[3]/div/content/span"
AUTHOR_NAME_XPATH = "/html[1]/body[1]/div[3]/div[3]/div[1]/div[1]/div[6]/section[2]/div[1]/ul[1]/li[2]/a[1]"
PICTURE_NAME_XPATH = "/html[1]/body[1]/div[3]/div[3]/div[1]/div[1]/div[6]/section[2]/div[1]/ul[1]/li[1]"
TIMEOUT_FOR_IMAGE_LOADING = 45


def is_image_loaded(counter):
    """
    Checks if image on screenshot is loaded.

    Note from the future: Yes, it checks if pixels around the center dot are not white
    - it can cause bugs if image is fully white at center. So, feel free to improve this via pull request.
    """
    im = Image.open('temp/scrapping/image' + str(counter) + '.png')
    rgb_im = im.convert('RGB')
    white = (255, 255, 255)
    return all(rgb_im.getpixel(dot) != white for dot in [(2000, 1300), (2100, 1300), (2000, 1400), (2000, 1500)])


def is_screenshot_changed(counter):
    """
    Checks if screenshot changed: if yes, image is still loading.
    """
    if counter > 0:
        prev_counter = counter - 1
        new_file = os.path.getsize('temp/scrapping/image%s.png' % str(counter))
        old_file = os.path.getsize('temp/scrapping/image%s.png' % str(prev_counter))
        os.remove('temp/scrapping/image%s.png' % str(prev_counter))
        return new_file == old_file


def trim(image):
    """
    Trims white space around the image.

    Note from the future: image could be cropped incorrectly, if it has white spaces.
    Feel free to improve this via pull request.
    """
    image = image.convert('RGB')
    bg = Image.new(image.mode, image.size, (255, 255, 255))
    diff = ImageChops.difference(image, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return image.crop(bbox)
    return image


def initialize_folders():
    """
    Initializes folder structure for caching files.
    """
    if not os.path.exists('temp'):
        os.makedirs('temp')
    else:
        shutil.rmtree('temp')
    if not os.path.exists('temp/scrapping'):
        os.makedirs('temp/scrapping')


def file_save(name, temp_img_path):
    """
    Copies downloaded image from temporary folder to the new destination.
    """
    new_img_buffer = filedialog.asksaveasfile(mode='wb', defaultextension=".png", title="Saving picture",
                                            initialfile=name,
                                            filetypes=(("PNG high resolution image", "*.png"), ("all files", "*.*")))
    if new_img_buffer is None:
        lbl.config(text='Downloading was cancelled')
        btn_run.config(state='normal')
        return
    new_img_path = new_img_buffer.name
    new_img_buffer.close()
    temp_img_path = os.path.abspath(temp_img_path)
    if platform.system() == 'Windows':
        new_img_path = new_img_path.replace('/', '\\')
    if temp_img_path != new_img_path:
        shutil.move(temp_img_path, new_img_path)
        lbl.config(text='Success! File saved as : ' + str(temp_img_path) + '!')
    else:
        lbl.config(text='Failed! Please next time don\'t replace file in script directory!')


def do_scrapping(url):
    """
    Starts webdriver, opens url and makes multiple screenshots of zoomed image.
    """
    if '?' in url:
        url = url[:url.index('?')]
    lbl.config(text='2/3: Scrapping: starting webdriver... [it takes several seconds]')
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    os_name = platform.system()
    if os_name == 'Windows':
        executable = "bin/chromedriver_win32/chromedriver.exe"
    elif os_name == 'Linux':
        executable = "bin/chromedriver_linux64/chromedriver.exe"
    elif os_name == 'Darwin':
        executable = "bin/chromedriver_mac32/chromedriver.exe"
    else:
        raise OSError(f'Operation system is not supported now: {os_name}')
    driver = webdriver.Chrome(executable_path=executable, options=options)
    driver.set_window_size(4000, 4000)
    driver.get(url)
    lbl.config(text='2/3: Scrapping: waiting for response')
    driver.implicitly_wait(1)
    lbl.config(text='2/3: Scrapping: getting information about artist and picture')
    is_image_appeared = False
    is_image_zoomed = False
    last_file = ''
    try:
        author_pic = driver.find_element_by_xpath(AUTHOR_NAME_XPATH).text
    except selenium.common.exceptions.WebDriverException:
        author_pic = ''
    try:
        name_pic = driver.find_element_by_xpath(PICTURE_NAME_XPATH).text[7:]
        if author_pic != '':
            name_pic = ' - ' + name_pic
    except (selenium.common.exceptions.WebDriverException, IndexError):
        name_pic = driver.title[0:-23]
    name_file = author_pic + name_pic
    for c in '\\/:*?"<>|':
        name_file = name_file.replace(c, '')
    lbl.config(text='2/3: Scrapping: starting ' + name_file + ' [+3 sec]')
    t.sleep(3)
    for i in range(0, TIMEOUT_FOR_IMAGE_LOADING):
        t.sleep(1)
        if is_image_appeared:
            lbl.config(text='2/3: Scrapping: %sth attempt, image appeared, zooming...' % str(i + 1) + ' [+6 sec]')
            t.sleep(3)
            if is_image_vertical_check.get() == 1:
                elem2 = driver.find_element_by_xpath(OPEN_IMAGE_BTN_XPATH)
            else:
                elem2 = driver.find_element_by_xpath(ZOOM_BTN_XPATH)
            elem3 = driver.find_element_by_xpath(IMG_XPATH)
            driver.execute_script("arguments[0].click();", elem2)
            driver.execute_script("arguments[0].click();", elem3)
            t.sleep(3)
            is_image_appeared = False
            is_image_zoomed = True
        else:
            lbl.config(text='2/3: Scrapping: %sth attempt, waiting for the image...' % str(i + 1))
        lbl.config(text='2/3: Scrapping: %sth attempt, taking screenshot' % str(i + 1))
        driver.save_screenshot('temp/scrapping/image%s.png' % str(i))
        lbl.config(text='2/3: Scrapping: %sth attempt, checking progress...' % str(i + 1))
        if is_image_loaded(i) and not is_image_zoomed:
            is_image_appeared = True
        if is_screenshot_changed(i):
            last_file = 'temp/scrapping/image%s.png' % str(i)
            break
    lbl.config(text='2/3: Scrapping: Success!')
    driver.quit()
    return last_file, name_file


def do_finally_changes(last_file, name_file):
    if last_file != '':
        shutil.move(last_file, 'temp/image_result.png')
        shutil.rmtree('temp/scrapping')
        im = Image.open('temp/image_result.png')
        im = im.crop((0, 50, 4000, 4000))
        # if is_image_vertical_check.get() == 1:
        #     pass
        # else:
        #     im = im
        im = trim(im)
        im.save(name_file + '.png')
        shutil.rmtree('temp')
        return name_file
    return 'An error occurred with processing image'


def process_image():
    """
    Processes a chose image: downloads, crops and saves.
    """
    btn_run.config(state='disabled')
    btn_paste.config(state='disabled')
    ent.config(state='disabled')
    chk.config(state='disabled')
    lbl.config(text='Working...')
    lbl.config(text='1/3: Initializing folders')
    initialize_folders()
    lbl.config(text='2/3: Scrapping picture (may take a few minutes)')
    file, name = do_scrapping(ent.get())
    lbl.config(text='3/3: Cropping image')
    status = do_finally_changes(file, name)
    lbl.config(text='Saving the file: ' + str(status) + '...')
    file_save(status + '.png', status + '.png')
    btn_paste.config(state='normal')
    ent.config(state='normal')
    btn_run.config(state='normal')
    chk.config(state='normal')


def start_download():
    """
    Starts downloading process.
    """
    lbl.config(text="Starting..")
    th = Thread(target=process_image)
    th.start()


def on_key_release(event):
    """
    Initializes folder structure for caching purposes. Also it removes last cached files.
    """
    ctrl = (event.state & 0x4) != 0
    if event.keycode == 88 and ctrl and event.keysym.lower() != "x":
        event.widget.event_generate("<<Cut>>")

    if event.keycode == 86 and ctrl and event.keysym.lower() != "v":
        event.widget.event_generate("<<Paste>>")

    if event.keycode == 67 and ctrl and event.keysym.lower() != "c":
        event.widget.event_generate("<<Copy>>")

    if event.keycode == 65 and ctrl and event.keysym.lower() != "a":
        event.widget.event_generate("<<SelectAll>>")


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Google Art Downloader 0.1.3')
    root.resizable(0, 0)

    entryText = tk.StringVar()
    ent = tk.Entry(root, width=77, textvariable=entryText)
    entryText.set(r"https://artsandculture.google.com/asset/the-starry-night/bgEuwDxel93-Pg")
    lbl = tk.Label(root, width=80)
    btn_run = tk.Button(root, text="Download", command=start_download)
    btn_paste = tk.Button(root, text="Paste url", command=lambda: entryText.set(root.clipboard_get()))
    is_image_vertical_check = tk.IntVar()
    chk = tk.Checkbutton(root, text="Is image a vertical oriented?", variable=is_image_vertical_check, anchor=tk.W)
    about = tk.Label(root, text="[github.com/mewforest/google-art-downloader]", fg='#888888')
    about.bind('<Button-1>', lambda e: webbrowser.open('https://github.com/mewforest/google-art-downloader'))

    lbl.grid(row=1, column=1, columnspan=4, pady=1)
    ent.grid(row=2, column=1, columnspan=2, padx=6, pady=1)
    btn_paste.grid(row=2, column=3, padx=3, pady=2)
    btn_run.grid(row=2, column=4, padx=3, pady=2)
    chk.grid(row=3, column=1, columnspan=1, pady=1, padx=5, sticky=tk.W)
    about.grid(row=3, column=2, columnspan=1, pady=1, padx=1, sticky=tk.W)

    lbl.configure(text='Insert here link to picture from Google Arts & Culture:')
    ent.bind("<Key>", on_key_release, "+")
    root.mainloop()
