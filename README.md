> **Important Note:** The code in this repository does not work anymore, since Google Arts & Culture was updated.
> You can use
> - [dezoomify](https://ophir.alwaysdata.net/dezoomify/dezoomify.html) (works online),
> - [dezoomify-rs](https://github.com/lovasoa/dezoomify-rs) (a command-line application for windows, linux and macos),
> - or [gapdecoder](https://github.com/gap-decoder/gapdecoder) (a python script) instead.

# Google Art Downloader beta
This utility allows you to save all of the images from [Google Art Project](https://artsandculture.google.com) in high quality (up to 4K). 
## Using utility
Just download [google-art-downloader.zip](https://github.com/mewforest/google-art-downloader/releases/download/v0.1.2-beta/google-art-downloader-0-1-2.zip) from [releases](https://github.com/mewforest/google-art-downloader/releases), unzip it to any folder and run **google-art-downloader.exe**. Then insert link to the text field using `CTRL+V` or button **"Paste url"** (yes, you can delete example link), click **"Download"** and wait until the image is ready.

![Screenshot of the interface](http://up.mewf.ru/ga/images/04_scr.png)
## Dependencies
Compiled release requires just connection to Internet.

Source code has written in Python 3.6 and has the following dependencies: Selenium, PIL and added chromedriver.exe to PATH.
## Problems
In old release elongated vertical images had cropped incorrectly, now you can fix it with option "Check this, if your image cropped wrongly". Unfortunately with this options quality may deteriorate. Sometimes this option causes artifacts on the image, I haven't uderstanding why.

If you'll get error on specific page, please contact me on github.
