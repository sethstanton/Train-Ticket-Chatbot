import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Install chromedriver
chromedriver_autoinstaller.install()

# Function to construct the URL for different journey types
def build_url(journey_type, origin, dest, lor, date, time=None, return_date=None, return_time=None, return_lor=None, adults=1, extra_time=0):
    base_url = "https://www.nationalrail.co.uk/journey-planner/"
    url = f"{base_url}?type={journey_type}&origin={origin}&destination={dest}&leavingType={lor}&leavingDate={date}&adults={adults}&extraTime={extra_time}"
    if time:
        url += f"&leavingHour={time[:2]}&leavingMin={time[2:]}"
    if journey_type == "return" and return_date and return_time and return_lor:
        url += f"&returnType={return_lor}&returnDate={return_date}&returnHour={return_time[:2]}&returnMin={return_time[2:]}"
    return url + "#O"

# Function to scrape prices from the URL
def scrape_prices(url):
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Ensure GUI is off
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    # Set up the webdriver
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    # Wait for JavaScript to load the dynamic content
    wait = WebDriverWait(driver, 10)
    wait.until(EC.visibility_of_element_located((By.ID, "main-content")))

    # Locate the section within the main-content
    main_section = driver.find_element(By.ID, "main-content")
    sections = main_section.find_elements(By.TAG_NAME, "section")
    prices = []

    # Iterate through each section to find list items and extract prices
    for section in sections:
        list_items = section.find_elements(By.TAG_NAME, "li")
        for item in list_items:
            try:
                button = item.find_element(By.XPATH, ".//button[contains(@id, 'result-card-selection-outward-')]")
                price_span = button.find_element(By.XPATH, ".//span[@class='styled__StyledCalculatedFare-sc-1gozmfn-2 goNENa']")
                price = price_span.text.strip('£')
                price = format_float(float(price))
                prices.append(price)
            except Exception as e:
                pass

    # Clean up: close the browser
    driver.quit()

    return prices

# Function to find the lowest price
def find_lowest_price(prices):
    if prices:
        return min(prices)
    else:
        return None

def format_date_url(date):
    year, month, day = date.split("-")

    short_year = year[2:]

    return day + month + short_year

def format_time_url(time):
    return time.replace(":", "")

def lor_formatting(lor):
    if lor == "leave":
        return "departing"
    elif lor == "arrive":
        return "arriving"

def format_float(price):
    # Convert the number to a string with two decimal places
    formatted = f"{price:.2f}"

    # Check if the second decimal place is '0' and remove it if necessary
    if formatted[-1] == '0':
        formatted = formatted[:-1]

    return formatted

# One way journey
def one_way(origin, dest, date, time, lor, adults=1, extra_time=0):
    date = format_date_url(date)
    time = format_time_url(time)
    lor = lor_formatting(lor)
    url = build_url("single", origin, dest, lor, date, time, adults=adults, extra_time=extra_time)
    prices = scrape_prices(url)
    return find_lowest_price(prices)

# Open ticket journey
def open_ticket(origin, dest, date, lor="departing", adults=1, extra_time=0):
    date = format_date_url(date)
    lor = lor_formatting(lor)
    time = "0800"
    url = build_url("single", origin, dest, lor, date, time, adults=adults, extra_time=extra_time)
    prices = scrape_prices(url)
    return find_lowest_price(prices)

# Open return journey
def open_return(origin, dest, leave_date, return_date, lor="departing", return_lor="departing", adults=1, extra_time=0):
    leave_date = format_date_url(leave_date)
    return_date = format_date_url(return_date)
    lor = lor_formatting(lor)
    return_lor = lor_formatting(return_lor)
    time = "0800"
    url = build_url("return", origin, dest, lor, leave_date, time, return_date, time, return_lor, adults=adults, extra_time=extra_time)
    prices = scrape_prices(url)
    return find_lowest_price(prices)

# Round trip journey
def round_trip(origin, dest, leave_date, leave_time, return_date, return_time, lor, return_lor, adults=1, extra_time=0):
    leave_date = format_date_url(leave_date)
    leave_time = format_time_url(leave_time)
    return_date = format_date_url(return_date)
    return_time = format_time_url(return_time)
    lor = lor_formatting(lor)
    return_lor = lor_formatting(return_lor)
    url = build_url("return", origin, dest, lor, leave_date, leave_time, return_date, return_time, return_lor, adults=adults, extra_time=extra_time)
    prices = scrape_prices(url)
    return find_lowest_price(prices)

# Example usage
if __name__ == "__main__":
    print("One way journey price:", one_way("NRW", "ABE", "240524", "0215", "departing", 1, 0))
    print("Open ticket journey price:", open_ticket("NRW", "ABE", "240524", "departing", 1, 0))
    print("Open return journey price:", open_return("NRW", "ABE", "240524", "250524", "departing", "departing", 1, 0))
    print("Round trip journey price:", round_trip("NRW", "ABE", "240524", "0215", "250524", "1030", "departing", "departing", 1, 0))
