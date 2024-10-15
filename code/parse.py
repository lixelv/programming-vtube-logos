import os
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from aiofiles import open as aioopen

domen = "https://vtuber-style-logos.vercel.app"

# Асинхронная функция для скачивания изображений
async def download_image(session, img_url, file_path):
    print(f"Downloading: {img_url}")
    print(f"Saving to: {file_path}")
    print("=====================================")
    
    # Проверка относительных URL
    if img_url.startswith("/"):
        img_url = domen + img_url

    # Скачивание изображения
    async with session.get(img_url) as response:
        if response.status == 200:
            async with aioopen(file_path, 'wb') as f:
                await f.write(await response.read())

# Основная функция для парсинга и подготовки к скачиванию
def process_html():
    # Парсим HTML файл
    with open('VTuberized Logos.html', 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Создаем папку, если она не существует
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)

    # Множество для отслеживания занятых имен файлов
    used_filenames = set()

    # Ищем все блоки с изображениями
    cards = soup.find_all('div', class_='card-container')

    images_to_download = []

    for card in cards:
        # Находим заголовок (название программы)
        title = card.find('h3').text.strip().lower()

        # Находим URL изображения
        img_tag = card.find('img')
        if img_tag:
            img_url = img_tag['src']

            # Определение имени файла и проверка на уникальность
            file_name = f"{title}.png"
            count = 0
            while file_name in used_filenames:
                file_name = f"{title} ({count}).png"
                count += 1

            # Добавляем имя файла в множество
            used_filenames.add(file_name)

            # Определяем путь сохранения
            file_path = os.path.join(output_dir, file_name)
            images_to_download.append((img_url, file_path))

    return images_to_download

# Асинхронная функция для скачивания всех изображений
async def download_all_images(images):
    async with aiohttp.ClientSession() as session:
        tasks = [download_image(session, img_url, file_path) for img_url, file_path in images]
        await asyncio.gather(*tasks)

# Запускаем процесс
def main():
    images = process_html()  # Получаем список изображений для скачивания
    asyncio.run(download_all_images(images))  # Асинхронно скачиваем все изображения

if __name__ == "__main__":
    main()
