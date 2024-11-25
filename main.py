import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import F

import top_domains
from config import BOT_TOKEN

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token=BOT_TOKEN)
# Диспетчер
dp = Dispatcher()


# Определяем состояния
class Form(StatesGroup):
    query = State()
    folder_id = State()
    api_key = State()
    domains = State()


@dp.message(CommandStart())
async def cmd_start(message: types.Message,  state: FSMContext):
    await state.set_state(Form.query)
    await message.reply("Привет! Отправьте мне CSV/TXT файл с запросами или строку с запросами.")


@dp.message(Form.query, F.document)
async def process_file(message: types.Message, state: FSMContext):
    document = message.document
    file_info = await bot.get_file(document.file_id)

    file_bytes = await bot.download_file(file_info.file_path)
    # Преобразуем содержимое файла в строку
    queries_string = file_bytes.read().decode("utf-8")

    await state.update_data(queries_string=queries_string)

    await state.set_state(Form.api_key)
    await message.reply("Теперь отправьте ключ API.")


@dp.message(Form.query)
async def process_string(message: types.Message, state: FSMContext):
    await state.update_data(queries_string=message.text)

    await state.set_state(Form.api_key)
    await message.reply("Теперь отправьте ключ API.")


@dp.message(Form.api_key)
async def process_api_key(message: types.Message, state: FSMContext):
    await state.update_data(api_key=message.text)

    await state.set_state(Form.folder_id)
    await message.reply("Теперь отправьте идентификатор каталога (https://yandex.cloud/ru/docs/resource-manager/operations/folder/get-id#console_1)")


@dp.message(Form.folder_id)
async def process_folder_id(message: types.Message, state: FSMContext):
    await state.update_data(folder_id=message.text)

    await state.set_state(Form.domains)
    await message.reply("Теперь отправьте домен или домены, по которым мы будем смотреть позиции (разделите домены запятой).")


@dp.message(Form.domains)
async def process_domains(message: types.Message, state: FSMContext):
    await state.update_data(domains=message.text)

    user_data = await state.get_data()
    queries_string = user_data.get('queries_string')
    api_key = user_data.get('api_key')
    domains = user_data.get('domains')
    folder_id = user_data.get('folder_id')

    # Обработка данных
    repl = top_domains.process_queries(queries_string, api_key, folder_id, domains)
    await message.reply(repl)
    # await message.reply(f"Полученные данные:\nЗапросы: {queries_string}\nAPI Key: {api_key}\nДомены: {domains}")

    # Старт по новой
    await cmd_start(message, state)
    # await state.set_state(Form.query)


# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())