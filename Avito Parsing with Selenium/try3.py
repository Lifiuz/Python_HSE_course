from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Инициализация драйвера
driver = webdriver.Chrome()
driver.get(
    'https://www.avito.ru/perm/kvartiry/sdam/na_dlitelnyy_srok/1-komnatnye-ASgBAgICA0SSA8gQ8AeQUswIjlk?cd=1&context=H4sIAAAAAAAA_wEjANz_YToxOntzOjg6ImZyb21QYWdlIjtzOjc6ImNhdGFsb2ciO312FITcIwAAAA')

# Ждем загрузки объявлений
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.iva-item-content-fRmzq'))
    )
except:
    print("Не удалось произвести поиск по объявлениям (капча?)")

# Счётчик объявлений для цикла
ad_counter = 0

# Парсинг объявлений
containers = driver.find_elements(By.CSS_SELECTOR, '[class^=iva-item-content]')

for container in containers:
    ad_counter += 1
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

    print(f" Объявление-{ad_counter}:")
    print(f" {title}")
    print(f" Цена: {price} ₽")
    print(f" Адрес: {street} {house_number}")
    print(f" Район: {district}")
    print(f" Описание: {description}")
    print(f" Дата публикации: {date}")
    print("- " * 50)

driver.quit()
print(f"Всего было обработано: {ad_counter} объявлений")
