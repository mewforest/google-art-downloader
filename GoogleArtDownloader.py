from selenium import webdriver
import os, shutil
import time as t
from PIL import Image, ImageChops
import tkinter as tk
from tkinter import ttk
from threading import Thread
from tkinter import filedialog


def is_picture(counter):
    im = Image.open('temp/scrapping/image' + str(counter) + '.png')
    rgb_im = im.convert('RGB')
    r, g, b = rgb_im.getpixel((2000, 3000))
    if r == 255 and g == 255 and b == 255:
        return False
    else:
        return True


def is_same(counter):
    if counter > 0:
        prev_counter = counter - 1
        new_file = os.path.getsize('temp/scrapping/image%s.png' % str(counter))
        old_file = os.path.getsize('temp/scrapping/image%s.png' % str(prev_counter))
        os.remove('temp/scrapping/image%s.png' % str(prev_counter))
        if new_file == old_file:
            return True
        else:
            return False


def trim(image):
    bg = Image.new(image.mode, image.size, image.getpixel((0, 0)))
    diff = ImageChops.difference(image, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return image.crop(bbox)


def remove(value, deletechars):
    for c in deletechars:
        value = value.replace(c, '')
    return value


def initialize_folders():
    if not os.path.exists('temp'):
        os.makedirs('temp')
    else:
        shutil.rmtree('temp')
    if not os.path.exists('temp/scrapping'):
        os.makedirs('temp/scrapping')


def file_save(name, status):
    path = status
    f = filedialog.asksaveasfile(mode='wb', defaultextension=".png", title="Saving picture", initialfile=name, filetypes=(("PNG high resolution image", "*.png"), ("all files", "*.*")))
    if f is None:
        lbl.config(text='Downloading was cancelled')
        btn.config(state='normal')
        return
    im = Image.open(path)
    im.save(f)
    os.remove(path)
    f.close()
    lbl.config(text='Success! File saved as : ' + str(status) + '!')
    btn.config(state='normal')


def do_scrapping(url):
    old_url = url
    url = ''

    for char in old_url:
        if char == '?':
            break
        url += char

    lbl.config(text='2/3: Scrapping: starting webdriver...')
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(executable_path=r"chromedriver.exe", chrome_options=options)
    driver.set_window_size(4000, 4000)
    driver.get(url)
    xPath3 = r".//html/body/div[3]/div[3]/div/div/div/div[3]/div"  # img xPath
    xPath2 = r".//html/body/div[3]/div[3]/div/div/div[2]/div[1]/div[2]/div[1]/div"  # zoom xPath
    imageAppeared = True  # flag for starting click on image
    last_file = ''  # last succeed file
    lbl.config(text='2/3: Scrapping: waiting for response')
    driver.implicitly_wait(1)
    lbl.config(text='2/3: Scrapping: getting information about artist and picture')

    try:
        authorPic = driver.find_element_by_xpath(r'/html[1]/body[1]/div[3]/div[3]/div[1]/div[1]/div[6]/section[2]/div[1]/ul[1]/li[2]/a[1]').text  # author of the picture xPath
    except Exception:
        authorPic = ''

    try:
        name_pic = driver.find_element_by_xpath(r'/html[1]/body[1]/div[3]/div[3]/div[1]/div[1]/div[6]/section[2]/div[1]/ul[1]/li[1]').text[7::]  # name of the picture xPath
        if authorPic != '':
            name_pic = ' - ' + name_pic
    except Exception:
        name_pic = driver.title[0:-23]

    name_file = authorPic + name_pic
    name_file = remove(name_file, '\/:*?"<>|')
    lbl.config(text='2/3: Scrapping: starting ' + name_file)
    for i in range(0, 59):  # 60 attempts

        if imageAppeared:
            t.sleep(3)
            lbl.config(text='2/3: Scrapping: %s/60 it looks like the image appeared, zooming...' % str(i+1))
            elem2 = driver.find_element_by_xpath(xPath2)
            elem3 = driver.find_element_by_xpath(xPath3)
            driver.execute_script("arguments[0].click();", elem2)
            driver.execute_script("arguments[0].click();", elem3)
            t.sleep(3)
            imageAppeared = False
        else:
            lbl.config(text='2/3: Scrapping: %s/60 waiting for the image...' % str(i+1))
        lbl.config(text='2/3: Scrapping: %s/60 taking snapshot' % str(i+1))
        driver.save_screenshot('temp/scrapping/image%s.png' % str(i))
        lbl.config(text='2/3: Scrapping: %s/60 checking downloading progress...' % str(i+1))

        if is_picture(i):
            imageAppeared = False

        if is_same(i):
            last_file = 'temp/scrapping/image%s.png' % str(i)
            break
    lbl.config(text='2/3: Scrapping: Success!')
    driver.quit()
    return last_file, name_file


def do_finally_changes(last_file, name_file):
    if last_file != '':
        shutil.copyfile(last_file, 'temp/image_result.png')
        shutil.rmtree('temp/scrapping')
        im = Image.open('temp/image_result.png')
        im = trim(im)
        im.save(name_file + '.png')
        shutil.rmtree('temp')
        return name_file
    return 'An error occurred with processing image'


def start_process():
    btn.config(state='disabled')
    lbl.config(text='Working...')
    lbl.config(text='1/3: Initializing folders')
    initialize_folders()
    lbl.config(text='2/3: Scrapping picture (may take a few minutes)')
    file, name = do_scrapping(ent.get())
    lbl.config(text='3/3: Cropping image')
    status = do_finally_changes(file, name)
    lbl.config(text='Saving the file: ' + str(status) + '...')
    file_save(status + '.png', status + '.png')


def start():
    lbl.config(text="Starting..")
    th = Thread(target=start_process)
    th.start()


def on_key_release(event):
    ctrl = (event.state & 0x4) != 0
    if event.keycode == 88 and ctrl and event.keysym.lower() != "x":
        event.widget.event_generate("<<Cut>>")

    if event.keycode == 86 and ctrl and event.keysym.lower() != "v":
        event.widget.event_generate("<<Paste>>")

    if event.keycode == 67 and ctrl and event.keysym.lower() != "c":
        event.widget.event_generate("<<Copy>>")

    if event.keycode == 65 and ctrl and event.keysym.lower() != "a":
        event.widget.event_generate("<<SelectAll>>")


root = tk.Tk()
root.title('Google Art Downloader 0.1 beta')

entryText = tk.StringVar()
ent = tk.Entry(root, width=77, textvariable=entryText)
entryText.set(r"https://www.google.com/culturalinstitute/beta/asset/sunflowers/NgEmkPlWfmO9aQ")
lbl = tk.Label(root, width=80)
btn = tk.Button(root, text="Download", command=start)

lbl.grid(row=1, column=1, columnspan=2)
ent.grid(row=2, column=1)
btn.grid(row=2, column=2)

lbl.configure(text='Insert here link to picture from Google Arts & Culture:')
ent.bind("<Key>", on_key_release, "+")
root.mainloop()
