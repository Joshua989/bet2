import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import difflib
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
def load_json_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {file_path}.")
        return None
def string_similarity(a, b):
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()
def set_zoom(driver, zoom_level):
    driver.execute_script(f"document.body.style.zoom = '{zoom_level}%'")
def scroll_page(driver, delay=0.5, step=300):
    page_height = driver.execute_script("return document.body.scrollHeight")
    current_position = 0
    while current_position < page_height:
        driver.execute_script(f"window.scrollTo(0, {current_position});")
        current_position += step
        time.sleep(delay)
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(delay)
def scroll_to_bottom(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
def find_match(driver, match_name):
    print(f"Looking for match: {match_name}")
    scroll_page(driver)
    try:
        team_elements = driver.find_elements(By.CSS_SELECTOR, "div.team")
        matches = []
        for i in range(0, len(team_elements), 2):
            if i + 1 < len(team_elements):
                home_team = team_elements[i].text.strip()
                away_team = team_elements[i + 1].text.strip()
                full_match = f"{home_team} - {away_team}"
                similarity = string_similarity(full_match, match_name)
                matches.append((full_match, similarity, i // 2))
        matches.sort(key=lambda x: x[1], reverse=True)
        if matches and matches[0][1] > 0.6:
            print(f"Found match: {matches[0][0]} with similarity score {matches[0][1]}")
            match_index = matches[0][2] * 2
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", team_elements[match_index])
            time.sleep(1)
            return team_elements[match_index]
        else:
            print(f"No match found for {match_name}")
            return None
    except Exception as e:
        print(f"Error finding match: {e}")
        return None
def find_closest_odds(driver, target_odds):
    try:
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        target_odds = float(target_odds)
        market_section = driver.find_element(By.CSS_SELECTOR, "div.m-table.market-content")
        print("Found market content section")
        odds_elements = market_section.find_elements(By.CSS_SELECTOR, "div.m-outcome em:nth-child(2)")
        if not odds_elements:
            print("No odds elements found in the top section, trying alternative selector")
            odds_elements = market_section.find_elements(By.CSS_SELECTOR, "div.m-table-cell.m-outcome em:nth-child(2)")
        print(f"Found {len(odds_elements)} odds elements")
        closest_element = None
        closest_diff = float('inf')
        for element in odds_elements:
            try:
                odds_text = element.text.strip()
                print(f"Found odds: {odds_text}")
                odds_value = float(odds_text)
                diff = abs(odds_value - target_odds)
                if diff < closest_diff:
                    closest_diff = diff
                    closest_element = element
            except ValueError:
                print(f"Could not convert '{element.text}' to float")
                continue
        if closest_element and closest_diff < 0.5:
            print(f"Best matching odds: {closest_element.text} (target was {target_odds}, difference: {closest_diff})")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", closest_element)
            time.sleep(1)
            return closest_element
        else:
            print(f"No suitable odds found close to {target_odds}")
            return None
    except Exception as e:
        print(f"Error finding odds: {e}")
        import traceback
        traceback.print_exc()
        return None
def click_betslip_button(driver):
    try:
        print("Looking for betslip button at the bottom of the page...")
        scroll_to_bottom(driver)
        time.sleep(2)
        specific_selector = "div[data-op='betslip-multi-min-count'].bet-count-wrapper"
        wait = WebDriverWait(driver, 10)
        betslip_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, specific_selector)))
        print("Found betslip button, preparing to click...")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", betslip_button)
        time.sleep(1)
        try:
            driver.execute_script("arguments[0].click();", betslip_button)
            print("Clicked betslip button using JavaScript")
        except Exception as js_error:
            print(f"JavaScript click failed: {js_error}, trying actions chain")
            actions = ActionChains(driver)
            actions.move_to_element(betslip_button).click().perform()
            print("Clicked betslip button using action chains")
        time.sleep(2)
        return True
    except Exception as e:
        print(f"Error clicking betslip button: {e}")
        try:
            print("Trying alternative betslip button selector...")
            span_selector = "div.bet-count-wrapper span.real-theme"
            span_element = driver.find_element(By.CSS_SELECTOR, span_selector)
            if span_element:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", span_element)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", span_element)
                print("Clicked betslip button span using JavaScript")
                time.sleep(2)
                return True
        except Exception as alt_error:
            print(f"Alternative selector failed: {alt_error}")
        return False
def click_book_bet_button(driver):
    try:
        print("Looking for Book Bet button...")
        wait = WebDriverWait(driver, 10)
        book_bet_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-op='betslip-book-bet-button']")))
        print("Found Book Bet button")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", book_bet_button)
        time.sleep(1)
        try:
            driver.execute_script("arguments[0].click();", book_bet_button)
            print("Clicked Book Bet button using JavaScript")
        except Exception as js_error:
            print(f"JavaScript click failed: {js_error}, trying regular click")
            book_bet_button.click()
            print("Clicked Book Bet button using regular click")
        time.sleep(3)
        return True
    except Exception as e:
        print(f"Error clicking Book Bet button: {e}")
        import traceback
        traceback.print_exc()
        return False
def get_booking_code(driver):
    try:
        print("Looking for booking code...")
        wait = WebDriverWait(driver, 10)
        code_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span[data-op='share-booking-code-dialog-code-text']")))
        booking_code = code_element.text.strip()
        print(f"BOOKING CODE: {booking_code}")
        return booking_code
    except Exception as e:
        print(f"Error getting booking code: {e}")
        import traceback
        traceback.print_exc()
        return None
def process_matches(json_data):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    try:
        driver.get("https://mobile.sportybet.com/ng/m/sport/football/today?sort=0")
        time.sleep(5)
        set_zoom(driver, 25)
        time.sleep(1)
        successful_bets = 0
        for match_data in json_data.get("matches", []):
            match_name = match_data.get("match")
            target_odds = match_data.get("odds")
            print(f"\nProcessing match: {match_name} with target odds: {target_odds}")
            match_element = find_match(driver, match_name)
            if match_element:
                try:
                    match_element.click()
                    print("Clicked on match, waiting for details page...")
                    time.sleep(3)
                    set_zoom(driver, 25)
                    time.sleep(1)
                    odds_element = find_closest_odds(driver, target_odds)
                    if odds_element:
                        try:
                            driver.execute_script("arguments[0].click();", odds_element)
                            print("Clicked on odds using JavaScript")
                            successful_bets += 1
                        except Exception as e:
                            print(f"JavaScript click failed: {e}, trying regular click")
                            odds_element.click()
                            print("Clicked on odds using regular click")
                            successful_bets += 1
                        time.sleep(2)
                    print("Navigating back to main page")
                    driver.get("https://mobile.sportybet.com/ng/m/sport/football/today?sort=0")
                    time.sleep(3)
                    set_zoom(driver, 25)
                    time.sleep(1)
                except Exception as e:
                    print(f"Error processing match {match_name}: {e}")
                    import traceback
                    traceback.print_exc()
                    driver.get("https://mobile.sportybet.com/ng/m/sport/football/today?sort=0")
                    time.sleep(3)
                    set_zoom(driver, 25)
                    time.sleep(1)
            else:
                print(f"Match {match_name} not found, continuing to next match")
        if successful_bets > 0:
            print(f"\nSuccessfully added {successful_bets} bets. Looking for betslip button...")
            driver.get("https://mobile.sportybet.com/ng/m/sport/football/today?sort=0")
            time.sleep(3)
            set_zoom(driver, 25)
            time.sleep(1)
            if click_betslip_button(driver):
                print("Successfully clicked on betslip button")
                time.sleep(3)
                if click_book_bet_button(driver):
                    print("Successfully clicked Book Bet button")
                    time.sleep(3)
                    booking_code = get_booking_code(driver)
                    if booking_code:
                        print(f"\n========================")
                        print(f"BOOKING CODE: {booking_code}")
                        print(f"========================\n")
                    else:
                        print("Failed to get booking code")
                else:
                    print("Failed to click Book Bet button")
            else:
                print("Failed to click on betslip button")
        else:
            print("No bets were successfully added, skipping betslip button click")
    except Exception as e:
        print(f"An error occurred during processing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        time.sleep(10)
        print("Closing browser")
        driver.quit()
if __name__ == "__main__":
    json_data = load_json_data("real.json")
    if json_data:
        process_matches(json_data)
    else:
        print("Failed to load JSON data. Script terminated.")