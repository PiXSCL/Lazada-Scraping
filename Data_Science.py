from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import bs4
import time

def close_popup(driver):
    try:
        popup = driver.find_element_by_class_name('mod-signup-login-popup__close-btn')
        popup.click()
        time.sleep(3)
    except:
        pass

def sort_by_lowest_price(driver):
    sorting_dropdown = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[@class="ant-select ant-select-lg XPPbv ant-select-single ant-select-show-arrow"]'))
    )
    sorting_dropdown.click()

    lowest_price_option = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[text()="Price low to high"]'))
    )
    lowest_price_option.click()

# Initialize the driver
driver = webdriver.Chrome()
driver.get('https://www.lazada.com.ph/')
time.sleep(5)

# Close the popup if it's present
close_popup(driver)

# Search for 'microwave and oven'
search = driver.find_element(By.XPATH, '//*[@id="q"]')
search.send_keys('microwave and oven')
search.send_keys(Keys.ENTER)
time.sleep(3)

# Stop loading using JavaScript
driver.execute_script("window.stop();")

# Refresh the page
driver.refresh()
time.sleep(5)

# Sort by 'Lowest Price'
sort_by_lowest_price(driver)

# Wait for the product grid to be visible
product_grid = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.XPATH, '//div[@data-qa-locator="general-products"]'))
)

# Get links directly from the search result page
data = driver.page_source
soup = bs4.BeautifulSoup(data, 'html.parser')

# Find the product grid
product_grid = soup.find('div', {'data-qa-locator': 'general-products'})

if product_grid:
    # Find all product items in the grid
    product_elements = product_grid.find_all('div', {'data-qa-locator': 'product-item'})[:10]

    # Extract details from each product element with error handling
    for index, element in enumerate(product_elements, 1):
        title = element.find('div', {'class': 'RfADt'}).find('a')['title']
        price = element.find('span', {'class': 'ooOxS'}).text

        # Error handling for discount
        discount_element = element.find('span', {'class': 'IcOsH'})
        discount = discount_element.text if discount_element else None

        sold_count_element = element.find('span', {'class': '_1cEkb'})
        sold_count = sold_count_element.find_all('span')[0].text if sold_count_element else None

        location_element = element.find('span', {'class': 'oa6ri'})
        location = location_element.text if location_element else None

        print(f"{index}. Title: {title}")
        print(f"   Price: {price}")
        print(f"   Discount: {discount}")
        print(f"   Sold Count: {sold_count}")
        print(f"   Location: {location}")
        print("\n")

# Close the main driver when you're done    
driver.quit()










