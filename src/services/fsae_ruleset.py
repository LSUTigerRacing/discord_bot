from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

"""Scrape FSAE Website for the latest rules pdf url"""
def get_latest_rules_url():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') # run in background
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get("https://www.fsaeonline.com/cdsweb/gen/DocumentResources.aspx")

        # click rules dropdown
        rules_menu = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.LINK_TEXT, "Ruleset and Resources"))
        )
        rules_menu.click()
        print("clicked.")
        #wait for dropdown to appear
        pdf_link = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href,'.pdf')]"))
        )
        pdf_url = pdf_link.get_attribute('href')

        return pdf_url
    
    except Exception as e:
        print(f"Error encountered while scraping: {e}")
        return None
    
    finally:
        driver.quit()


print(get_latest_rules_url())