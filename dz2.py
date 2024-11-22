import requests
from bs4 import BeautifulSoup
import json
import re
import os

# Базовый URL сайта
base_url = 'http://books.toscrape.com/catalogue/page-{}.html'

# Список для хранения данных о книгах
books_data = []

# Цикл по страницам (1 до 50)
for page in range(1, 51):
    url = base_url.format(page)
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Находим все контейнеры книг
        book_containers = soup.find_all('article', class_='product_pod')
        
        for book in book_containers:
            # Извлечение названия
            title = book.h3.a['title']
            
            # Извлечение цены
            price = book.find('p', class_='price_color').text[1:]  # Убираем символ валюты
            
            # Извлечение наличия
            in_stock = book.find('p', class_='instock availability').text.strip()
            stock_quantity_match = re.search(r'(\d+)', in_stock)  # Извлекаем число
            
            if stock_quantity_match:
                stock_quantity = int(stock_quantity_match.group(1))  # Преобразуем в integer
            else:
                stock_quantity = 0  # Устанавливаем значение по умолчанию
            
            # Извлечение ссылки на страницу книги
            detail_link = book.h3.a['href']
            detail_url = f'http://books.toscrape.com/catalogue/{detail_link}'
            
            # Запрос к странице книги для получения описания
            detail_response = requests.get(detail_url)
            if detail_response.status_code == 200:
                detail_soup = BeautifulSoup(detail_response.content, 'html.parser')
                # Извлечение описания
                description = detail_soup.find('meta', attrs={'name': 'description'})['content'].strip()
                
                # Добавление данных о книге в список
                books_data.append({
                    'title': title,
                    'price': float(price),  # Преобразуем цену в float
                    'stock_quantity': stock_quantity,
                    'description': description
                })
            else:
                print(f"Не удалось получить детали для {title}")
    else:
        print(f"Не удалось получить страницу {page}")

# Проверка количества собранных данных
print(f"Количество книг, собранных для сохранения: {len(books_data)}")

# Сохранение данных в JSON файл
try:
    with open('books_data.json', 'w', encoding='utf-8') as json_file:
        json.dump(books_data, json_file, ensure_ascii=False, indent=4)
    print("Скрейпинг завершен, данные сохранены в books_data.json")
except Exception as e:
    print(f"Ошибка при сохранении файла: {e}")

#print(f"Текущая директория: {os.getcwd()}")
