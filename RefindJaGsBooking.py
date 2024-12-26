"""
JagsClubBook - Automated class booking system for Jags Sports Club.
This script automates the process of booking fitness classes through the club's web interface.
"""

import os
from datetime import datetime, date, timedelta
from typing import Dict, List
import logging
from dataclasses import dataclass
from enum import Enum
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
    TimeoutException
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
WAIT_TIMEOUT = 5
IMPLICIT_WAIT = 3
BASE_DELAY = 0.5

class URLs(str, Enum):
    HOME = 'https://jagssportsclub.gs-signature.cloud/Connect/MRMLogin.aspx'
    LOGIN = 'https://jagssportsclub.gs-signature.cloud/Connect/mrmLogin.aspx'

# The @ symbol is a decorator in Python
# @dataclass is a decorator that automatically adds generated special methods 
# such as __init__() and __repr__() to user-defined classes
# It reduces boilerplate code needed for classes that primarily store data
@dataclass
class Credentials:
    username: str
    password: str
    name: str

    @classmethod
    def from_env(cls) -> 'Credentials':
        """Load credentials from environment variables."""
        return cls(
            username=os.getenv('JAGS_USERNAME', '119423'),
            password=os.getenv('JAGS_PASSWORD', '5739'),
            name=os.getenv('JAGS_USER_NAME', 'Default')
        )

# Add new class to handle user-specific schedules
@dataclass
class User:
    credentials: Credentials
    class_schedule: Dict[int, List[str]]

# Define multiple users and their schedules
USERS = [
    User(
        credentials=Credentials(username='YOUR_USERNAME_1', password='YOUR_PASSWORD_1', name='User1'),
        class_schedule={
            0: ["Circuits", "Trx - Mon 6pm"],  # Monday
            1: ["Cyclecross"],  # Tuesday
            2: ['Hot Yoga - Wed 8pm'],  # Wednesday
            3: ["Boot Camp - Thurs 6.45am"],  # Thursday
            5: ['Cardio Tone - Sat 10.10am','Cardio Tone 10am','Cardio Tone']  # Saturday
        }
    ),
    User(
        credentials=Credentials(username='YOUR_USERNAME_2', password='YOUR_PASSWORD_2', name='User2'),
        class_schedule={
            1: ["Cyclecross"],  # Tuesday
            2: ['Hot Yoga - Wed 7pm'],  # Wednesday
            5: ['Cardio Tone']  # Saturday
        }
    )
]

class ClassBooker:
    def __init__(self, user: User):
        self.driver = self._setup_driver()
        self.credentials = user.credentials
        self.class_schedule = user.class_schedule
        self.wait = WebDriverWait(self.driver, WAIT_TIMEOUT)
        
    def _setup_driver(self) -> webdriver.Chrome:
        # The -> arrow indicates the return type annotation
        # In this case, it specifies that this method returns a webdriver.Chrome object
        """Setup and configure Chrome WebDriver."""
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-extensions')
        options.page_load_strategy = 'eager'
        # options.add_argument("--headless")  # Uncomment for headless mode
        
        # Cache ChromeDriver installation
        driver_path = ChromeDriverManager().install()
        driver = webdriver.Chrome(
            service=Service(driver_path),
            options=options
        )
        driver.implicitly_wait(IMPLICIT_WAIT)
        return driver

    def login(self):
        """Perform login to the website."""
        try:
            self.driver.get(URLs.LOGIN)
            self.driver.find_element(By.ID, "ctl00_MainContent_InputLogin").send_keys(self.credentials.username)
            self.driver.find_element(By.ID, "ctl00_MainContent_InputPassword").send_keys(self.credentials.password)
            self.driver.find_element(By.ID, "ctl00_MainContent_btnLogin").click()
        except Exception as e:
            logger.error(f"Login failed: {e}")
            raise

    def get_booking_dates(self) -> tuple[str, str]:
        """Calculate booking date range."""
        today = date.today()
        from_date = today
        to_date = today + timedelta(days=7)
        return (
            datetime.strftime(from_date, '%m-%d-%Y'),
            datetime.strftime(to_date, '%m-%d-%Y')
        )

    def open_advanced_search(self):
        """Open the advanced search menu."""
        try:
            # Reduced to most common selectors
            selectors = [
                "/html/body/form/div[3]/div/div/div/section/div[2]/div[1]/div[1]/div/div/div[2]/div[1]/h3/span/i",
                "//h3[contains(text(), 'Advanced Search')]"
            ]
            
            for selector in selectors:
                try:
                    element = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    element.click()
                    return  # Remove delay, not needed after successful click
                except TimeoutException:
                    continue
                
            logger.error("Could not find advanced search menu with any known selector")
            raise TimeoutException("Advanced search menu not found")
            
        except Exception as e:
            logger.error(f"Advanced search menu not accessible: {e}")
            # Re-raises the caught exception with original traceback
            raise

    def select_activity(self, activity_name: str):
        """Select an activity from the dropdown."""
        try:
            # Try multiple possible selectors for the Activity dropdown
            selectors = [
                "/html/body/form/div[3]/div/div/div/section/div[2]/div[1]/div[1]/div/div/div[2]/div[2]/div/div[3]/div/div/div/div[2]/select"
            ]
            
            user_name = self.credentials.name
            dropdown_wait = WebDriverWait(self.driver, WAIT_TIMEOUT * 2)
            
            for selector in selectors:
                try:
                    # Wait for dropdown to be present and have options
                    dropdown_element = dropdown_wait.until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    
                    # Additional wait for options to be populated
                    # Wait until dropdown has more than 1 option (first is usually blank)
                    # The lambda function takes a driver parameter 'd' and returns True when
                    # the dropdown has loaded with multiple options, False otherwise
                    dropdown_wait.until(
                        lambda d: len(Select(dropdown_element).options) > 1
                    )
                    
                    # Create a Select object from the dropdown element to interact with it
                    dropdown = Select(dropdown_element)
                    # Get a list of all available activity options from the dropdown menu
                    available_options = [o.text for o in dropdown.options]
                    
                    # Try to select the activity
                    try:
                        # Select the activity by visible text
                        dropdown.select_by_visible_text(activity_name)
                        logger.info(f"[{user_name}] Successfully selected activity: {activity_name}")
                        return
                    except NoSuchElementException:
                        # If exact match fails, try partial match
                        matches = [opt for opt in available_options if activity_name.lower() in opt.lower()]
                        if matches:
                            dropdown.select_by_visible_text(matches[0])
                            logger.warning(
                                f"[{user_name}] Used partial match for activity. "
                                f"Requested: '{activity_name}', Selected: '{matches[0]}'"
                            )
                            return
                        else:
                            # Log available options when no match is found
                            logger.warning(
                                f"[{user_name}] Activity '{activity_name}' not found in dropdown. "
                                f"Available activities: {', '.join(available_options)}"
                            )
                            continue
                            
                except TimeoutException:
                    logger.warning(f"[{user_name}] Timeout waiting for dropdown with selector: {selector}")
                    continue
                    
            # If we get here, no selector worked
            available_options_str = "No options found"
            for selector in selectors:
                try:
                    # Try to find the dropdown element using the selector
                    dropdown = Select(self.driver.find_element(By.XPATH, selector))
                    # Get a list of all available options from the dropdown menu
                    available_options = [o.text for o in dropdown.options]
                    # Join the available options into a string for logging
                    available_options_str = ', '.join(available_options)
                    break
                except:
                    continue
                    
            logger.error(
                f"[{user_name}] Failed to select activity '{activity_name}'. "
                f"Available options were: {available_options_str}"
            )
            raise NoSuchElementException(
                f"Activity '{activity_name}' not found in dropdown. "
                f"Available options: {available_options_str}"
            )
            
        except Exception as e:
            logger.error(f"[{user_name}] Failed to select activity {activity_name}: {str(e)}")
            raise

    def set_date_range(self, from_date: str, to_date: str):
        """Set the date range for booking search."""
        try:
            # Use XPath selectors for date inputs
            from_date_xpath = "/html/body/form/div[3]/div/div/div/section/div[2]/div[1]/div[1]/div/div/div[2]/div[2]/div/div[4]/div/div/div[1]/input"
            to_date_xpath = "/html/body/form/div[3]/div/div/div/section/div[2]/div[1]/div[1]/div/div/div[2]/div[2]/div/div[5]/div/div/div[1]/input"
            
            # Convert dates to datetime objects for comparison
            def parse_date(date_str: str) -> datetime:
                return datetime.strptime(date_str, '%m-%d-%Y')
            
            # Handle from date with retry logic
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    logger.info(f"Setting from date to: {from_date}")
                    from_date_input = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, from_date_xpath))
                    )
                    from_date_input.clear()
                    time.sleep(BASE_DELAY)
                    from_date_input.send_keys(from_date)
                    break
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed for from_date: {e}")
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(BASE_DELAY)

            time.sleep(BASE_DELAY * 2)
            
            # Handle to date with retry logic
            expected_date = parse_date(to_date)
            for attempt in range(max_attempts):
                try:
                    logger.info(f"Setting to date to: {to_date}")
                    to_date_input = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, to_date_xpath))
                    )
                    to_date_input.clear()
                    time.sleep(BASE_DELAY)
                    to_date_input.send_keys(to_date)
                    
                    # Get the actual value and convert for comparison
                    actual_value = to_date_input.get_attribute('value')
                    logger.info(f"To date value after setting: {actual_value}")
                    
                    # Try to parse the actual value in YYYY-MM-DD format
                    try:
                        actual_date = datetime.strptime(actual_value, '%Y-%m-%d')
                        if actual_date == expected_date:
                            logger.info("Date values match after normalization")
                            break
                    except ValueError:
                        # If parsing fails, try the original format
                        actual_date = parse_date(actual_value)
                        if actual_date == expected_date:
                            break
                    
                    raise ValueError(f"Date mismatch after normalization")
                    
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed for to_date: {e}")
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(BASE_DELAY)
            
            # Click away from the date inputs to close any calendars
            self.driver.find_element(By.TAG_NAME, "body").click()
            logger.info("Date range set successfully")
            
        except Exception as e:
            logger.error(f"Failed to set date range: {e}")
            raise

    def book_class(self, button_id: str):
        """Attempt to book a class using the specified button."""
        try:
            button = self.driver.find_element(By.ID, button_id)
            button.click()
            time.sleep(BASE_DELAY)
            
            confirm_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, 'ctl00_MainContent_btnBasket'))
            )
            confirm_button.click()
            logger.info(f"Successfully booked class with button {button_id}")
            
        except Exception as e:
            logger.error(f"Failed to book class: {e}")
            self.driver.get(URLs.HOME)

    def close(self):
        """Close the browser and clean up."""
        self.driver.quit()

    def submit_search(self):
        """Click the submit button to search for classes."""
        try:
            submit_xpath = "/html/body/form/div[3]/div/div/div/section/div[2]/div[1]/div[1]/div/div/div[2]/div[2]/div/div[9]/div/div/button"
            
            # Wait for and click the submit button
            submit_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, submit_xpath))
            )
            submit_button.click()
            logger.info("Search submitted successfully")
            
        except Exception as e:
            logger.error(f"Failed to submit search: {e}")
            raise

    def find_and_click_booking_button(self):
        """Find and click the booking button if a slot is available."""
        try:
            booking_button_xpath = "/html/body/form/div[3]/div/div/div/section/div[2]/div[1]/div[3]/div/div/div[1]/div[2]/div[2]/div[1]/div/a[1]"
            
            # Wait for the button and check if it's clickable
            booking_button = self.wait.until(
                EC.presence_of_element_located((By.XPATH, booking_button_xpath))
            )
            
            if booking_button.is_displayed() and booking_button.is_enabled():
                logger.info("Found available booking slot")
                booking_button.click()
                logger.info("Successfully clicked booking button")
                return True
            else:
                logger.warning("Booking button found but not clickable - slot might be full")
                return False
            
        except TimeoutException:
            logger.warning("No booking button found - slot might be full or not available")
            return False
        except Exception as e:
            logger.error(f"Error while trying to click booking button: {e}")
            raise

    def confirm_booking(self):
        """Handle the final booking confirmation steps."""
        try:
            # First book button on the new page
            first_book_xpath = "/html/body/form/div[3]/div/div/div/section/div/div[2]/div[1]/div[5]/div[2]/table/tbody/tr[1]/td/input"
            
            # Wait for button presence first
            first_book_button = self.wait.until(
                EC.presence_of_element_located((By.XPATH, first_book_xpath))
            )
            
            # Check if button is enabled and has the correct attributes
            if not first_book_button.is_enabled():
                logger.warning("First book button is present but disabled - class might be full")
                return False
            
            # Check for any attributes that might indicate the button is disabled
            button_class = first_book_button.get_attribute('class')
            if 'disabled' in button_class or 'grey' in button_class:
                logger.warning("First book button is greyed out - class might be full")
                return False
            
            # Try to click the button
            try:
                first_book_button.click()
                logger.info("Clicked first book button")
            except ElementClickInterceptedException:
                logger.warning("First book button not clickable - class might be full")
                return False
            
            # Final confirmation button
            final_book_xpath = "/html/body/form/div[3]/div/div/div/div/div/div/div[3]/input[1]"
            try:
                final_book_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, final_book_xpath))
                )
                final_book_button.click()
                logger.info("Clicked final confirmation button")
                return True
                
            except TimeoutException:
                logger.warning("Final confirmation button not found or not clickable")
                return False
            
        except TimeoutException:
            logger.warning("Booking confirmation buttons not found or not clickable")
            return False
        except Exception as e:
            logger.error(f"Error during booking confirmation: {e}")
            # Try to get additional information about the button state
            try:
                button = self.driver.find_element(By.XPATH, first_book_xpath)
                logger.error(f"Button state - Enabled: {button.is_enabled()}, "
                            f"Displayed: {button.is_displayed()}, "
                            f"Class: {button.get_attribute('class')}")
            except:
                pass
            raise

    def return_to_home(self):
        """Return to home page and prepare for next booking."""
        try:
            # Click the Home link in the navigation bar
            home_xpath = "/html/body/form/div[3]/header/nav/div/div[2]/ul/li[1]/a/span"
            home_link = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, home_xpath))
            )
            home_link.click()
            logger.info("Clicked Home link")
            
            # Wait for page to load and expand Advanced Search
            time.sleep(BASE_DELAY * 2)  # Give page time to load
            self.open_advanced_search()
            logger.info("Returned to home page and expanded Advanced Search")
            
        except Exception as e:
            logger.error(f"Failed to return to home page: {e}")
            # Fallback to direct URL if clicking fails
            try:
                self.driver.get(URLs.HOME)
                time.sleep(BASE_DELAY * 2)
                self.open_advanced_search()
                logger.info("Successfully returned to home using direct URL")
            except Exception as fallback_error:
                logger.error(f"Fallback to home page failed: {fallback_error}")
                raise

    def book_classes_for_day(self, day: int, classes: List[str]):
        """Book multiple classes for a given day."""
        from_date, to_date = self.get_booking_dates()
        user_name = self.credentials.name
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_name = days[day]
        
        logger.info(f"[{user_name}] Attempting to book {len(classes)} classes for {day_name}")
        for index, activity in enumerate(classes, 1):
            try:
                logger.info(f"[{user_name}] Booking class {index} of {len(classes)}: {activity} for {day_name}")
                
                self.open_advanced_search()
                try:
                    self.select_activity(activity)
                except NoSuchElementException as e:
                    logger.warning(
                        f"[{user_name}] Skipping {activity} as it's not available in the dropdown. "
                        f"Moving to next class."
                    )
                    self.return_to_home()
                    continue
                    
                self.set_date_range(from_date, to_date)
                self.submit_search()
                
                if self.find_and_click_booking_button():
                    logger.info(f"[{user_name}] Successfully initiated booking for {activity} on {day_name}")
                    if self.confirm_booking():
                        logger.info(f"[{user_name}] Successfully completed booking for {activity} on {day_name}")
                        if index < len(classes):
                            logger.info(f"[{user_name}] Returning to home to book next class")
                            self.return_to_home()
                    else:
                        logger.warning(f"[{user_name}] Class {activity} on {day_name} appears to be full or not available for booking")
                        self.return_to_home()
                else:
                    logger.warning(f"[{user_name}] No available slots for {activity} on {day_name}")
                    self.return_to_home()
                    
            except Exception as e:
                logger.error(f"[{user_name}] Failed to book {activity} on {day_name}: {e}")
                try:
                    self.return_to_home()
                except:
                    logger.error(f"[{user_name}] Failed to return to home after error")
                    try:
                        self.driver.get(URLs.HOME)
                        time.sleep(BASE_DELAY * 2)
                    except:
                        logger.error(f"[{user_name}] Failed to navigate to home page via URL")
                continue

def main():
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    current_day = date.today().weekday()
    current_day_name = days[current_day]

    # Try booking for each user
    for user in USERS:
        logger.info(f"Starting bookings for {user.credentials.name} ({user.credentials.username})")
        booker = ClassBooker(user)
        
        try:
            booker.login()
            
            if current_day in user.class_schedule:
                classes_for_today = user.class_schedule[current_day]
                logger.info(f"[{user.credentials.name}] Found {len(classes_for_today)} classes to book for {current_day_name}")
                booker.book_classes_for_day(current_day, classes_for_today)
            else:
                logger.info(f"[{user.credentials.name}] No classes scheduled for {current_day_name}")
                
        except Exception as e:
            logger.error(f"An error occurred for {user.credentials.name}: {e}")
        finally:
            booker.close()
            logger.info(f"Completed bookings for {user.credentials.name}")
            time.sleep(BASE_DELAY * 2)  # Small delay between users

if __name__ == "__main__":
    main()