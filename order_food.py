from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import os

# --- Get Credentials from Environment Variables ---
# These are set by GitHub Secrets in your repository settings
USERNAME = os.environ.get("KHANA_USERNAME")
PASSWORD = os.environ.get("KHANA_PASSWORD")

if not USERNAME or not PASSWORD:
    raise ValueError("KHANA_USERNAME and KHANA_PASSWORD environment variables not set in GitHub Secrets.")

# --- Chrome Options for Headless Mode in GitHub Actions ---
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')

# --- Initialize WebDriver ---
# This uses the headless options defined above
driver = webdriver.Chrome(options=options)

try:
    driver.get("https://khanakhazana.hilabs.com/")

    wait = WebDriverWait(driver, 20)
    try:
        username_input = wait.until(EC.presence_of_element_located((By.NAME, "userId")))
        password_input = driver.find_element(By.NAME, "password")
    except Exception as e:
        print("Could not find username/password fields.")
        # Saving page source for debugging is less useful in CI, but can be kept
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        raise e

    username_input.send_keys(USERNAME)
    password_input.send_keys(PASSWORD)

    login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
    login_button.click()
    print("Login successful.")

    # Wait for dashboard to load
    time.sleep(5)

    # --- ORDERING ACTIONS ---
    # 1. Click 'Non Veg' for Lunch (if enabled)
    try:
        lunch_nonveg_btn = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//p[contains(translate(text(), 'LUNCH', 'lunch'), 'lunch')]/following::span[contains(text(), 'Non Veg')][1]/parent::div[not(contains(@class, 'Mui-disabled'))]"
        )))
        lunch_nonveg_btn.click()
        print("Clicked 'Non Veg' for Lunch.")
        time.sleep(1)
    except Exception:
        print("Could not order 'Non Veg' for Lunch (likely disabled or already ordered).")

    # # 2. Click 'Non Veg' for Dinner (if enabled)
    # try:
    #     dinner_nonveg_btn = wait.until(EC.element_to_be_clickable((
    #         By.XPATH,
    #         "//p[contains(translate(text(), 'DINNER', 'dinner'), 'dinner')]/following::span[contains(text(), 'Non Veg')][1]/parent::div[not(contains(@class, 'Mui-disabled'))]"
    #     )))
    #     dinner_nonveg_btn.click()
    #     print("Clicked 'Non Veg' for Dinner.")
    #     time.sleep(1)
    # except Exception:
    #     print("Could not order 'Non Veg' for Dinner (likely disabled or already ordered).")

    # # 3. Click '+ Add' for Snacks
    # try:
    #     snacks_add_btn = wait.until(EC.element_to_be_clickable((
    #         By.XPATH,
    #         "//p[translate(normalize-space(text()), 'SNACKS', 'snacks')='snacks']/following::span[text()='+ Add'][1]/parent::div[@tabindex='0']"
    #     )))
    #     snacks_add_btn.click()
    #     print("Clicked '+ Add' for Snacks.")
    #     time.sleep(1)
    # except Exception:
    #     print("Could not add Snacks (maybe already added).")

    # 4. Click 'Confirm Order' button
    try:
        confirm_btn = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//button[.//text()[contains(.,'Confirm Order')]]"
        )))
        confirm_btn.click()
        print("Clicked 'Confirm Order' button.")
    except Exception:
        print("Could not click 'Confirm Order' button.")

    print("Order actions script finished.")

finally:
    time.sleep(5)
    driver.quit() 
