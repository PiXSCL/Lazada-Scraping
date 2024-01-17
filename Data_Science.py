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

# Print the product grid for debugging
print("Product Grid:", product_grid)

# Get links directly from the search result page
data = driver.page_source
soup = bs4.BeautifulSoup(data, 'html.parser')

# Find the product grid
product_grid = soup.find('div', {'data-qa-locator': 'general-products'})

if product_grid:
    # Find all product items in the grid
    product_elements = product_grid.find_all('div', {'data-qa-locator': 'product-item'})[:10]

    # Print the first 10 product elements for debugging
    print("First 10 Product Elements:")
    for index, element in enumerate(product_elements, 1):
        print(f"{index}. {element}")

# Close the main driver when you're done    
driver.quit()









