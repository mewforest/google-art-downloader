# Google Art Downloader 

Cross-platform utility allows you to save all images from [Google Art Project](https://artsandculture.google.com) in high quality (up to 4K).

⭐ It works perfectly from 2018 year till today, thanks for stars!

## Usage
Just download archive from [releases](https://github.com/mewforest/google-art-downloader/releases) and unzip it to any
folder, after all: just run **google-art-downloader.exe**.

![2021-10-31_01h43_29](https://user-images.githubusercontent.com/15357833/139560460-020941b1-bf22-43c2-91f2-c6c1640d1b4b.png)

You can insert link to the text field using button **"Paste url"** (or `CTRL+V`) and click **"Download"** to start the image downloading.

## Requirements

Compiled release requires just connection to the Internet and Chrome installed (added in PATH).

## Running from the source

### Running with Python

> This method is also suit for you if you don't use Windows.

If you want co compile your own version or use it without downloading compiled files:

1. Install Python 3.6+ and add interpreter to PATH
2. Install Google Chrome or Chromium and add executable to PATH
3. Install all project dependencies:
   ```shell
   python -m pip install -r requirements.txt
   ```
   
### Compiling to executable 
If you need to compile it with PyInstaller (for Windows), follow this instructions:
- Change source code of installed Selenium to disable terminal showing:
  
  Open file: `<your-path-to-python>\Lib\site-packages\selenium\webdriver\common\service.py`. 
  
  and override method in `selenium.webdriver.common.service.Service`:
  ```python
  self.process = subprocess.Popen(cmd, env=self.env,
                                         close_fds=platform.system() != 'Windows',
                                         stdout=self.log_file,
                                         stderr=self.log_file,
                                         stdin=PIPE,
                                         )
  ```
  To this:
   ```python
   self.process = subprocess.Popen(cmd, env=self.env,
                                               close_fds=True,
                                               stdout=self.log_file,
                                               stderr=self.log_file,
                                               stdin=PIPE,
                                               )
   ```
- After changes above, execute commands below to compile it:
   ```shell
   python -m pip install pyinstaller --upgrade
   pyinstaller --onefile --noconsole --icon=favicon.ico .\GoogleArtDownloader.py
   ```
- Copy `bin` folder to `dist`.
- Done! Now your compiled program in `dist` folder.

## Alternatives
If you are interested in more highest image resolution or Selenium webdriver isn't starting well, you could use alternatives:
- [dezoomify](https://ophir.alwaysdata.net/dezoomify/dezoomify.html) (works online),
- [dezoomify-rs](https://github.com/lovasoa/dezoomify-rs) (a command-line application for windows, linux and macos),
- or [gapdecoder](https://github.com/gap-decoder/gapdecoder) (a python script) instead.

