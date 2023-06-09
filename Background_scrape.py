from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import pandas as pd
import numpy as np
from lxml import html
import os


from datetime import datetime, timedelta

# from final_project import options

# from final_project import df

# these are the indices which we provide in dropdown

chrome_options = Options()
chrome_options.add_argument("--headless")  # Enable headless mode
chrome_service = Service("/path/to/chromedriver")
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

# navigate to the webpage
driver.get("https://nepsealpha.com/nepse-data")

# wait for the relevant elements to load
wait = WebDriverWait(driver, 200)
wait.until(
    EC.presence_of_element_located(
        (
            By.XPATH,
            '//*[@id="vue_app_content"]/div[3]/div/div/div/form/div/div/div[2]/input',
        )
    )
)

# calculate start and end dates

end_date = datetime.today().strftime("%m/%d/%Y")
start_date = (datetime.today() - timedelta(days=3650)).strftime("%m/%d/%Y")

# fill in the start date

start_date_input = driver.find_element(
    By.XPATH, '//*[@id="vue_app_content"]/div[3]/div/div/div/form/div/div/div[2]/input'
)
start_date_input.clear()
start_date_input.send_keys(start_date)

# fill in the end date

end_date_input = driver.find_element(
    By.XPATH, '//*[@id="vue_app_content"]/div[3]/div/div/div/form/div/div/div[3]/input'
)
end_date_input.clear()
end_date_input.send_keys(end_date)

# select the symbol or indices
symbol_name = "NABIL (Nabil Bank Limited)"

# click on the symbol or indices dropdown
symbol_name_dropdown = driver.find_element(
    By.XPATH,
    '//*[@id="vue_app_content"]/div[3]/div/div/div/form/div/div/div[4]/span/span[1]/span',
)
symbol_name_dropdown.click()

# enter the search text and wait for results to load
search_box = driver.find_element(By.XPATH, "/html/body/span/span/span[1]/input")
search_box.send_keys(symbol_name)
wait.until(
    EC.visibility_of_element_located(
        (
            By.CSS_SELECTOR,
            ".select2-results__option.select2-results__option--highlighted",
        )
    )
)

# select the searched item from the dropdown
search_results = driver.find_elements(
    By.CSS_SELECTOR, ".select2-results__option.select2-results__option--highlighted"
)
for result in search_results:
    if symbol_name in result.text:
        result.click()
        break


# click on the submit button to get the data
filter_button = driver.find_element(
    By.XPATH, '//*[@id="vue_app_content"]/div[3]/div/div/div/form/div/div/div[5]/button'
)
filter_button.click()


# wait for the table to load
wait.until(
    EC.presence_of_element_located(
        (By.XPATH, '//*[@id="result-table_wrapper"]/div[1]/button[4]')
    )
)
data = []
# Scrape the first 100 entries on the first page
for i in range(
1, 101):
    row = []
    for col in range(1, 7):  # Assuming there are 6 columns in each row
        table_cell = driver.find_element(
            By.XPATH, '//*[@id="result-table"]/tbody/tr[{}]/td[{}]'.format(i, col)
        )
        row.append(table_cell.text)
    data.append(row)

# Iterate through the remaining pages and scrape the data
for j in range(1, 5):
    # Click the "Next" button
    next_button = driver.find_element(By.XPATH, '//a[@class="paginate_button next"]')
    next_button.click()
    time.sleep(5)  # Wait for the page to load

    # Scrape the next 100 entries on the current page
    for i in range(1, 101):
        row = []
        for col in range(1, 7):  # Assuming there are 6 columns in each row
            table_cell = driver.find_element(
                By.XPATH, '//*[@id="result-table"]/tbody/tr[{}]/td[{}]'.format(i, col)
            )
            row.append(table_cell.text)
        data.append(row)

# Define the column names
column_names = ["Stock Name", "Date", "Open", "High", "Low", "Close"]

# Create a DataFrame from the scraped data
df = pd.DataFrame(data, columns=column_names)

# Save the data to a CSV file
filename = "scraped_data.csv"
df.to_csv(filename, index=False)

# Get the absolute path of the saved file
abs_path = os.path.abspath(filename)

# Print the absolute path of the saved file
print("Data saved to:", abs_path)

# Close the web driver
driver.quit()
