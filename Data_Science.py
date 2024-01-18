import tkinter as tk
from tkinter import scrolledtext
from tkinter import Label, Entry, Button
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import bs4
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re 

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
    time.sleep(5)

def scrape_lazada(search_term):
    # Initialize the driver
    driver = webdriver.Chrome()
    driver.get('https://www.lazada.com.ph/')
    time.sleep(5)

    # Close the popup if it's present
    close_popup(driver)

    # Search for the specified term
    search = driver.find_element(By.XPATH, '//*[@id="q"]')
    search.send_keys(search_term)
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

    # Extract details from the first 10 product elements
    product_details = []
    if product_grid:
        product_elements = product_grid.find_all('div', {'data-qa-locator': 'product-item'})[:10]

        for index, element in enumerate(product_elements, 1):
            title = element.find('div', {'class': 'RfADt'}).find('a')['title']
            price = float(element.find('span', {'class': 'ooOxS'}).text.replace('₱', '').replace(',', ''))

           # Error handling for discount
            discount_element = element.find('span', {'class': 'IcOsH'})
            discount_text = discount_element.text if discount_element else '0%'
            
            # Extracting only the numeric part from the discount using regular expression
            discount_match = re.search(r'\d+', discount_text)
            discount = float(discount_match.group()) if discount_match else 0

            sold_count_element = element.find('span', {'class': '_1cEkb'})
            sold_count_text = sold_count_element.find_all('span')[0].text if sold_count_element else '0 sold'
            
            # Extracting only the numeric part from the sold count using regular expression
            sold_count_match = re.search(r'\d+', sold_count_text)
            sold_count = int(sold_count_match.group()) if sold_count_match else 0

            location_element = element.find('span', {'class': 'oa6ri'})
            location = location_element.text if location_element else None

            product_details.append({
                'Name': title,
                'Price': price,
                'Discount': discount,
                'Sold': sold_count,
                'Location': location
            })

    # Close the driver
    driver.quit()

    return product_details

def on_search_button_click():
    search_term = entry_search.get()
    result_text.config(state='normal')
    result_text.delete(1.0, tk.END)

    scraped_data = scrape_lazada(search_term)

    # Plotting the comparison chart
    fig, axs = plt.subplots(3, figsize=(10, 10), sharex=True)
    fig.suptitle('Product Comparison')

    # Extracting data for plotting
    names = [product['Name'] for product in scraped_data]
    prices = [product['Price'] for product in scraped_data]
    discounts = [product['Discount'] for product in scraped_data]
    sold_counts = [product['Sold'] for product in scraped_data]

    # Plotting Price
    axs[0].bar(names, prices, color='blue')
    axs[0].set_ylabel('Price (₱)')

    # Plotting Discount
    axs[1].bar(names, discounts, color='orange')
    axs[1].set_ylabel('Discount (%)')

    # Plotting Sold Count
    axs[2].bar(names, sold_counts, color='green')
    axs[2].set_ylabel('Sold Count')

    # Display the plot on Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

    result_text.config(state='disabled')

# Tkinter UI setup
window = tk.Tk()
window.title("Lazada Scraper")

# Set custom background color
window.configure(bg="#36393F")  # Discord background color

# Entry widget for search term
label_search = Label(window, text="Enter product name:", bg="#36393F", fg="white")
label_search.grid(row=0, column=0, padx=(10, 0), pady=10, sticky="e")  # Adjust padx and sticky parameters
entry_search = Entry(window, bg="#36393F", fg="white")  # Discord input box color
entry_search.grid(row=0, column=1, padx=5, pady=10, sticky="w")  # Adjust padx and sticky parameters

# Button for initiating the search
search_button = Button(window, text="Search", command=on_search_button_click, bg="#36393F", fg="white")  # Discord button color
search_button.grid(row=0, column=2, padx=(0, 380), pady=10, sticky="e")  # Adjust padx and sticky parameters

# Text widget for displaying results
result_text = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=80, height=20, bg="#36393F", fg="white")
result_text.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")  # Add sticky="nsew"
result_text.config(state='disabled')

# Configure row and column weights
window.grid_rowconfigure(2, weight=1)
window.grid_columnconfigure(0, weight=1)

window.mainloop()
















