from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_key = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Загрузить файл в базу знаний 📥')],
                                         [KeyboardButton(text='Дать ответ из базы 🗣️')]],
                            resize_keyboard=True,
                            input_field_placeholder='Что вы хотите сделать?')