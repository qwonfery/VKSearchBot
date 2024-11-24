import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command

from config import BOT_TOKEN

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token=BOT_TOKEN)
# Диспетчер
dp = Dispatcher()

# Directory to save downloaded files
DOWNLOAD_DIR = 'downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


@dp.message(content_types=types.ContentType.DOCUMENT)
async def handle_document(message: types.Message):
    user = message.from_user.id

    document = message.document
    file_info = await bot.get_file(document.file_id)
    file_path = file_info.file_path
    destination = os.path.join(DOWNLOAD_DIR, document.file_name)

    await bot.download_file(file_path, destination)
    await message.reply(f"Файл {document.file_name} успешно загружен.")


# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello!")


# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())