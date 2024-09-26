import json
import time
import os
from tempfile import mkdtemp
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

def handler(event=None, context=None):
  # Configure Selenium to use Chrome in headless mode
  print(os.listdir("."))
  options = webdriver.ChromeOptions()
  service = webdriver.ChromeService("/opt/chromedriver")

  options.binary_location = "/opt/chrome/chrome"
  options.add_argument("--headless=new")
  options.add_argument("--no-sandbox")
  options.add_argument("--disable-gpu")
  options.add_argument("--window-size=1280x1696")
  options.add_argument("--single-process")
  options.add_argument("--disable-dev-shm-usage")
  options.add_argument("--disable-dev-tools")
  options.add_argument("--no-zygote")
  options.add_argument(f"--user-data-dir={mkdtemp()}")
  options.add_argument(f"--data-path={mkdtemp()}")
  options.add_argument(f"--disk-cache-dir={mkdtemp()}")
  options.add_argument("--remote-debugging-port=9222")

  chrome = webdriver.Chrome(options=options, service=service)
  base_url = "https://www.abc.org/Membership/MasterFormat-CSI-Codes-NAICS-Codes/CSI-Codes"

  # List to store the extracted CSI codes
  csi_codes = []
  processed_categories = set()
  failed_categories = set()


  def scrape_page():
      """Scrape the main page and follow links to nested pages."""
      print(f"Opening {base_url}")
      chrome.get(base_url)

      # Wait until the links are present
      wait = WebDriverWait(chrome, 10)
      wait.until(EC.presence_of_element_located((By.CLASS_NAME, "numCase")))

      # Extract top-level categories
      link_categories = set(
          map(
              lambda x: x.text.strip(),
              set(chrome.find_elements(By.CLASS_NAME, "numCase")),
          )
      )

      while link_categories.difference(processed_categories):
        
          print(len(link_categories.difference(processed_categories | failed_categories)))

          category_name = link_categories.difference(processed_categories).pop()
          print(f"Processing category: {category_name}")
          wait.until(EC.presence_of_element_located((By.CLASS_NAME, "numCase")))
          chrome.find_element(By.XPATH, '//body').send_keys(Keys.CONTROL + Keys.HOME)
          time.sleep(0.5)
          # Click the link to navigate to the category page
          try:
              chrome.find_element(By.PARTIAL_LINK_TEXT, category_name).click()
          except Exception as e:
              failed_categories.add(category_name)
              processed_categories.add(category_name)
              print(f"Error clicking link: {e}")
              continue
          # Wait for the page to load
          time.sleep(2)

          # Scrape codes from the category page
          scrape_codes()
          processed_categories.add(category_name)
          # Navigate back to the main page
          chrome.back()


  def scrape_codes():
      """Scrape CSI codes from the current page."""
      # Wait until the codes are present
      wait = WebDriverWait(chrome, 10)
      wait.until(EC.presence_of_element_located((By.CLASS_NAME, "subcode")))

      # Extract code elements
      subcodes = chrome.find_elements(By.CLASS_NAME, "subcode")
      # print([code.get_attribute('innerHTML') for code in subcodes])
      subcode_names = chrome.find_elements(By.CLASS_NAME, "subcode-name")
      for subcode, subcode_name in zip(subcodes, subcode_names):
          subcode_text = subcode.get_attribute("innerHTML")
          subcode_name_text = subcode_name.get_attribute("innerHTML")
          split_subcode = subcode_text.split(" ")
          db_line = {
              "id": subcode_text,
              "primaryCode": split_subcode[0],
              "secondaryCode": split_subcode[1],
              "tertiaryCode": split_subcode[2],
              "codeDescription": subcode_name_text,
          }
          print(f"{subcode_text} {subcode_name_text}")
          csi_codes.append(db_line)


  try:
      scrape_page()
  finally:
      # Close the WebDriver
      chrome.quit()

  # Output the collected CSI codes
  print("\nCollected CSI Codes:")
  for code in list(processed_categories.difference(failed_categories)):
      print(code)

  print("\nFailed categories:")
  for category in failed_categories:
      print(category)

  with open("successful_categories.json", "w") as file:
      json.dump(list(processed_categories.difference(failed_categories)).sort(), file, indent=2)

  # Optionally, save the codes to a file
  with open("csi_codes_all.json", "w") as file:
      json.dump(csi_codes, file, indent=2)

if __name__ == "__main__":
    handler()