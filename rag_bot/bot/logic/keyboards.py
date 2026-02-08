from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_key = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Работа с файлами 📝')],
                                         [KeyboardButton(text='Дать ответ из базы 🗣️')]],
                            resize_keyboard=True,
                            input_field_placeholder='Что вы хотите сделать?')

file_actions_key = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Загрузить новый документ 📥'), KeyboardButton(text='Удалить документ 🗑️')],
        [KeyboardButton(text='Посмотреть все загруженные документы 📚'), KeyboardButton(text='Назад к меню ⬅️')]],
    resize_keyboard=True,
    input_field_placeholder='Выберите действие с файлом...'
)