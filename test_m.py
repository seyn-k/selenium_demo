import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import shutil
import logging
import time

user_credentials = [
    ("lookscool", "Senthil@2004"),
    ("senthil", "senthil@2004"),
    ("sugan", "sugan@2004")
]

@pytest.mark.parametrize("userna,passw", user_credentials)
def test_demoblaze_parallel(userna, passw):
    log_file = f"logs/{userna}.log"
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    binary_path = shutil.which("firefox")
    options = Options()
    options.binary = FirefoxBinary(binary_path)
    driver = webdriver.Firefox(options=options)
    driver.maximize_window()

    try:
        logging.info("Opening DemoBlaze")
        driver.get("https://www.demoblaze.com/index.html")

        assert "STORE" in driver.title, "Page title does not contain 'STORE'"
        logging.info("Page title verified")

        logging.info("Clicking on Sign Up")
        driver.find_element(By.ID, 'signin2').click()
        time.sleep(1)
        driver.find_element(By.ID, 'sign-username').clear()
        driver.find_element(By.ID, 'sign-username').send_keys(userna)
        driver.find_element(By.ID, 'sign-password').clear()
        driver.find_element(By.ID, 'sign-password').send_keys(passw)
        driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[3]/button[2]').click()

        try:
            WebDriverWait(driver, 5).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            alert_text = alert.text
            logging.info(f"Signup alert: {alert_text}")
            alert.accept()
        except TimeoutException:
            logging.warning("No alert appeared after signup")

        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
        time.sleep(2)

        logging.info("Attempting login")
        driver.find_element(By.ID, 'login2').click()
        time.sleep(1)
        driver.find_element(By.ID, 'loginusername').clear()
        driver.find_element(By.ID, 'loginusername').send_keys(userna)
        driver.find_element(By.ID, 'loginpassword').clear()
        driver.find_element(By.ID, 'loginpassword').send_keys(passw)
        driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div[3]/button[2]').click()
        time.sleep(2)

        try:
            WebDriverWait(driver, 5).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            logging.error(f"Login alert: {alert.text}")
            alert.accept()
            assert False, f"Login failed for {userna}: {alert.text}"
        except TimeoutException:
            logging.info("No alert appeared after login. Checking welcome...")

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "nameofuser")))
        welcome_text = driver.find_element(By.ID, "nameofuser").text
        assert userna in welcome_text, "Login failed or username not displayed"
        logging.info("Login successful and username verified")

        logging.info("Adding first product to cart")
        driver.find_element(By.XPATH, '/html/body/div[5]/div/div[2]/div/div[1]/div/div/h4/a').click()
        time.sleep(2)
        driver.find_element(By.XPATH, '/html/body/div[5]/div/div[2]/div[2]/div/a').click()

        try:
            WebDriverWait(driver, 5).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            assert alert.text != "", "Unexpected or missing alert text"
            logging.info(f"Cart alert (1st item): {alert.text}")
            alert.accept()
        except TimeoutException:
            logging.warning("No alert appeared after adding 1st item to cart")

        driver.back()
        driver.back()
        time.sleep(2)

        logging.info("Adding second product to cart")
        driver.find_element(By.XPATH, '/html/body/div[5]/div/div[2]/div/div[2]/div/div/h4/a').click()
        time.sleep(2)
        driver.find_element(By.XPATH, '/html/body/div[5]/div/div[2]/div[2]/div/a').click()

        try:
            WebDriverWait(driver, 5).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            assert alert.text != "", "Unexpected or missing alert text"
            logging.info(f"Cart alert (2nd item): {alert.text}")
            alert.accept()
        except TimeoutException:
            logging.warning("No alert appeared after adding 2nd item to cart")

        time.sleep(2)
        driver.back()
        driver.back()
        time.sleep(2)

        logging.info("Proceeding to cart")
        driver.find_element(By.ID, 'cartur').click()
        time.sleep(3)

        cart_items = driver.find_elements(By.XPATH, "//tr[@class='success']")
        assert len(cart_items) > 0, "Cart is empty!"
        logging.info(f"{len(cart_items)} item(s) found in cart")

        driver.find_element(By.XPATH, '/html/body/div[6]/div/div[2]/button').click()
        time.sleep(2)

        logging.info("Entering order details")
        driver.find_element(By.ID, 'name').send_keys('Senthil')
        driver.find_element(By.ID, 'card').send_keys('94823473284')
        driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div[3]/button[2]').click()

        driver.save_screenshot(f"Buyed_{userna}.png")
        logging.info("Purchase complete. Screenshot saved")

        time.sleep(2)
        driver.find_element(By.XPATH, '/html/body/div[10]/div[7]/div/button').click()
        logging.info("Closed confirmation popup")

    except AssertionError as ae:
        logging.error(f"Assertion failed: {ae}")
        assert False, f"Test failed for {userna}: {ae}"
    except Exception as e:
        logging.error("Unexpected error occurred", exc_info=True)
        assert False, f"Test failed for {userna} due to exception"
    finally:
        driver.quit()
