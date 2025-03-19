from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import json
import time
import sys
import os
import re
import codecs

def wait_for_element(driver, selector, timeout=20, by=By.CSS_SELECTOR):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
        return element
    except:
        return None

def scrape_bet9ja_booking(booking_code):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--ignore-ssl-errors")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(options=chrome_options)
    try:
        print(f"Opening Bet9ja website and searching for booking code: {booking_code}")
        driver.set_page_load_timeout(60)
        retry_count = 0
        max_retries = 3
        while retry_count < max_retries:
            try:
                driver.get("https://sports.bet9ja.com/")
                break
            except Exception as e:
                retry_count += 1
                print(f"Failed to load website (attempt {retry_count}/{max_retries}): {str(e)}")
                if retry_count < max_retries:
                    print("Retrying in 5 seconds...")
                    time.sleep(5)
                else:
                    raise Exception("Failed to load Bet9ja website after multiple attempts")
        
        time.sleep(10)
        print("Waiting for page to fully load...")
        
        try:
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
        except Exception as e:
            print(f"Scroll error: {str(e)}")
        
        input_selectors = [
            "input.input[placeholder='Booking Number']",
            "input[type='text'][placeholder='Booking Number']",
            "input[placeholder='Booking Number']",
            "input[placeholder*='Booking']",
            "input[placeholder*='booking']",
            "input.search-input",
            "input[type='text']"
        ]
        
        input_field = None
        for selector in input_selectors:
            print(f"Trying selector: {selector}")
            input_field = wait_for_element(driver, selector, timeout=5)
            if input_field:
                print(f"Found input field with selector: {selector}")
                break
        
        if not input_field:
            print("Input field not found with CSS selectors, trying XPath...")
            xpath_selectors = [
                "//input[@placeholder='Booking Number']",
                "//input[contains(@placeholder, 'Booking')]",
                "//input[contains(@placeholder, 'booking')]",
                "//input[@type='text']",
                "//form//input"
            ]
            
            for xpath in xpath_selectors:
                print(f"Trying XPath: {xpath}")
                input_field = wait_for_element(driver, xpath, timeout=5, by=By.XPATH)
                if input_field:
                    print(f"Found input field with XPath: {xpath}")
                    break
        
        if not input_field:
            print("Using JavaScript to find input field...")
            try:
                input_field = driver.execute_script("""
                    return document.querySelector('input[placeholder*="Booking"], input[placeholder*="booking"], input[type="text"]');
                """)
                if input_field:
                    print("Found input field using JavaScript")
            except Exception as e:
                print(f"JavaScript input field search error: {str(e)}")
        
        if not input_field:
            print("Taking screenshot for debugging...")
            driver.save_screenshot("page_load_debug.png")
            raise Exception("Could not find booking code input field")
        
        try:
            input_field.clear()
            time.sleep(1)
        except:
            pass
        
        try:
            input_field.send_keys(booking_code)
            print("Entered booking code")
        except Exception as e:
            print(f"Failed to enter booking code: {str(e)}")
            try:
                driver.execute_script(f"arguments[0].value = '{booking_code}';", input_field)
                print("Entered booking code using JavaScript")
            except Exception as js_e:
                print(f"JavaScript input failed: {str(js_e)}")
        
        button_selectors = [
            "button.btn-blue-s.ml10",
            "button.btn-blue-s",
            "button[type='submit']",
            "button:contains('Search')",
            "button:contains('Book')",
            "button:contains('Find')"
        ]
        
        book_button = None
        for selector in button_selectors:
            print(f"Trying button selector: {selector}")
            book_button = wait_for_element(driver, selector, timeout=5)
            if book_button:
                print(f"Found button with selector: {selector}")
                break
        
        if not book_button:
            print("Button not found with CSS selectors, trying XPath...")
            xpath_buttons = [
                "//button[contains(text(), 'Search')]",
                "//button[contains(text(), 'Book')]",
                "//button[contains(text(), 'Find')]",
                "//button[contains(@class, 'blue')]",
                "//button[@type='submit']",
                "//form//button"
            ]
            
            for xpath in xpath_buttons:
                print(f"Trying button XPath: {xpath}")
                book_button = wait_for_element(driver, xpath, timeout=5, by=By.XPATH)
                if book_button:
                    print(f"Found button with XPath: {xpath}")
                    break
        
        if not book_button:
            print("Using JavaScript to find button...")
            try:
                book_button = driver.execute_script("""
                    return document.querySelector('button.btn-blue-s, button[type="submit"], form button');
                """)
                if book_button:
                    print("Found button using JavaScript")
            except Exception as e:
                print(f"JavaScript button search error: {str(e)}")
        
        if not book_button:
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                try:
                    button_text = button.text.lower()
                    if "book" in button_text or "search" in button_text or "find" in button_text:
                        book_button = button
                        print(f"Found button with text: {button_text}")
                        break
                except:
                    continue
        
        if not book_button:
            print("Trying to submit form...")
            try:
                form = driver.find_element(By.TAG_NAME, "form")
                form.submit()
                print("Form submitted")
            except Exception as e:
                print(f"Form submission failed: {str(e)}")
                raise Exception("Could not find book button")
        else:
            print("Clicking search button")
            click_attempts = 0
            while click_attempts < 5:
                try:
                    book_button.click()
                    print("Button clicked successfully")
                    break
                except Exception as e:
                    click_attempts += 1
                    print(f"Click attempt {click_attempts} failed: {str(e)}")
                    time.sleep(2)
                    try:
                        driver.execute_script("arguments[0].click();", book_button)
                        print("Button clicked using JavaScript")
                        break
                    except Exception as js_e:
                        print(f"JavaScript click failed: {str(js_e)}")
                        try:
                            ActionChains(driver).move_to_element(book_button).click().perform()
                            print("Button clicked using ActionChains")
                            break
                        except Exception as ac_e:
                            print(f"ActionChains click failed: {str(ac_e)}")
        
        print("Waiting for game data to fully load...")
        time.sleep(15)
        
        for attempt in range(3):
            betslip_body = wait_for_element(driver, "div.betslip_body", timeout=15)
            if betslip_body:
                print("Betslip data found")
                break
            else:
                print(f"Betslip data not found, attempt {attempt+1}/3")
                if attempt < 2:
                    try:
                        print("Retrying search...")
                        if book_button and book_button.is_displayed():
                            driver.execute_script("arguments[0].click();", book_button)
                        time.sleep(15)
                    except Exception as e:
                        print(f"Retry click failed: {str(e)}")
        
        bet_data = {"booking_code": booking_code, "odds": "", "matches": []}
        
        print("Attempting to extract data...")
        bet_data = extract_data_all_methods(driver, booking_code)
        
        if not bet_data["matches"]:
            print("No matches found in bet data")
            driver.save_screenshot(f"{booking_code}_screen.png")
            simple_bet_data = extract_minimal_data(driver, booking_code)
            if simple_bet_data["matches"]:
                bet_data = simple_bet_data
        
        with open("bet.json", 'w', encoding='utf-8') as f:
            json.dump(bet_data, f, indent=4, ensure_ascii=False)
        
        print(f"Scraped data for booking code {booking_code} saved to bet.json")
        print(f"Found {len(bet_data['matches'])} matches")
        
        return bet_data
        
    except Exception as e:
        print(f"Error: {str(e)}")
        error_file = f"{booking_code}_error.png"
        driver.save_screenshot(error_file)
        print(f"Error screenshot saved to {error_file}")
        
        try:
            emergency_data = {
                "booking_code": booking_code,
                "odds": "",
                "matches": []
            }
            
            html_content = driver.page_source
            if "betslip" in html_content.lower() or "bet9ja" in html_content.lower():
                print("Attempting emergency data extraction...")
                emergency_data = extract_emergency_data(driver, booking_code)
                
                with open("bet.json", 'w', encoding='utf-8') as f:
                    json.dump(emergency_data, f, indent=4, ensure_ascii=False)
                print("Emergency data saved to bet.json")
                return emergency_data
        except:
            pass
            
        return None
    finally:
        driver.quit()

def extract_data_all_methods(driver, booking_code):
    bet_data = {
        "booking_code": booking_code,
        "odds": "",
        "matches": []
    }
    try:
        bet_data = extract_bet_data_with_soup(driver, booking_code)
        if not bet_data["matches"]:
            print("BeautifulSoup extraction failed, trying JavaScript method")
            js_data = extract_bet_data_javascript(driver, booking_code)
            if js_data["matches"]:
                bet_data = js_data
    except Exception as e:
        print(f"Data extraction error: {str(e)}")
    return bet_data

def extract_minimal_data(driver, booking_code):
    bet_data = {
        "booking_code": booking_code,
        "odds": "",
        "matches": []
    }
    try:
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        all_divs = soup.find_all('div')
        match_index = 1
        for div in all_divs:
            if div.get('class') and 'match' in ' '.join(div.get('class')):
                match_text = div.text.strip()
                if match_text and len(match_text) > 5:
                    match_data = {
                        "match_index": match_index,
                        "match": match_text[:100],
                        "odds": ""
                    }
                    for span in div.find_all('span'):
                        if span.get('class') and ('primary' in ' '.join(span.get('class')) or 'orange' in ' '.join(span.get('class'))):
                            match_data["odds"] = span.text.strip()
                            break
                    bet_data["matches"].append(match_data)
                    match_index += 1
    except Exception as e:
        print(f"Minimal extraction error: {str(e)}")
    return bet_data

def extract_emergency_data(driver, booking_code):
    bet_data = {
        "booking_code": booking_code,
        "odds": "",
        "matches": []
    }
    try:
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        all_elements = soup.find_all(['div', 'span', 'p', 'strong'])
        match_index = 1
        for element in all_elements:
            text = element.text.strip()
            if text and len(text) > 10 and ('vs' in text.lower() or 'v' in text.lower()):
                match_data = {
                    "match_index": match_index,
                    "match": text,
                    "odds": ""
                }
                next_element = element.find_next()
                if next_element:
                    next_text = next_element.text.strip()
                    if next_text and len(next_text) < 10:
                        try:
                            float(next_text.replace(',', '.'))
                            match_data["odds"] = next_text
                        except:
                            pass
                bet_data["matches"].append(match_data)
                match_index += 1
    except Exception as e:
        print(f"Emergency extraction error: {str(e)}")
    return bet_data

def extract_bet_data_javascript(driver, booking_code):
    bet_data = {
        "booking_code": booking_code,
        "odds": "",
        "matches": []
    }
    try:
        total_odds = driver.execute_script("""
            return document.querySelector('.betslip_info-odds')?.textContent.trim() || '';
        """)
        bet_data["odds"] = total_odds
        match_count = driver.execute_script("""
            return document.querySelectorAll('.betslip_match, [class*="match"]').length;
        """)
        for i in range(match_count):
            match_data = driver.execute_script(f"""
                const matches = document.querySelectorAll('.betslip_match, [class*="match"]');
                const match = matches[{i}];
                if (!match) return null;
                const matchData = {{
                    match_index: {i + 1},
                    match: '',
                    odds: ''
                }};
                matchData.match = match.querySelector('span.d-grow-1 strong')?.textContent.trim() || 
                                  match.querySelector('strong')?.textContent.trim() ||
                                  match.querySelector('[class*="head"]')?.textContent.trim() || 
                                  match.textContent.trim().substring(0, 100);
                matchData.odds = match.querySelector('[class*="odds"] span')?.textContent.trim() ||
                                match.querySelector('span[class*="primary"], span[class*="orange"]')?.textContent.trim() || '';
                return matchData;
            """)
            if match_data:
                bet_data["matches"].append(match_data)
    except Exception as e:
        print(f"JavaScript extraction error: {str(e)}")
    return bet_data

def extract_bet_data_with_soup(driver, booking_code):
    bet_data = {
        "booking_code": booking_code,
        "odds": "",
        "matches": []
    }
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    total_odds_element = soup.select_one("div.betslip_info-odds")
    if total_odds_element:
        bet_data["odds"] = total_odds_element.text.strip()
    try:
        match_elements = soup.select("div.betslip_match")
        if not match_elements:
            match_elements = soup.find_all("div", class_=lambda x: x and "match" in x)
        for match_index, match in enumerate(match_elements):
            match_data = {
                "match_index": match_index + 1,
                "match": "Unknown Match",
                "odds": ""
            }
            match_name_element = match.select_one("span.d-grow-1 strong")
            if match_name_element:
                match_data["match"] = match_name_element.text.strip()
            else:
                match_head = match.select_one("div.betslip_match-head, div[class*='match-head']")
                if match_head:
                    match_data["match"] = match_head.text.strip()
                else:
                    strong_element = match.select_one("strong")
                    if strong_element:
                        match_data["match"] = strong_element.text.strip()
            odds_element = match.select_one("div.betslip_match-odds span, span.txt-primary, span.txt-darkorange, span[class*='primary'], span[class*='orange']")
            if odds_element:
                match_data["odds"] = odds_element.text.strip()
            bet_data["matches"].append(match_data)
    except Exception as e:
        print(f"BeautifulSoup extraction error: {str(e)}")
    return bet_data

def clean_betting_data(input_data):
    """
    Clean betting data by:
    1. Removing incomplete matches (Unknown Match or empty odds)
    2. Standardizing match formats
    3. Handling duplicate matches
    4. Properly parsing odds values
    """
    # Extract basic info
    booking_code = input_data.get("booking_code", "")
    matches = input_data.get("matches", [])
    
    # Track processed matches to avoid duplicates
    processed_matches = {}
    
    for match in matches:
        match_index = match.get("match_index")
        match_name = match.get("match", "")
        odds_value = match.get("odds", "")
        
        # Skip invalid matches
        if match_name == "Unknown Match" or not odds_value:
            continue
            
        # Check for proper team format (Team1 - Team2)
        if " - " in match_name:
            # This is a full match with both teams
            key = match_name
            
            # For matches with score odds (like "0:0"), store as match results
            if ":" in odds_value and odds_value.replace(":", "").isdigit():
                match_type = "result"
            else:
                # Otherwise treat as betting odds
                try:
                    # Validate odds are numeric
                    float(odds_value.replace(",", "."))
                    match_type = "odds"
                except ValueError:
                    # Skip if odds aren't properly formatted
                    continue
                    
        else:
            # This is a single team entry - likely incomplete
            # Check if it's part of a full match we've seen
            found = False
            for full_match in processed_matches:
                if match_name in full_match:
                    # Update the existing entry if this has valid odds
                    try:
                        float(odds_value.replace(",", "."))
                        key = full_match
                        match_type = "odds"
                        found = True
                        break
                    except ValueError:
                        # Invalid odds format
                        continue
            
            # Skip if we couldn't associate with a full match
            if not found:
                continue
                
        # Store the best version of each match
        if key not in processed_matches or match_type not in processed_matches[key]:
            if key not in processed_matches:
                processed_matches[key] = {"match_index": match_index}
            
            processed_matches[key][match_type] = odds_value
    
    # Format the final cleaned matches
    cleaned_matches = []
    for match_name, details in processed_matches.items():
        cleaned_match = {
            "match_index": details.get("match_index"),
            "match": match_name,
        }
        
        # Add the appropriate odds information
        if "result" in details:
            cleaned_match["score"] = details["result"]
        if "odds" in details:
            cleaned_match["odds"] = details["odds"]
            
        cleaned_matches.append(cleaned_match)
    
    # Sort by match index
    cleaned_matches.sort(key=lambda x: x["match_index"])
    
    return {
        "booking_code": booking_code,
        "matches": cleaned_matches
    }

def process_betting_data(booking_code):
    """
    Main function to scrape and clean betting data
    """
    print("=" * 50)
    print(f"PROCESSING BOOKING CODE: {booking_code}")
    print("=" * 50)
    
    # Step 1: Scrape the betting data
    print("\nSTEP 1: SCRAPING DATA FROM BET9JA")
    bet_data = scrape_bet9ja_booking(booking_code)
    
    if not bet_data:
        print("Failed to scrape data. Exiting.")
        return False
    
    # Step 2: Clean the data
    print("\nSTEP 2: CLEANING BETTING DATA")
    try:
        cleaned_data = clean_betting_data(bet_data)
        
        # Save the cleaned data
        with open("real.json", "w", encoding="utf-8") as f:
            json.dump(cleaned_data, f, indent=4, ensure_ascii=False)
        
        print(f"Cleaned data saved to real.json with {len(cleaned_data['matches'])} valid matches")
        return True
        
    except Exception as e:
        print(f"Error cleaning data: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        booking_code = sys.argv[1]
    else:
        booking_code = input("Please enter the Bet9ja booking code: ")
    
    success = process_betting_data(booking_code)
    
    if success:
        print("\nProcess completed successfully!")
    else:
        print("\nProcess completed with errors. Check the logs above.")