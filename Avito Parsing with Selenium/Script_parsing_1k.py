import json
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

print("-"*50)
print("Идёт парсинг объявлений для 1к-квартир")

# Инициализация драйвера
driver = webdriver.Chrome()
driver.get(
    'https://www.avito.ru/perm/kvartiry/sdam/na_dlitelnyy_srok-ASgBAgICAkSSA8gQ8AeQUg?cd=1&context=H4sIAAAAAAAA_wEjANz_YToxOntzOjg6ImZyb21QYWdlIjtzOjc6ImNhdGFsb2ciO312FITcIwAAAA&f=ASgBAQICA0SSA8gQ8AeQUsDBDbr9NwFAzAgkjFmOWQ&s=104&user=1')

# Ждем загрузки объявлений
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.iva-item-content-fRmzq'))
    )
except:
    print("Не удалось произвести поиск по объявлениям (капча?)")
    driver.quit()
    exit()

# Счётчик объявлений для цикла
ad_counter = 0
id_counter = 0
avito_ad_id = []

# Парсинг объявлений
containers = driver.find_elements(By.CSS_SELECTOR, '[class^=iva-item-content]')

file_1k = open ('output_scripts_parsing\parsing_output_1k.txt', 'w', encoding='utf-8')

for container in containers:
    # Извлечение названия - заголовка
    try:
        title = container.find_element(By.CSS_SELECTOR, '[class^=iva-item-title]').text
    except:
        title = "Не удалось получить заголовок"

    # Парсинг цены
    try:
        price_element = container.find_element(By.XPATH, ".//meta[@itemProp='price']")
        price = price_element.get_attribute('content')
    except:
        price_element = "Не удалось получить цену"

    # Парсинг улицы и номера дома
    try:
        address_links = container.find_elements(By.XPATH, ".//div[@class='geo-root-BBVai']//a")
        if len(address_links) >= 2:
            street = address_links[0].text.strip()
            house_number = address_links[1].text.strip()
        elif len(address_links) == 1:
            street = address_links[0].text.strip()
            house_number = "Номер дома не указан"
        else:
            street = "Улица не найдена"
            house_number = "Номер дома не найден"
    except Exception:
        street = "Улица не найдена"
        house_number = "Номер дома не найден"

    # Парсинг района
    try:
        district = container.find_element(By.CSS_SELECTOR, '.styles-module-root_top-XeS0S').text
    except NoSuchElementException:
        district = "Район не найден"

    # Парсинг описания
    try:
        description = container.find_element(By.CSS_SELECTOR, '.styles-module-root_bottom-hgeJ2').text
    except NoSuchElementException:
        description = "Описание не найдено"

    # Парсинг даты публикации
    try:
        date = container.find_element(By.CSS_SELECTOR, '.iva-item-dateInfoStep-AoWrh .styles-module-root-PY1ie').text
    except NoSuchElementException:
        date = "Дата не найдена"

    # Парсинг ID. Ищем место в html коде, где указан ID, пишем в json
    try:
        outer = container.find_element(By.XPATH, './ancestor::*[@data-marker="item"]')
        item_id = outer.get_attribute('data-item-id')
    except NoSuchElementException:
        continue

    if district != "Район не найден":
        ad_counter += 1
        print(f" Объявление-{ad_counter}:", file=file_1k)
        print(f" {title}", file=file_1k)
        print(f" Цена: {price} ₽", file=file_1k)
        print(f" Адрес: {street} {house_number}", file=file_1k)
        print(f" Район: {district}", file=file_1k)
        print(f" Описание: {description}", file=file_1k)
        print(f" Дата публикации: {date}", file=file_1k)
        print("- " * 50, file=file_1k)
        if item_id:
            id_counter += 1
            avito_ad_id.append(item_id)

driver.quit()
file_1k.close()

print(f"Закончил запись {ad_counter} объявлений в parsing_output_1k.txt")
# Запись всех ID в JSON после завершения парсинга
with open("id_1k.json", "w", encoding="utf-8") as f:
    json.dump(avito_ad_id, f, ensure_ascii=False, indent=2)
print(f"Закончил запись {id_counter} ID в id_1k.json")
print("-"*50)