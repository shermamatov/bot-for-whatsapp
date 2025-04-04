import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WhatsAppBot:
    def __init__(self):
        self.driver = None
        self.is_initialized = False
        
    def initialize(self):
        """Инициализация драйвера и вход в WhatsApp Web"""
        try:
            # Настройка опций Chrome
            options = webdriver.ChromeOptions()
            options.add_argument("--start-maximized")
            options.add_argument("--disable-notifications")
            
            # Инициализация драйвера
            self.driver = webdriver.Chrome(options=options)
            self.driver.get("https://web.whatsapp.com/")
            
            # Ожидание загрузки QR-кода и сканирования пользователем
            logger.info("Пожалуйста, отсканируйте QR-код для входа в WhatsApp Web...")
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "._2G4rS"))
            )
            
            logger.info("Успешный вход в WhatsApp Web")
            self.is_initialized = True
            return True
        except Exception as e:
            logger.error(f"Ошибка при инициализации: {str(e)}")
            return False
    
    def open_group(self, group_name):
        """Открытие группового чата по названию"""
        try:
            # Поиск группы
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "._2vDPL"))
            )
            search_box.clear()
            search_box.send_keys(group_name)
            time.sleep(2)
            
            # Выбор группы из результатов поиска
            group_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//span[@title='{group_name}']"))
            )
            group_element.click()
            time.sleep(2)
            logger.info(f"Группа '{group_name}' успешно открыта")
            return True
        except Exception as e:
            logger.error(f"Ошибка при открытии группы: {str(e)}")
            return False
    
    def get_new_member_info(self, message):
        """Извлечение информации о новом участнике из сообщения"""
        try:
            # Регулярное выражение для извлечения номера телефона
            phone_pattern = r'(\+\d{1,3}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}'
            match = re.search(phone_pattern, message)
            
            if match:
                phone_number = match.group(0)
                # Удаление всех символов, кроме цифр и +
                phone_number = re.sub(r'[^\d+]', '', phone_number)
                return phone_number
            return None
        except Exception as e:
            logger.error(f"Ошибка при извлечении номера телефона: {str(e)}")
            return None
    
    def mention_user(self, phone_number, message):
        """Отметка пользователя в группе и отправка сообщения"""
        try:
            # Ввод символа @ для упоминания
            chat_input = self.driver.find_element(By.CSS_SELECTOR, ".selectable-text")
            chat_input.send_keys("@")
            time.sleep(1)
            
            # Выбор пользователя из списка
            mention_box = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "._1TBIl"))
            )
            
            # Поиск элемента с номером телефона пользователя
            user_elements = self.driver.find_elements(By.CSS_SELECTOR, "._37FrU")
            for element in user_elements:
                if phone_number in element.text:
                    element.click()
                    break
            
            # Добавление сообщения и отправка
            chat_input.send_keys(" " + message)
            chat_input.send_keys(Keys.ENTER)
            logger.info(f"Пользователь с номером {phone_number} упомянут в сообщении")
            return True
        except Exception as e:
            logger.error(f"Ошибка при упоминании пользователя: {str(e)}")
            return False
    
    def remove_user(self, phone_number):
        """Удаление пользователя из группы"""
        try:
            # Открытие информации о группе
            header = self.driver.find_element(By.CSS_SELECTOR, "._2au8k")
            header.click()
            time.sleep(1)
            
            # Поиск списка участников
            participants_section = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "._3Dr4e"))
            )
            participants_section.click()
            time.sleep(1)
            
            # Поиск пользователя по номеру телефона
            participants = self.driver.find_elements(By.CSS_SELECTOR, "._1X8rk")
            for participant in participants:
                if phone_number in participant.text:
                    # Открытие контекстного меню
                    participant.click()
                    time.sleep(1)
                    
                    # Выбор опции "Удалить"
                    menu_items = self.driver.find_elements(By.CSS_SELECTOR, "._3UUbR")
                    for item in menu_items:
                        if "Удалить" in item.text:
                            item.click()
                            time.sleep(1)
                            
                            # Подтверждение удаления
                            confirm_button = self.driver.find_element(By.CSS_SELECTOR, "._20C5O._2Zdgs")
                            confirm_button.click()
                            time.sleep(1)
                            
                            logger.info(f"Пользователь с номером {phone_number} удален из группы")
                            return True
            
            logger.warning(f"Пользователь с номером {phone_number} не найден в списке участников")
            return False
        except Exception as e:
            logger.error(f"Ошибка при удалении пользователя: {str(e)}")
            return False
    
    def send_private_message(self, phone_number, message):
        """Отправка личного сообщения пользователю"""
        try:
            # Открытие нового чата
            new_chat_button = self.driver.find_element(By.CSS_SELECTOR, "._1XaK7")
            new_chat_button.click()
            time.sleep(1)
            
            # Ввод номера телефона
            search_box = self.driver.find_element(By.CSS_SELECTOR, "._2vDPL")
            search_box.clear()
            search_box.send_keys(phone_number)
            time.sleep(2)
            
            # Выбор пользователя из результатов поиска
            user_element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "._37FrU"))
            )
            user_element.click()
            time.sleep(1)
            
            # Отправка сообщения
            chat_input = self.driver.find_element(By.CSS_SELECTOR, ".selectable-text")
            chat_input.send_keys(message)
            chat_input.send_keys(Keys.ENTER)
            
            logger.info(f"Личное сообщение отправлено пользователю с номером {phone_number}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при отправке личного сообщения: {str(e)}")
            return False
    
    def monitor_new_members(self, group_name, welcome_message, private_message):
        """Мониторинг новых участников группы"""
        if not self.is_initialized:
            if not self.initialize():
                return False
        
        # Открытие группы
        if not self.open_group(group_name):
            return False
        
        logger.info(f"Начат мониторинг новых участников в группе '{group_name}'")
        
        # Список уже обработанных сообщений
        processed_messages = set()
        
        try:
            while True:
                # Поиск системных сообщений о добавлении участников
                system_messages = self.driver.find_elements(By.CSS_SELECTOR, "._2nGZn")
                
                for message_element in system_messages:
                    message_text = message_element.text
                    message_id = message_element.get_attribute("data-id")
                    
                    # Проверка, обрабатывали ли мы уже это сообщение
                    if message_id in processed_messages:
                        continue
                    
                    # Проверка, является ли сообщение уведомлением о новом участнике
                    if "добавлен" in message_text.lower() or "присоединился" in message_text.lower():
                        # Добавление сообщения в список обработанных
                        processed_messages.add(message_id)
                        
                        # Получение номера телефона нового участника
                        phone_number = self.get_new_member_info(message_text)
                        
                        if phone_number:
                            logger.info(f"Обнаружен новый участник с номером: {phone_number}")
                            
                            # Шаг 1: Копирование номера (уже выполнено)
                            
                            # Шаг 2: Отметка пользователя и отправка сообщения
                            self.mention_user(phone_number, welcome_message)
                            time.sleep(2)
                            
                            # Шаг 3: Удаление пользователя из группы
                            self.remove_user(phone_number)
                            time.sleep(2)
                            
                            # Шаг 4: Отправка личного сообщения
                            self.send_private_message(phone_number, private_message)
                            time.sleep(2)
                
                # Пауза перед следующей проверкой
                time.sleep(10)
                
        except KeyboardInterrupt:
            logger.info("Мониторинг остановлен пользователем")
        except Exception as e:
            logger.error(f"Ошибка во время мониторинга: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("Драйвер закрыт")
    
    def close(self):
        """Закрытие драйвера"""
        if self.driver:
            self.driver.quit()
            logger.info("Драйвер закрыт")

# Пример использования
if __name__ == "__main__":
    bot = WhatsAppBot()
    
    # Настройки
    group_name = "Название вашей группы"  # Замените на название своей группы
    welcome_message = "Привет! К сожалению, вы будете удалены из группы. Проверьте личные сообщения для дополнительной информации."
    private_message = "Здравствуйте! Вы были удалены из группы. Для получения дополнительной информации свяжитесь с администратором."
    
    # Запуск мониторинга
    bot.monitor_new_members(group_name, welcome_message, private_message)