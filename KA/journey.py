import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Install chromedriver
chromedriver_autoinstaller.install()

# Function to build the URL from user input
def get_user_input():
    base_url = "https://www.nationalrail.co.uk/journey-planner/"
    print("Please enter your journey parameters (see example values in parentheses):")
    type_journey = input("Type of journey (single/return) [e.g., single]: ")
    origin = input("Origin station code [e.g., ABW for Abbey Wood]: ")
    destination = input("Destination station code [e.g., ABE for Aber]: ")
    leaving_type = input("Leaving type (departing/arriving) [e.g., departing]: ")
    leaving_date = input("Leaving date (yymmdd) [e.g., 200424]: ")
    leaving_hour = input("Leaving hour (HH) [e.g., 02]: ")
    leaving_min = input("Leaving minute (MM) [e.g., 15]: ")
    adults = input("Number of adults [e.g., 1]: ")
    extra_time = input("Extra time (minutes, optional, default is 0) [e.g., 0]: ")
    extra_time = extra_time if extra_time else "0"

    # Construct the URL with input parameters
    url = f"{base_url}?type={type_journey}&origin={origin}&destination={destination}&leavingType={leaving_type}&leavingDate={leaving_date}&leavingHour={leaving_hour}&leavingMin={leaving_min}&adults={adults}&extraTime={extra_time}"
    
    if type_journey == "return":
        return_type = input("Return type (departing/arriving) [e.g., departing]: ")
        return_date = input("Return date (yymmdd) [e.g., 200425]: ")
        return_hour = input("Return hour (HH) [e.g., 10]: ")
        return_min = input("Return minute (MM) [e.g., 30]: ")
        # Append return journey details to the URL
        url += f"&returnType={return_type}&returnDate={return_date}&returnHour={return_hour}&returnMin={return_min}"

    return url + "#O"

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument('--headless')  # Ensure GUI is off
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# Set up the webdriver
driver = webdriver.Chrome(options=chrome_options)

# Get user input for URL
url = get_user_input()

# Navigate to the page
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
            prices.append(float(price))
            print(f"Found price: £{price}")
        except Exception as e:
            print("Not Found")

# Clean up: close the browser
driver.quit()

# Handling to find the lowest price
if prices:
    lowest_price = min(prices)
    print(f"The lowest cost for your journey is: £{lowest_price:.2f}")
else:
    print("No prices were found, please check your input parameters and try again.")
