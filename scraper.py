from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
import csv

main_list = list() # Initialize the main list to store the data
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
    }

def get_links(): # Function to get the listing URLs
    driver = webdriver.Chrome() # Set up the WebDriver
    driver.get("https://www.hepsiemlak.com/buca-kiralik") # Open the desired page
    with open("listing_links.txt", "w", encoding="utf-8") as file: # Open a file to write the links
        while True:
            try:
                WebDriverWait(driver, 10).until( # Wait for the listings to load
                    EC.visibility_of_element_located((By.CLASS_NAME, "listingView")) # Wait for the listing elements to be visible
                )

                listings = driver.find_elements(By.CLASS_NAME, "listingView") # Find all the listing elements
                
                # Loop through the listings and extract the href attribute of each link
                for listing in listings:
                    link_element = listing.find_element(By.CLASS_NAME, "img-link")
                    listing_url = link_element.get_attribute("href")
                    file.write(listing_url + "\n")
                    print(listing_url)  # Optionally, print the URL to the console

                # Check if the "Sonraki Sayfa" button is enabled
                next_button = driver.find_element(By.CLASS_NAME, "he-pagination__navigate-text--next")
                if "disabled" in next_button.get_attribute("class"):
                    print("No more pages to process.")
                    break
                
                next_button.click() # Click the "Sonraki Sayfa" button
                time.sleep(2)  # Wait for the next page to load
            except (NoSuchElementException, TimeoutException): # If the element is not found or the timeout is reached
                print("No more pages to process.")
                break

    driver.quit() # Close the browser when done

def scraper(): # Function to scrape the data from the listings
    with open("listing_links.txt", "r") as url_list_file: # Open the file containing the URLs
        for line in url_list_file: # Loop through the URLs
            time.sleep(3) # Add a delay to avoid overloading the server
            attribute_dict = dict() # Initialize a dictionary to store the attributes
            line = line.strip() # Remove leading and trailing whitespaces from the URL
            if "https" not in line: # Check if the URL is valid
                continue
            response = requests.get(line, headers=headers) # Send a GET request to the URL

            # Check if the response is successful
            try:
                response.raise_for_status() # Check if the response is successful
            except Exception as ex: 
                print(f"ERROR: {ex}") # Print the error message
                break

            soup = BeautifulSoup(response.text, 'html.parser') # Parse the HTML content of the page

            # Extract the desired information from the page
            listing_heading = soup.find('h1', class_='fontRB').get_text(strip=True)
            attribute_dict['listing_url'] = line
            attribute_dict['listing_heading'] = listing_heading
            listing_price = soup.find('p', class_='fz24-text price').get_text(strip=True)
            attribute_dict['listing_price'] = listing_price
            spec_items = soup.find_all('li', class_='spec-item')

            # Loop through the spec items and extract the key-value pairs
            for item in spec_items:
                spans = item.find_all('span')
                if len(spans) >= 2: 
                    key = spans[0].get_text(strip=True)
                    value = spans[1].get_text(strip=True)
                    attribute_dict[key] = value        
            
            main_list.append(attribute_dict) # Append the attribute dictionary to the main list
        
def csv_writer(): # Function to write the data to a CSV file
    with open("output_csv.csv", "w", newline='', encoding="utf-8") as csv_file: # Open the CSV file to write the data
        all_keys = list()
        for item in main_list: # Loop through the main list to extract all the keys
            for key in item.keys(): # Loop through the keys of each dictionary
                if key not in all_keys: # Check if the key is already in the list
                    all_keys.append(key) # Append the key to the list if it is not already there
        
        csv_writer = csv.DictWriter(csv_file, fieldnames=all_keys) # Create a CSV writer object
        csv_writer.writeheader() # Write the header row

        # Loop through the main list and write the data to the CSV file
        for row in main_list:
            try: 
                csv_writer.writerow(row) # Write the row to the CSV file
            except ValueError as ex: 
                pass # Handle the ValueError exception

def csv_to_excel(): # Function to convert the CSV file to an Excel file
    csv_file = 'output_csv.csv' # CSV file path
    df = pd.read_csv(csv_file) # Read the CSV file
    excel_file = 'buca_listings.xlsx' # Excel file path
    df.to_excel(excel_file, index=False, engine='openpyxl') # Write the data to an Excel file

def main(): # Main function to run the program
    print ("Starting the process...")
    print("Getting the listing URLs...")
    get_links() # Get the listing URLs
    print("Scraping the data from the listings...")
    scraper() # Scrape the data from the listings
    print("Writing the data to a CSV file...")
    csv_writer() # Write the data to a CSV file
    print("Converting the CSV file to an Excel file...")
    csv_to_excel() # Convert the CSV file to an Excel file

if __name__ == "__main__":
    main() # Call the main function
