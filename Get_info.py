from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv
import os
import pickle
import time

load_dotenv()
cookie_path = "cookies.pkl"

# CONFIG
canvas_login_url = "https://canvas.tamu.edu/"  # change this
canvas_dashboard_url = "https://canvas.tamu.edu/"   # change this too
login_url = "https://login.microsoftonline.com/"
your_email = os.getenv('EMAIL')
your_password = os.getenv("PASSWORD")  # ⚠️ not secure — better to prompt or use environment variable

# START BROWSER
driver = webdriver.Chrome()  # Make sure chromedriver is in PATH

# Line ~23 in your script
driver.get("https://canvas.tamu.edu/")  
time.sleep(2)  # wait for page to load

# ----- INSERT COOKIE LOADING CODE HERE (starts) -----
if os.path.exists(cookie_path):
    with open(cookie_path, "rb") as file:
        cookies = pickle.load(file)
    for cookie in cookies:
        if 'expiry' in cookie:
            del cookie['expiry']
        try:
            if "login.microsoftonline.com" in cookie.get('domain', ''):
                driver.add_cookie(cookie)
        except Exception as e:
            print(f"Skipping cookie due to error: {e}")
    driver.refresh()
    time.sleep(3)

#Chekcing to see if any cookies are present to skip past the verificatyion stuff
if os.path.exists(cookie_path):
    with open(cookie_path, "rb") as file:
        cookies = pickle.load(file)
    for cookie in cookies:
        if 'expiry' in cookie:
            del cookie['expiry']
        # Add only cookies valid for microsoft login domain to avoid domain errors
        if "login.microsoftonline.com" in cookie.get('domain', ''):
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                print(f"Skipping cookie due to error: {e}")
    driver.get(login_url)  # Refresh after loading cookies
    time.sleep(3)

# Check if logged in by looking for a known element
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "ic-DashboardCard"))
    )
    print("Logged in using cookies!")
except:

# Fill in login form — update these selectors if needed
    driver.find_element(By.ID, "i0116").send_keys(your_email)
    wait = WebDriverWait(driver, 10)
    next_button = wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
    next_button.click()
    time.sleep(1)
    driver.find_element(By.ID, "i0118").send_keys(your_password)
    wait = WebDriverWait(driver, 10)
    next_button = wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
    next_button.click()

    # You may need to manually approve Duo/2FA here
    print("Waiting for you to approve DUO push...")
    try:
        WebDriverWait(driver, 60).until(
            lambda d: (
                "https://login.microsoftonline.com/common/federation/OAuth2ClaimsProvider" in d.current_url or
                len(d.find_elements(By.ID, "trust-browser-button")) > 0  # Replace "dashboard" with actual ID
            )
        )
        print("✅ DUO approved and Canvas loaded!")
    except TimeoutException:
        print("❌ Timed out waiting for post-DUO page.")


    time.sleep(1)

    wait = WebDriverWait(driver, 10)
    next_button = wait.until(EC.element_to_be_clickable((By.ID, "trust-browser-button")))
    next_button.click()

    time.sleep(1)

    wait = WebDriverWait(driver, 10)
    next_button = wait.until(EC.element_to_be_clickable((By.ID, "KmsiCheckboxField")))
    next_button.click()

    wait = WebDriverWait(driver, 10)
    next_button = wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
    next_button.click()

# STEP 3: Try to find assignment links/due dates
print("Scraping assignments...")
try:
    cards = driver.find_elements(By.CLASS_NAME, "ic-DashboardCard")
    for card in cards:
        try:
            aria_label = card.get_attribute("aria-label")
            print(f"📘 Course name: {aria_label}")

            # Optional: navigate into course page and scrape assignments there
            open_assignment = card.find_element(By.CLASS_NAME,"ic-DashboardCard__link")
            open_assignment.click()
            link = card.find_element(By.TAG_NAME, "a").get_attribute("href")
            driver.get(link + "/assignments")
            time.sleep(5)

            assignments = driver.find_elements(By.CLASS_NAME, "ig-title")
            for a in assignments:
                name = a.text
                try:
                    due = a.find_element(By.XPATH, "../../..").find_element(By.CLASS_NAME, "assignment-date").text
                except:
                    due = "No due date"
                print(f"   📝 {name} — {due}")

        except Exception as e:
            print("Error loading course:", e)
except Exception as e:
    print("Error during scraping:", e)
finally:
    driver.quit()
