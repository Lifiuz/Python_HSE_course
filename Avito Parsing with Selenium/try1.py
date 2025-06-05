from selenium import webdriver #Selenium — фреймворк для автоматизации действий в браузере,

driver = webdriver.Chrome() #Создание экземпляра драйвера
driver.get('https://www.avito.ru/perm/kvartiry/sdam/na_dlitelnyy_srok/1-komnatnye-ASgBAgICA0SSA8gQ8AeQUswIjlk?cd=1&context=H4sIAAAAAAAA_wEjANz_YToxOntzOjg6ImZyb21QYWdlIjtzOjc6ImNhdGFsb2ciO312FITcIwAAAA')
#Метод driver.get(url) загружает страницу по указанному URL

print(driver.title) # Выводим заголовок страницы
filter_2k = name_input = driver.find_element_by_name("params[550]")

