from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Инициализация драйвера
driver = webdriver.Chrome()
driver.get('https://www.avito.ru/perm/kvartiry/sdam/na_dlitelnyy_srok/1-komnatnye-ASgBAgICA0SSA8gQ8AeQUswIjlk?cd=1&context=H4sIAAAAAAAA_wEjANz_YToxOntzOjg6ImZyb21QYWdlIjtzOjc6ImNhdGFsb2ciO312FITcIwAAAA')

# Ждем загрузки объявлений
try:
    WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, '.iva-item-content-fRmzq'))
)
except:
    print("Не удалось произвести поиск по объявлениям (капча?")
# Счётчик объявлений для цикла
ad_counter=0
# Парсинг объявлений
containers = driver.find_elements(By.CSS_SELECTOR, '[class^=iva-item-content]')

for container in containers:
    ad_counter +=1
    try:
        # Извлечение данных
        title = container.find_element(By.CSS_SELECTOR, '[class^=iva-item-title]').text
        price_element = container.find_element(By.XPATH, ".//meta[@itemProp='price']")
        price = price_element.get_attribute('content')
        # Парсинг улицы
        try:
            # Альтернативный способ поиска улицы
            street = container.find_element(By.XPATH, ".//div[@class='geo-root-BBVai']//a").text
        except NoSuchElementException:
            street = "Улица не найдена"

        #price = container.find_element(By.CSS_SELECTOR, '[class=^iva-item-priceStep-TVego iva-item-ivaItemRedesign-QmNXd]').text
        #address = container.find_element(By.CSS_SELECTOR, '[class=^geo-root]').text
        #description = container.find_element(By.CSS_SELECTOR, '[class=^iva-item-autoParamsStep]').text
        #additional_info = container.find_element(By.CSS_SELECTOR, '[class=^iva-item-listMiddleBlock]').text

        print(f"Объявление-{ad_counter}: \n {title}")
        print(f" Цена: {price} ₽")
        print(f" Улица: {street}")
        print("-" * 50)

        #print(f"Описание: {description}")
        #print(f"Дополнительные параметры: {additional_info}")
        #print("-" * 50)

    except Exception as e:
        print(f"Ошибка при обработке объявления: {e}")


driver.quit()
print (f"Всего было обработано: {ad_counter} объявлений")