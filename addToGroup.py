from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import pandas as pd

def get_default_chrome_options():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    return options
options = get_default_chrome_options()
driver = webdriver.Chrome(options=options)
driver.get("https://web.whatsapp.com/")
wait = WebDriverWait(driver, 30)

my_group_name = "не обращаем внимание"

numbers_arr = []
input("Нажмите Enter для выхода...")
def addToGroup():
    search_box = driver.find_element(By.XPATH, "//div[@contenteditable='true']")
    search_box.clear()
    search_box.send_keys(my_group_name)
    time.sleep(2) 
    search_box.send_keys(Keys.ENTER)
    time.sleep(2)
    driver.find_element(By.XPATH, "//div[@id='main']/header/div[1]").click()
    time.sleep(2)
    driver.find_element(By.XPATH, "//section/div[6]/div[2]/div[1]").click()
    time.sleep(2)
    for nomer in numbers_arr:
        try : 
            search_participant = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')))
            search_participant.clear()
            search_participant.send_keys(nomer)
            time.sleep(2)
            try:    
                driver.find_element(By.XPATH, "//div[@role='dialog']//div[@role='checkbox']/div[2]/div[1]").click()
            except NoSuchElementException:
                    print(f"Контакт {nomer} не найден и пропущен")
                    search_participant.clear()
                    continue
        except Exception as e:
                print(f"Ошибка при добавлении {nomer}")
    driver.find_element(By.XPATH, "//div[@role='dialog']//span[2]//div[@role='button']").click()
    time.sleep(2)
    driver.find_element(By.XPATH, "//div[@role='dialog']//button[2]").click()
    time.sleep(3)
    print('готово')

if __name__ == "__main__":
    addToGroup()

input("Нажмите Enter для выхода...")
