from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests

def scrape_cars():
    """Scrapper function for scrapping cars data from the listed website."""
    url = 'https://www.carmudi.com.ph/used-cars/makati/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    cars = []
    containers = soup.find_all('div', class_='new__car__lists used__inventory')

    for container in containers:
        title = container.find('div', class_="new__car__title d-flex align-items-center").text.strip()
        price = container.find('div', class_='new__car__price').text.split('View Seller Details')[0].strip()
        details = container.find('p', class_='shortDescription').text.strip()

        car_data = {'title': title, 'price': price, 'details':details}
        cars.append(car_data)

    return cars