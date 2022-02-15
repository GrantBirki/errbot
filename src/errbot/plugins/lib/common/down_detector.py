import uuid
from io import BytesIO

import validators
from lib.common.errhelper import ErrHelper
from PIL import Image
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

OK = "no current problems"
DOWN = "reports indicate problems"
WARNING = "indicate possible problems"


class DownDetector:
    """
    A helper class for interacting with and scraping the downdetector.com website
    """

    def __init__(self, output_dir="plugins/lib/common/tmp"):
        """
        Initializes the DownDetector class
        """
        self.output_dir = output_dir
        self.bad_characters = "\\/;*?\"<>$#@!|[}]{=^%"

    def chart(self, service, search=False):
        """
        Gets the chart of a service from downdetector.com
        :param service: the service to get the chart for (e.g. "escape-from-tarkov")
        :param search: Defaults to False, set to True if you want to attempt to search for a service rather than an exact match on a service name - (e.g. "escape from tarkav" - with a typo)
        :return file_name: the path to the downloaded chart (String) - False if anything fails
        :return status: best effort guess of the status of the service (String)

        Note: The service can be found in the url after /status/ -> https://downdetector.com/status/escape-from-tarkov/

        Note: If the 'search' flag is set to True, the service will be searched for rather than a straight up GET call. If you can use the exact service name, it is recommended
        """

        try:

            display = Display(visible=0, size=(1920, 1080))
            display.start()

            options = Options()
            options.add_argument("--no-sandbox")
            options.add_argument("--headless")
            options.add_argument("log-level=3")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")
            options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
            )

            # initializing webdriver for Chrome with our options
            driver = webdriver.Chrome(options=options)

            # If the search flag was provided, we search for the service in DownDetector
            if search:
                driver.get(
                    f"https://downdetector.com/search/?q={service.replace(' ', '+')}"
                )

            # If the search flag was not provided, we attempt to go directly to the service page
            else:
                driver.get(f"https://downdetector.com/status/{service}/")

            # Wait for the chart to load
            WAIT = 2
            try:

                # If we used the search flag, check the page to ensure a result was found
                if search:
                    # check the search input
                    if self.bad_input(service):
                        # close browser
                        driver.close()
                        driver.quit()
                        display.stop()
                        return False, f"❌ Bad search string: `{service}`"

                    # If the search returned no results, return None
                    # dev note: the /search/ url stays if no results are found
                    if "/search/?q=" in driver.current_url:
                        return None, None

                WebDriverWait(driver, WAIT).until(
                    EC.presence_of_element_located((By.ID, "chart-row"))
                )
            except TimeoutException:
                return False, False

            # Get the chart element
            chart_elem = driver.find_element(
                By.XPATH, "//body/div[3]/div[2]/div[1]/div[2]/div[1]"
            )

            # Get the sizes of the chart for cropping
            location = chart_elem.location
            size = chart_elem.size
            x = location["x"]
            y = location["y"]
            h = location["y"] + size["height"]
            w = location["x"] + size["width"]

            # Save the chart screenshot to memory
            p = driver.get_screenshot_as_png()

            # Open the captured image to crop it
            img_open = Image.open(BytesIO(p))

            # Crop the image
            img_crop = img_open.crop((x, y, w, h))

            # Save the cropped image
            # Example url https://downdetector.com/status/escape-from-tarkov/
            file_name = f"{self.output_dir}/{service}-{uuid.uuid4()}.png"
            img_crop.save(file_name)

            try:
                # Make a best effort attempt to get the status of the service from the page header
                page_header = driver.find_element(
                    By.XPATH,
                    "/html[1]/body[1]/div[3]/div[2]/div[1]/div[1]/div[1]/div[1]",
                )
                # Get the header text
                page_header_text = page_header.text.strip().lower()

                # Get and format the service name from the URL
                service_name = (
                    driver.current_url.split("/status/")[-1]
                    .replace("-", " ")
                    .replace("/", "")
                )

                # Set the status based on the text of the header page
                if OK in page_header_text:
                    status = f"🟢 User reports do not indicate problems for **{service_name}**"
                elif DOWN in page_header_text:
                    status = f"🔴 User reports indicate problems for **{service_name}**"
                elif WARNING in page_header_text:
                    status = f"🟡 User reports indicate possible problems for **{service_name}**"
                else:
                    # unknown status, maybe DownDetector changed their page layout
                    status = f"❓ The status of **{service_name}** is unknown due to a processing error"
            except:
                status = f"❓ The status of **{service_name}** is unknown due to a processing error"

            # close browser
            driver.close()
            driver.quit()
            display.stop()

            return file_name, status

        except Exception as error:
            ErrHelper().capture(error)

            # close browser in the case of an error
            driver.close()
            driver.quit()
            display.stop()

            return False, "❌ A critical error occurred while trying to get the chart"

    def bad_input(self, data):
        """
        Helper function to check if provided data is 'bad'
        Bad could be data that is not a valid search string or malicious
        :param data: data to check (String)
        :return bool: true if bad data - false otherwise
        """
        # If the provided input is a URL, it is bad
        if validators.url(data):
            return True

        # Check against our 'bad_characters' list
        for sub_string in self.bad_characters:
            if sub_string in data:
                # If a 'bad character' is found, return true
                return True

        # Add more check here...

        return False
        