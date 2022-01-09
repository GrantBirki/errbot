import uuid
from io import BytesIO

from PIL import Image
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class DownDetector:
    """
    A helper class for interacting with and scraping the downdetector.com website
    """

    def __init__(self, output_dir="plugins/lib/common/tmp"):
        """
        Initializes the DownDetector class
        """
        self.output_dir = output_dir

    def chart(self, service):
        """
        Gets the chart of a service from downdetector.com
        :param service: the service to get the chart for (e.g. "escape-from-tarkov")
        :return: the path to the downloaded chart (String) - False if anything fails

        Note: The service can be found in the url after /status/ -> https://downdetector.com/status/escape-from-tarkov/
        """

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

        # Open the website
        driver.get(f"https://downdetector.com/status/{service}/")

        # Wait for the chart to load
        WAIT = 2
        try:
            WebDriverWait(driver, WAIT).until(
                EC.presence_of_element_located((By.ID, "chart-row"))
            )
        except TimeoutException:
            return False

        # Get the chart element
        s = driver.find_element(By.XPATH, "//body/div[3]/div[2]/div[1]/div[2]/div[1]")

        # Get the sizes of the chart for cropping
        location = s.location
        size = s.size
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

        # close browser
        driver.close()
        driver.quit()
        display.stop()

        return file_name
