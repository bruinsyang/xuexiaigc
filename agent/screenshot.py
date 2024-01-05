import os
import re
import time

from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse
from common.agent import Agent

class ScreenshotAgent(Agent):
    def __init__(self, cos_client, cos_prefix, output, log_fd, just_upload_to_cos, just_do_ci_process):
        Agent.__init__(self, output, log_fd)
        self._cos_client = cos_client
        self._cos_prefix = cos_prefix
        self._just_upload_to_cos = just_upload_to_cos
        self._just_do_ci_process = just_do_ci_process
        self._local_file = ""

    def set_local_file_by_url(self, url):
        parts = urlparse(url)
        domain = parts.netloc
        fdomain = domain.replace("www.", "")
        fdlist = fdomain.split(".")
        path = parts.path
        plist = path.split("/")
        fplist = list(filter(None, plist))
        self._local_file = "-".join(fdlist + fplist + ["screenshot.png"])
        #print("set to:", self._local_file)

    def is_screenshot_exist(self, url):
        okey = self._cos_prefix + self._local_file
        object_info = self._cos_client.does_object_exist(okey)
        if object_info:
            print("Exist url:", url)
            return True
        else:
            return False

    def image_color_counts(self, driver):
        screenshot = driver.get_screenshot_as_png()
        image = Image.open(BytesIO(screenshot))
        pixels = image.load()
        color_counts = {}
        for x in range(image.width):
            for y in range(image.height):
                color = pixels[x, y]
                if color in color_counts:
                    color_counts[color] += 1
                else:
                    color_counts[color] = 1

        return len(color_counts)

    def capture_website_screenshot(self, url):
        #TODO
        #print(self._local_file)
        #return True
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--window-size=1920,1080')
        #chrome_options.add_argument('--window-size=3840,4320')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        try:
            driver = webdriver.Chrome(options=chrome_options)
            #driver.implicitly_wait(20)
            driver.get(url)
            time.sleep(10)
            #WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

            width = driver.execute_script("return Math.max(document.body.scrollWidth, document.body.offsetWidth, document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth);")
            height = driver.execute_script("return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);")
            #print(url, width, height)

            if height > 4320:
                height = 4320

            color_num = self.image_color_counts(driver)
            if color_num < 1500:
                print("%s screenshot with color counts %d" %(url, color_num))

            driver.set_window_size(width, height)
            driver.save_screenshot(self._local_file)
            driver.quit()
            return True
        except Exception as e:
            #print("Get %s error with: %s" %(url, e))
            return False

    def record_screenshot_info(self, line, ourl):
        msg = line + "\t" + ourl
        if self._output:
            with open(self._output, "a") as file:
                file.write(msg + "\n")
        else:
            print(msg)

    def put_original_screenshot_to_cos(self):
        if self._local_file == "":
            return
        okey = self._cos_prefix + self._local_file
        self._cos_client.upload_object_from_file(self._local_file, okey)
        os.remove(self._local_file)

    def generate_final_screenshot_with_ci(self):
        okey = self._cos_prefix + self._local_file
        fileid = "/website-screenshot/" + self._local_file.replace("png", "jpeg")
        operations = '{"rules":[{"fileid":"' + fileid + '","rule":"style/websiteformatstyle"}]}'
        #print(operations)
        response, data = self._cos_client.ci_image_process(okey, operations)
        if response == None:
            return None
        #print(response['x-cos-request-id'])
        #print(data['ProcessResults']['Object']['ETag'])
        return fileid

    def process_one_record(self, record):
        print("processing record: ", record)
        tlist = re.split('\t', record)
        url = tlist[0]

        # 1. Set screenshot local file name
        self.set_local_file_by_url(url)

        # 2. Check the screenshot exist or not on COS
        result = self.is_screenshot_exist(url)
        if self._just_do_ci_process == False and result:
            return True

        # 3. Capture website screenshot
        if self._just_do_ci_process == False:
            result = self.capture_website_screenshot(url)
            if result == False:
                return False
            self.put_original_screenshot_to_cos()

        if self._just_upload_to_cos == True:
            return True

        # 4. Generate final image with CI
        okey = self.generate_final_screenshot_with_ci()
        if okey == None:
            return False
        ourl = self._cos_client.get_object_url(okey)
        self.record_screenshot_info(record, ourl)

        return True

