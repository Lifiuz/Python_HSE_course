from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

# Инициализация драйвера
driver = webdriver.Chrome()
driver.get(
    'https://www.avito.ru/perm/kvartiry/sdam/na_dlitelnyy_srok/4-komnatnye-ASgBAgICA0SSA8gQ8AeQUswIlFk?cd=1&context=H4sIAAAAAAAA_wEjANz_YToxOntzOjg6ImZyb21QYWdlIjtzOjc6ImNhdGFsb2ciO312FITcIwAAAA&f=ASgBAgICBESSA8gQ8AeQUswIlFnAwQ26_Tc&s=104&user=1')

# Ждём загрузки блоков с объявлениями
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[class^=iva-item-content]'))
    )
except:
    print("Не удалось загрузить объявления (возможно, капча)")
    driver.quit()
    exit()

# Собираем ID объявлений с найденным районом
ad_ids = []
containers = driver.find_elements(By.CSS_SELECTOR, '[class^=iva-item-content]')

for container in containers:
    try:
        # Пытаемся получить район
        district = container.find_element(By.CSS_SELECTOR, '.styles-module-root_top-XeS0S').text
    except NoSuchElementException:
        district = "Район не найден"

    if district != "Район не найден":
        try:
            # Получаем ID из родительского блока
            outer = container.find_element(By.XPATH, './ancestor::*[@data-marker="item"]')
            item_id = outer.get_attribute('data-item-id')
            if item_id:
                ad_ids.append(item_id)
        except NoSuchElementException:
            continue

driver.quit()

# Сохраняем ID в файл JSON
with open("ids.json", "w", encoding="utf-8") as f:
    json.dump(ad_ids, f, ensure_ascii=False, indent=2)

print(f"Найдено {len(ad_ids)} ID с районом. Сохранено в ids.json")
