# tasks.py
# from .my_pass import LOGIN_PASSWORD, LOGIN_USERNAME, SEARCH_ITEM
from celery import shared_task
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from .my_pass import LOGIN_USERNAME,LOGIN_PASSWORD

"""
This module defines a Celery task that automates interactions with Facebook using Selenium.

Task: `run_selenium_bot`
-------------------------
- Automates the process of logging into Facebook, searching for a specific user, accessing 
  their photos, and saving the results as screenshots and a CSV file of photo URLs.

Parameters:
-----------
- `table` (str): Name of the database table triggering the task.
- `record_id` (int): ID of the database record associated with the task.
- `operation` (str): Type of database operation that triggered the task (e.g., "INSERT").

Key Features:
-------------
1. **Facebook Automation**:
   - Logs into Facebook with hardcoded credentials.
   - Searches for a target user by name.
   - Accesses and scrolls through the user's photo section.

2. **Photo Capture and Storage**:
   - Takes a screenshot of the photos page.
   - Extracts photo URLs and saves them to a CSV file.

3. **Error Handling**:
   - Ensures the Selenium WebDriver quits in case of an error.
   - Logs exceptions and returns the status of the task.

Dependencies:
-------------
- `selenium`: For automating browser actions.
- `pandas`: For saving photo URLs to a CSV file.
- `celery`: For handling asynchronous task execution.

"""


@shared_task
def run_selenium_bot(table, record_id, operation):
    print(f"Running bot for table={table}, record_id={record_id}, operation={operation}")

    try:
        # Set up the Selenium WebDriver with options
        chrome_options = Options()
        chrome_options.add_argument("--incognito")
        chrome_options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 2  # Block popups
        })

        # Initialize the Selenium WebDriver
        driver = webdriver.Chrome(options=chrome_options)
        url = 'https://facebook.com'
        driver.get(url)
        time.sleep(5)
        
        # Accept cookies (if they appear)
        try:
            popup = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="facebook"]/body/div[3]/div[2]/div/div/div/div/div[3]/div[2]/div/div[2]/div[1]/div')))
            popup.click()
        except:
            print('No cookie alert appeared. Continue...')
        
        time.sleep(2)
        
        # Find and fill username
        user_name_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'email')))
        user_name_field.click()
        user_name_field.send_keys(LOGIN_USERNAME)  
        time.sleep(2)
        
        # Find and fill password field
        pass_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'pass')))
        pass_field.click()
        pass_field.send_keys(LOGIN_PASSWORD)  
        pass_field.send_keys(Keys.ENTER)
        time.sleep(2)

        print('Logged in successfully')

        # Handle pop-ups or notifications after login
        try:
            desktop_notif = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id=":r3e:"]/div/div/div/div/div/div/div[2]/div')))
            desktop_notif.click()
        except:
            print('Notification after login did not show')
            
        # Search for the target account
        search_field = WebDriverWait(driver,5).until(EC.presence_of_element_located((By.XPATH, '//*[contains(concat( " ", @class, " " ), concat( " ", "x19gujb8", " " ))]')))
        # search_field = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,'/html/body/div[1]/div/div/div[1]/div/div[2]/div[3]/div/div/div[1]/div/div/label/input'))) 
        search_field.send_keys('amiroism')  
        search_field.send_keys(Keys.ENTER)
        print('I searched the name')

        # # Wait until the 'See all' button appears and click it
        # see_all = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[contains(concat( " ", @class, " " ), concat( " ", "xuxw1ft", " " ))]')))

        # # see_all = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//a[@aria-label="See all"]')))
        # see_all.click()

        try:
            see_all = WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH,'//*[contains(concat( " ", @class, " " ), concat( " ", "x1e0frkt", " " ))]')))
            print('I found see all') 
            see_all.click()   
            print('I clicked on see all button')  
        except Exception as e:
            print(f'i couldnt find see all button , {e}')
        time.sleep(2)  

        # Click on the target account
        target_account_xpath = "//a[contains(text(), 'Amir Hatami (Amiro)')]"
        targeted_search = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, target_account_xpath)))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", targeted_search)
        targeted_search.click()
        print('I found profile')

        # Access photos and scroll down to get more photos
        photos_list = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//a[contains(text(),"Photos")]')))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", photos_list)
        photos_list.click()
        time.sleep(2)
        
        driver.execute_script("window.scrollBy(0, 700);")
        print(' I scrolled.')
        # Take a screenshot of the photos
        driver.get_screenshot_as_file(f'order_{record_id}_photos.png')

        list_photos = []

        # Capture the photo URLs
        pictures = driver.find_elements(By.XPATH, '//img[contains(@class, "xzg4506")]')
        for pic in pictures:
            image = pic.get_attribute("src")
            list_photos.append([image])

        # Save the photo URLs to a CSV file
        if list_photos:
            import pandas as pd
            dataframe = pd.DataFrame(list_photos, columns=['photos'])
            dataframe.to_csv(f'order_{record_id}_photos.csv', index=False)
            print(f'Saving photos for order {record_id} was successful.')
        else:
            print(f'No photos found for order {record_id}.')

        # Finish up
        driver.quit()
        return f"Bot successfully completed for order {record_id}"

    except Exception as e:
        # Handle exceptions and close the driver
        driver.quit()
        return f"Task executed for table={table}, record_id={record_id}, operation={operation}"


