from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd

def get_default_chrome_options():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    return options


options = get_default_chrome_options()
driver = webdriver.Chrome(options=options)

driver.get("https://web.whatsapp.com/")

time.sleep(20)

input("Нажмите Enter для выхода...")

js_script = """
return (async function() {
    function getElementsByXPath(xpath, contextNode = document) {
        const results = [];
        const query = document.evaluate(xpath, contextNode, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
        for (let i = 0; i < query.snapshotLength; i++) {
            results.push(query.snapshotItem(i));
        }
        return results;
    }

    // Открываем диалог с контактами
    function clickButton1() {
        let elements = getElementsByXPath("//section/div[6]/div[2]/div[3]");
        for (let i of elements) i.click();
        return true;
    }

    // Получаем контейнер со скроллом
    function getScrollContainer() {
        // Сначала ищем по XPath
        let containers = getElementsByXPath("//div[@role='dialog']//div[contains(@class, 'scroll')]");
        if (containers.length > 0) return containers[0];
        
        // Затем ищем по свойствам стилей
        const dialog = document.querySelector("div[role='dialog']");
        if (dialog) {
            const scrollables = [...dialog.querySelectorAll('div')].filter(el => {
                const style = window.getComputedStyle(el);
                return (style.overflowY === 'auto' || style.overflowY === 'scroll') && el.scrollHeight > el.clientHeight;
            });
            if (scrollables.length > 0) return scrollables[0];
        }
        return null;
    }

    // Функция для получения номеров
    function getNumbers() {
        const elements = getElementsByXPath("//div[@role='dialog']//span");
        const numbers = new Set();
        
        for (let el of elements) {
            const text = el.innerText || el.textContent;
            if (text && text.trim().startsWith("+")) {
                numbers.add(text.trim());
            }
        }
        
        return Array.from(numbers);
    }

    // Функция для задержки
    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // Функция для автоматического скролла
    async function scrollToBottom(container) {
        if (!container) return [];
        
        const collectedNumbers = new Set();
        let prevHeight = -1;
        let noChangeCount = 0;
        const maxNoChange = 8;
        const delay = 600;
        
        // Основной цикл скролла
        while (noChangeCount < maxNoChange) {
            // Собираем номера
            getNumbers().forEach(num => collectedNumbers.add(num));
            
            // Проверяем высоту контента
            const currentHeight = container.scrollHeight;
            if (currentHeight === prevHeight) {
                noChangeCount++;
            } else {
                noChangeCount = 0;
                prevHeight = currentHeight;
            }
            
            // Скроллим вниз
            container.scrollTop += Math.min(container.clientHeight * 0.5, 300);
            await sleep(delay);
            
            // Если достигли конца
            if (container.scrollTop + container.clientHeight >= currentHeight) {
                break;
            }
        }
        
        // Повторный проход
        container.scrollTop = 0;
        await sleep(delay);
        
        let lastScrollTop = -1;
        while (container.scrollTop !== lastScrollTop) {
            lastScrollTop = container.scrollTop;
            getNumbers().forEach(num => collectedNumbers.add(num));
            container.scrollTop += Math.min(container.clientHeight * 0.5, 300);
            await sleep(delay);
        }
        
        return Array.from(collectedNumbers);
    }

    // Основной процесс
    try {
        // Открываем диалог
        clickButton1();
        await sleep(2000);
        
        // Находим контейнер
        const container = getScrollContainer();
        if (!container) {
            return { success: false, error: "Не найден контейнер для скролла" };
        }
        
        // Запускаем скролл и сбор
        const contacts = await scrollToBottom(container);
        
        // Возвращаем результат
        return { 
            success: true, 
            contacts: contacts, 
            count: contacts.length 
        };
    } catch (error) {
        return { 
            success: false, 
            error: error.toString() 
        };
    }
})();
"""

def get_group_members(group_name):
    search_box = driver.find_element(By.XPATH, "//div[@contenteditable='true']")
    search_box.clear()
    search_box.send_keys(group_name)
    time.sleep(2)
    search_box.send_keys(Keys.ENTER)
    time.sleep(2)
    
    driver.find_element(By.XPATH, "//div[@id='main']/header/div[1]").click()
    time.sleep(2)
    
    driver.find_element(By.XPATH, "//section/div[6]/div[2]/div[3]").click()
    time.sleep(2)
    numbers = driver.execute_script(js_script)
    return numbers


group_name = input("Введите название группы: ")
numbers = get_group_members(group_name)

print(numbers)
ca = input("finish")
driver.quit()



# Сохраняем в CSV
# df = pd.DataFrame(numbers, columns=["Phone Number"])
# df.to_csv("whatsapp_contacts.csv", index=False)

# print(f"Сохранено {len(numbers)} номеров в 'whatsapp_contacts.csv'")
