import tkinter as tk
from tkinter import Entry, Label, Button, Canvas, Scrollbar, Text
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
            title_element = element.find('div', {'class': 'RfADt'}).find('a')
            title = title_element['title']
            link = 'https://www.lazada.com.ph' + title_element['href']
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
                'Link': link,
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

    # Scraping data and plotting the comparison chart
    scraped_data = scrape_lazada(search_term)
    fig, axs = plt.subplots(4, figsize=(10, 15), sharex=True)  # Adjust the height (second parameter) as needed
    fig.suptitle('Product Comparison')

    # Extracting data for plotting
    names = [product['Name'] for product in scraped_data]
    prices = [product['Price'] for product in scraped_data]
    discounts = [product['Discount'] for product in scraped_data]
    sold_counts = [product['Sold'] for product in scraped_data]

    # Rotate x-axis labels to make them horizontal
    plt.xticks(rotation=45, ha="right")

    # Plotting Price
    axs[0].bar(names, prices, color='blue')
    axs[0].set_ylabel('Price (₱)')

    # Plotting Discount
    axs[1].bar(names, discounts, color='orange')
    axs[1].set_ylabel('Discount (%)')

    # Plotting Sold Count
    axs[2].bar(names, sold_counts, color='green')
    axs[2].set_ylabel('Sold Count')

    # Plotting Wave-Like Line Graph for Price, Discount, and Sold
    axs[3].plot(names, prices, label='Price', marker='o', linestyle='-', color='blue')
    axs[3].plot(names, discounts, label='Discount', marker='o', linestyle='-', color='orange')
    axs[3].plot(names, sold_counts, label='Sold', marker='o', linestyle='-', color='green')

    axs[3].set_ylabel('Values')

    # Display the plot on Tkinter window
    canvas = Canvas(window)
    canvas.grid(row=1, column=0, padx=10, pady=10, sticky="news")

    # Create a vertical scrollbar and link it to the canvas
    vbar = Scrollbar(window, orient=tk.VERTICAL, command=canvas.yview)
    vbar.grid(row=1, column=1, sticky="ns")
    canvas.config(yscrollcommand=vbar.set)

    # Create a frame to contain the plot
    frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=frame, anchor="nw")

    # Embed the plot in the frame
    canvas_widget = FigureCanvasTkAgg(fig, master=frame)
    canvas_widget.draw()
    canvas_widget.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # Set the canvas scrolling region
    canvas.config(scrollregion=canvas_widget.get_tk_widget().bbox("all"))

    # Create a text box for displaying product details
    text_box = Text(window, height=10, width=80, wrap=tk.WORD, bg="#36393F", fg="white")
    text_box.grid(row=2, column=0, padx=10, pady=10, sticky="news")

    # Insert product details into the text box
    for index, product in enumerate(scraped_data, 1):
        text_box.insert(tk.END, f"{index}. {product['Name']}\nPrice: ₱{product['Price']}\nDiscount: {product['Discount']}%\nSold: {product['Sold']}\nLocation: {product['Location']}\nLink: {product['Link']}\n\n")

# Tkinter UI setup
window = tk.Tk()
window.title("Lazada Scraper")

# Set fixed window size
window.geometry("800x800")  # Adjust the size as needed

# Set custom background color
window.configure(bg="#36393F")  # Discord background color

# Entry widget for search term
label_search = Label(window, text="Enter product name:", bg="#36393F", fg="white")
label_search.grid(row=0, column=0, padx=(10, 0), pady=10, sticky="e")  # Adjust padx and sticky parameters
entry_search = Entry(window, bg="#36393F", fg="white")  # Discord input box color
entry_search.grid(row=0, column=1, padx=5, pady=10, sticky="w")  # Adjust padx and sticky parameters

# Button for initiating the search
search_button = Button(window, text="Search", command=on_search_button_click, bg="#36393F", fg="white")  # Discord button color
search_button.grid(row=0, column=2, pady=10, sticky="e")  # Adjust pady and sticky parameters

# Configure row and column weights
window.grid_rowconfigure(1, weight=1)
window.grid_rowconfigure(2, weight=1)
window.grid_columnconfigure(0, weight=1)

window.mainloop()


































