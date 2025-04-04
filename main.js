function getElementsByXPath(xpath, contextNode = document) {
    const results = [];
    const query = document.evaluate(
        xpath,
        contextNode,
        null,
        XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,
        null
    );
    for (let i = 0; i < query.snapshotLength; i++) {
        results.push(query.snapshotItem(i));
    }
    return results;
}

// Открываем диалог с контактами
function clickButton1() {
    let elements = getElementsByXPath("//section/div[6]/div[2]/div[3]");
    for (let i of elements) i.click();
}

// Получаем контейнер со скроллом
function getScrollContainer() {
    // Сначала ищем по XPath
    let containers = getElementsByXPath(
        "//div[@role='dialog']//div[contains(@class, 'scroll')]"
    );
    if (containers.length > 0) return containers[0];

    // Затем ищем по свойствам стилей
    const dialog = document.querySelector("div[role='dialog']");
    if (dialog) {
        const scrollables = [...dialog.querySelectorAll("div")].filter((el) => {
            const style = window.getComputedStyle(el);
            return (
                (style.overflowY === "auto" || style.overflowY === "scroll") &&
                el.scrollHeight > el.clientHeight
            );
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

// Функция для автоматического скролла
async function scrollToBottom(container) {
    if (!container) return [];

    const collectedNumbers = new Set();
    let prevHeight = -1;
    let noChangeCount = 0;
    const maxNoChange = 8;
    const delay = 600;

    console.log("Начинаем сбор контактов...");

    // Основной цикл скролла
    while (noChangeCount < maxNoChange) {
        // Собираем номера
        getNumbers().forEach((num) => collectedNumbers.add(num));
        console.log(`Найдено ${collectedNumbers.size} номеров`);

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
        await new Promise((r) => setTimeout(r, delay));

        // Если достигли конца
        if (container.scrollTop + container.clientHeight >= currentHeight) {
            break;
        }
    }

    // Повторный проход
    container.scrollTop = 0;
    await new Promise((r) => setTimeout(r, delay));

    let lastScrollTop = -1;
    while (container.scrollTop !== lastScrollTop) {
        lastScrollTop = container.scrollTop;
        getNumbers().forEach((num) => collectedNumbers.add(num));
        container.scrollTop += Math.min(container.clientHeight * 0.5, 300);
        await new Promise((r) => setTimeout(r, delay));
    }

    return Array.from(collectedNumbers);
}

// Сохранение в localStorage
const storage = {
    save: (data) =>
        localStorage.setItem("whatsappContacts", JSON.stringify(data)),
    load: () => {
        try {
            return JSON.parse(localStorage.getItem("whatsappContacts")) || [];
        } catch (e) {
            return [];
        }
    },
    merge: function (newData) {
        const oldData = this.load();
        const result = Array.from(new Set([...oldData, ...newData]));
        this.save(result);
        return result;
    },
};

// Основная функция
async function scrapeAllContacts() {
    console.log("== Запуск парсера контактов WhatsApp ==");

    // Открываем диалог
    clickButton1();
    await new Promise((r) => setTimeout(r, 2000));

    // Находим контейнер
    const container = getScrollContainer();
    if (!container) {
        console.error("Не найден контейнер для скролла!");
        return;
    }

    // Запускаем скролл и сбор
    const contacts = await scrollToBottom(container);

    // Объединяем с предыдущими и сохраняем
    const allContacts = storage.merge(contacts);
    console.log(`Всего собрано ${allContacts.length} уникальных контактов`);

    // Копируем в буфер обмена
    navigator.clipboard
        .writeText(allContacts.join("\n"))
        .then(() => console.log("Скопировано в буфер обмена"))
        .catch((e) => console.error("Ошибка копирования:", e));

    // Сохраняем как CSV
    const csvContent =
        "data:text/csv;charset=utf-8," +
        allContacts.map((n) => `"${n}"`).join("\n");
    const link = document.createElement("a");
    link.setAttribute("href", encodeURI(csvContent));
    link.setAttribute("download", "whatsapp_contacts.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    console.log("Готово! CSV-файл сохранен.");
    return allContacts;
}

// Запускаем скрипт
scrapeAllContacts();
