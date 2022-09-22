from aiogram import Bot, types
from aiogram.utils.callback_data import CallbackData
import config


class Profile:
    def __init__(self):
        pass

    def view(self, id_profile):
        data = CallbackData('view_profile', 'action', 'id_profile')
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        btn_1 = types.InlineKeyboardButton(text='⚠️', callback_data=data.new(action='ban', id_profile=id_profile))
        btn_2 = types.InlineKeyboardButton(text='👎', callback_data=data.new(action='no', id_profile=id_profile))
        btn_3 = types.InlineKeyboardButton(text='👍', callback_data=data.new(action='yes', id_profile=id_profile))
        keyboard.add(btn_1, btn_2, btn_3)
        return keyboard

    def view2(self, id_profile):
        data = CallbackData('view_profile', 'action', 'id_profile')
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        btn_1 = types.InlineKeyboardButton(text='⚠️Жалоба', callback_data=data.new(action='ban', id_profile=id_profile))

        keyboard.add(btn_1)
        return keyboard

    def change_profile(self):
        data = CallbackData('change_profile', 'action')
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        btn_1 = types.InlineKeyboardButton(text='Создать профиль заново', callback_data=data.new(action='yes'))
        btn_2 = types.InlineKeyboardButton(text='Удалить профиль', callback_data=data.new(action='del'))
        keyboard.add(btn_1, btn_2)
        return keyboard

    def make_ban(self, id_profile):
        data = CallbackData('ban_profile', 'action', 'id_profile')
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        btn_1 = types.InlineKeyboardButton(text='ban', callback_data=data.new(action='ban', id_profile=id_profile))
        btn_2 = types.InlineKeyboardButton(text='unban', callback_data=data.new(action='unban', id_profile=id_profile))
        keyboard.add(btn_1, btn_2)
        return keyboard


async def choice_new_contact():
    data = CallbackData('confirm_new_contact', 'action')
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    btn_confirm = types.InlineKeyboardButton(text='Да', callback_data=data.new(action='yes'))
    btn_no = types.InlineKeyboardButton(text='Нет', callback_data=data.new(action='no'))
    keyboard.add(btn_no, btn_confirm)
    return keyboard


async def confirm_public():
    confirm_public_data = CallbackData('confirm_public_from_user', 'action')
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    btn_confirm = types.InlineKeyboardButton(text='Подтвердить', callback_data=confirm_public_data.new(action='yes'))
    btn_no_confirm = types.InlineKeyboardButton(text='Изменить', callback_data=confirm_public_data.new(action='no'))
    btn_stop = types.InlineKeyboardButton(text='Отменить',
                                          callback_data=confirm_public_data.new(action='stop'))
    keyboard.add(btn_confirm, btn_no_confirm, btn_stop)
    return keyboard
