from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dotenv import load_dotenv
import os
import time
from typing import List, Tuple, Optional

class CanvasScraper:
    def __init__(self):
        load_dotenv()
        self.canvas_url = "https://canvas.tamu.edu/"
        self.email = os.getenv('EMAIL')
        self.password = os.getenv('PASSWORD')
        self.driver = None
        self.wait = None
        
    def setup_driver(self) -> bool:
        """Initialize the Chrome driver and WebDriverWait"""
        try:
            self.driver = webdriver.Chrome()
            self.wait = WebDriverWait(self.driver, 10)
            return True
        except Exception as e:
            print(f"❌ Failed to setup driver: {e}")
            return False
        
    def login(self) -> bool:
        """Handle the complete login process including DUO authentication"""
        try:
            self.driver.get(self.canvas_url)
            time.sleep(1)
            
            # Enter email
            self.driver.find_element(By.ID, "i0116").send_keys(self.email)
            self._click_next_button()
            
            # Enter password
            time.sleep(1.5)
            self.driver.find_element(By.ID, "i0118").send_keys(self.password)
            self._click_next_button()
            
            # Handle DUO authentication
            if not self._handle_duo_auth():
                return False
                
            # Complete login process
            self._complete_login()
            return True
            
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False
    
    def _click_next_button(self):
        """Helper method to click the next button"""
        next_button = self.wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
        next_button.click()
    
    def _handle_duo_auth(self) -> bool:
        """Handle DUO authentication process"""
        time.sleep(4)
        print("Waiting for you to approve DUO push...")
        
        try:
            WebDriverWait(self.driver, 60).until(
                lambda d: (
                    "https://login.microsoftonline.com/common/federation/OAuth2ClaimsProvider" in d.current_url or
                    len(d.find_elements(By.ID, "trust-browser-button")) > 0
                )
            )
            print("✅ DUO approved and Canvas loaded!")
            return True
            
        except TimeoutException:
            print("❌ Timed out waiting for post-DUO page.")
            return False
        except Exception as e:
            print(f"❌ Error during DUO wait: {e}")
            return False
    
    def _complete_login(self):
        """Complete the login process after DUO authentication"""
        time.sleep(1)
        
        # Trust browser
        trust_button = self.wait.until(EC.element_to_be_clickable((By.ID, "trust-browser-button")))
        trust_button.click()
        
        # Check "Stay signed in"
        time.sleep(1)
        checkbox = self.wait.until(EC.element_to_be_clickable((By.ID, "KmsiCheckboxField")))
        checkbox.click()
        
        # Final next button
        self._click_next_button()
    
    def get_course_links(self) -> List[Tuple[str, str]]:
        """Extract course names and links from dashboard"""
        self.driver.get(self.canvas_url)
        time.sleep(2)
        
        course_links = []
        try:
            cards = self.driver.find_elements(By.CLASS_NAME, "ic-DashboardCard")
            
            for card in cards:
                try:
                    course_name = card.get_attribute("aria-label")
                    link = card.find_element(By.CLASS_NAME, "ic-DashboardCard__link").get_attribute("href")
                    if course_name and link:
                        course_links.append((course_name, link))
                except Exception as e:
                    print(f"⚠️ Could not extract course info: {e}")
                    
        except Exception as e:
            print(f"❌ Error getting course links: {e}")
            
        return course_links
    
    def scrape_course_assignments(self, course_name: str, course_link: str):
        """Scrape assignments for a specific course"""
        print(f"\n📘 Course name: {course_name}")
        
        try:
            self.driver.get(f"{course_link}/assignments")
            time.sleep(5)
            
            assignments = self.driver.find_elements(By.CLASS_NAME, "ToDoSidebarItem__Title")
            
            if not assignments:
                print("   ℹ️ No assignments found.")
                return
                
            for assignment_div in assignments:
                assignment_info = self._extract_assignment_info(assignment_div)
                if assignment_info:
                    label, date = assignment_info
                    print(f"   📝 {label} — 📅 {date}")
                    
        except Exception as e:
            print(f"❌ Error scraping assignments for {course_name}: {e}")
    
    def _extract_assignment_info(self, assignment_div) -> Optional[Tuple[str, str]]:
        """Extract assignment label and due date from assignment div"""
        try:
            # Get assignment link and label
            link = assignment_div.find_element(By.TAG_NAME, "a")
            label = link.get_attribute("aria-label")
            
            if not label:
                return None
                
            # Get due date
            parent = assignment_div.find_element(By.XPATH, "../..")
            info_items = parent.find_elements(By.CLASS_NAME, "css-7361do-view--inlineBlock-inlineListItem")
            
            date = "No due date found"
            for item in info_items:
                text = item.text.strip()
                if "at" in text:  # Look for date format like "Jul 10 at 11:59pm"
                    date = text
                    break
                    
            return (label, date)
            
        except NoSuchElementException:
            print("   ❌ Could not find required elements in assignment div")
            return None
        except Exception as e:
            print(f"   ❌ Error extracting assignment info: {e}")
            return None
    
    def scrape_all_assignments(self):
        """Main method to scrape assignments from all courses"""
        print("Scraping assignments...")
        time.sleep(3)
        
        try:
            course_links = self.get_course_links()
            
            for course_name, link in course_links:
                self.scrape_course_assignments(course_name, link)
                
            print("✅ Complete Scrape")
            
        except Exception as e:
            print(f"❌ Error during scraping: {e}")
    
    def run_continuous_scrape(self, interval_minutes: int = 1):
        """Run the scraper continuously with specified interval"""
        if not self.setup_driver():
            return
            
        if not self.login():
            self.cleanup()
            return
            
        while True:
            try:
                self.scrape_all_assignments()
                print(f"⏰ Waiting {interval_minutes} minute(s) before next scrape...")
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                print("\n🛑 Scraping stopped by user")
                break
            except Exception as e:
                print(f"❌ Error in main loop: {e}")
                time.sleep(60)  # Wait before retrying
                
        self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
            print("🧹 Browser closed")

def main():
    scraper = CanvasScraper()
    scraper.run_continuous_scrape()

if __name__ == "__main__":
    main()
