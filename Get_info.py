from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv
import os
import time

load_dotenv()

# CONFIG
canvas_login_url = "https://canvas.tamu.edu/"
canvas_dashboard_url = "https://canvas.tamu.edu/"
login_url = "https://canvas.tamu.edu/"
your_email = os.getenv('EMAIL')
your_password = os.getenv("PASSWORD")

# START BROWSER
driver = webdriver.Chrome()

driver.get(canvas_login_url)  
time.sleep(1)

# Manual login
driver.find_element(By.ID, "i0116").send_keys(your_email)
wait = WebDriverWait(driver, 10)
next_button = wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
next_button.click()
time.sleep(1.5)
driver.find_element(By.ID, "i0118").send_keys(your_password)
next_button = wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
next_button.click()

time.sleep(4)  # wait for page to load

print("Waiting for you to approve DUO push...")
try:
    WebDriverWait(driver, 60).until(
        lambda d: (
            "https://login.microsoftonline.com/common/federation/OAuth2ClaimsProvider" in d.current_url or
            len(d.find_elements(By.ID, "trust-browser-button")) > 0
        )
    )
    print("✅ DUO approved and Canvas loaded!")

except TimeoutException:
    print("❌ Timed out waiting for post-DUO page.")
except Exception as e:
    print(f"Error during DUO wait: {e}")

time.sleep(1)
next_button = wait.until(EC.element_to_be_clickable((By.ID, "trust-browser-button")))
next_button.click()

time.sleep(1)
next_button = wait.until(EC.element_to_be_clickable((By.ID, "KmsiCheckboxField")))
next_button.click()

next_button = wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
next_button.click()

# Scrape assignments
print("Scraping assignments...")
time.sleep(3)
while True:
    try:
        driver.get(canvas_dashboard_url)
        time.sleep(2)
        
        cards = driver.find_elements(By.CLASS_NAME, "ic-DashboardCard")
        course_links = []
        for card in cards:
            try:
                course_name = card.get_attribute("aria-label")
                link = card.find_element(By.CLASS_NAME, "ic-DashboardCard__link").get_attribute("href")
                course_links.append((course_name, link))
            except Exception as e:
                print("⚠️ Could not extract course info:", e)

        # Visit each course and scrape assignments
        for course_name, link in course_links:
            print(f"\n📘 Course name: {course_name}")
            driver.get(link + "/assignments")
            time.sleep(5)

            try:
                assignments_big = driver.find_elements(By.CLASS_NAME, "ToDoSidebarItem__Title")
            except Exception as e:
                print("❌ Failed to find To-Do items:", e)
                assignments_big = []

            if not assignments_big:
                print("   ℹ️ No assignments found.")
            else:
                for assignment_div in assignments_big:
                    try:
                        try:
                            link = assignment_div.find_element(By.TAG_NAME, "a")
                        except Exception as e:
                            print("   ❌ Could not find <a> tag in assignment div:", e)
                            continue

                        try:
                            label = link.get_attribute("aria-label")
                        except Exception as e:
                            print("   ❌ Could not get aria-label from link:", e)
                            label = None

                        if label:
                            print(f"   📝 {label}")
                        else:
                            print("   ⚠️ Assignment found but no label.")
                    except Exception as e:
                        print(f"   ❌ Unexpected error processing assignment div:", e)

        print("✅ Complete Scrape")

    except Exception as e:
        print("❌ Error during scraping loop:", e)

    time.sleep(3600)

