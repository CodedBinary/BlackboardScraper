# BlackboardScraper
Scrapes a blackboard course for structure and materials.

Blackboard's format, or your lecturers organisation, can sometimes be terrible. Sometimes all of the learning resources are directly under the main folder. Sometimes you need to go down 6 levels of folders to access resources. Sometimes you want to study a lot without internet. Sometimes you want to study without downloading a million files yourself. Sometimes you accidentally miss a months worth of lectures and learning resources. Enter BlackboardScraper - the tool to automate the process of downloading and (soon) naming your learning resources. 

Note: Please use this responsibly and respectfully. Run it off peak, don't try and remove sleep statements, and don't distribute material you aren't meant to. This is designed for individuals to create copies of blackboard pages for their own convenience. Lecturers put effort into their learning materials, and it is usually property of the university - not you. The university knows what and when you download things. Abuse this at your own risk.

Please open a bug report if this breaks - I wouldn't be surprised if the scraping breaks for a different university's website, although I hope blackboard's format stays the same. In particular, if you see a printout complaining about an unknown type, let us know! If the documentation is not clear on a topic, open a bug report and I'll try and fix it.

# Usage
Ensure you have python (obviously), selenium, and a chromium webdriver.

Run main.py with a single argument - your university's login page. After inspecting the source to check it won't send me your password, log in on the instance of chrome that opens. Navigate to the learning resources page of your chosing. Click enter in the terminal. By default, this will download the entire course learning resources, copy all links and text, and DOWNLOAD ALL OF THE LECTURES FROM ECHO. If you don't want to use this feature, read details.

# Configuration
Every download from is completed by the `downloadlink()` and function in base.py. Each download only succeeds if the `downloadok` returns `1`. You can configure what items you download by editing these functions. For instance, if you don't want to download any lectures, make `downloadok` return 0 if `bone["type"] = "Lecture_Recordings"`. By default, the files will be named after the text in blackboard of the item. 

If you want to not traverse into certain folders, edit the `downloadskeleton` function in main.py.

If you wish to download only some echo videos, then edit the selectvideos() function in echo.py. This function has access to information scraped from echo.

# Details
This will open a webdriver which first scrapes the html for the structure and links of the page. Each entry corresponds to one item in the blackboard page. Once it has done this, it stores the data in nested dictionaries, with a folder's contents in a list under its contents key. Then it will download the files. Feel free to replace the downloading script with your own.

For more details, see the documentation in the code.

# Todo
- Add support for blacklisting entire folders or filetypes. 
- Introduce options for file naming for the user. In particular, blackboard vs url names, depending on file type, item type, folder location etc.
- Add options for putting items in folders or stand alone
- Add ability to "refresh" a download (must be able to handle modified files, option to regenerate if files are moved/deleted, or just were downloaded?)
- Cookie pickling
