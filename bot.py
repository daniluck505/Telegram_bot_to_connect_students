from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from middlewares import rate_limit
import datetime
from functions import *
from loader import *


class Regist(StatesGroup):
    name = State()
    contact = State()
    photo = State()
    description = State()


@rate_limit(limit=3)
@dp.message_handler(commands=['start'], state='*')
async def start(message: types.Message, state: FSMContext):
    await state.finish()
    if message.chat.type == 'private':
        if not DB.user_exists(message.from_user.id):
            try:
                await bot.send_sticker(message.from_user.id,
                                       sticker='CAACAgIAAxkBAAJJlmMohFg5eojXDpEou2Qm-6AC6v6sAAKDAwAC8-O-C4kr1venYneGKQQ')
            except:
                pass
            await bot.send_message(message.from_user.id, config.t1)
            await bot.send_message(message.from_user.id, config.t2)
            await Regist.name.set()
        else:
            await bot.send_message(message.from_user.id, 'Вы уже зарегистрированы')

    else:
        await message.answer('Писать боту можно только в личку')


@dp.message_handler(state=Regist.name, content_types=['text'])
async def regist_name(message: types.Message, state: FSMContext):
    if len(message.text) < 40:
        await state.update_data(name=message.text)
        await bot.send_message(message.from_user.id, config.t3)
        await Regist.next()
    else:
        await bot.send_message(message.from_user.id, "Имя не должно превышать 40 символов, попробуйте еще раз")
        await Regist.name.set()


@dp.message_handler(state=Regist.contact, content_types=['text'])
async def regist_contact(message: types.Message, state: FSMContext):
    if len(message.text) < 100:
        await state.update_data(contact=message.text)
        await bot.send_message(message.from_user.id, config.t4)
        await Regist.next()
    else:
        await bot.send_message(message.from_user.id, "Текст не должен превышать 100 символов, попробуйте еще раз")
        await Regist.contact.set()


@dp.message_handler(state=Regist.photo, content_types=['photo', 'document'])
async def regist_photo(message: types.Message, state: FSMContext):
    from pathlib import Path
    Path(f'files/{message.from_user.id}/').mkdir(parents=True, exist_ok=True)
    if message.content_type == 'photo':
        file_info = await bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        src = f'files/{message.from_user.id}/' + file_info.file_path.replace('photos/', '')

        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file.getvalue())
        await state.update_data(photo=src)
        await bot.send_message(message.from_user.id, config.t5)
        await Regist.next()

    else:
        await bot.send_message(message.from_user.id, "Я жду от тебя фото!")
        await Regist.photo.set()


@dp.message_handler(state=Regist.description, content_types=['text'])
async def regist_description(message: types.Message, state: FSMContext):
    if len(message.text) < 1000:
        await state.update_data(description=message.text)
        telegram_id = message.from_user.id
        person_data = await state.get_data()

        DB.new_row_user(telegram_id,
                        person_data['photo'],
                        person_data['name'],
                        person_data['contact'],
                        person_data['description'])
        await bot.send_message(telegram_id, 'Вот так ваш профиль видят все пользователи')
        await send_profile(telegram_id, telegram_id, opening=False)
        await bot.send_message(telegram_id, 'Так выглядит ваш профиль, если вы отправили его другому пользователю')
        await send_profile(telegram_id, telegram_id, opening=True)
        key = profile_cls.make_ban(telegram_id)
        await send_profile(telegram_id, config.all_profiles_chat, opening=True, reply_markup=key)

        await bot.send_message(message.from_user.id, config.t6)
        await state.finish()
    else:
        await bot.send_message(message.from_user.id, "Текст не должен превышать 1000 символов, попробуйте еще раз")
        await Regist.description.set()


@dp.message_handler(commands=['restart'])
async def restart(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    isban = DB.user_ban_exists(user_id)
    if isban:
        await message.answer('https://www.youtube.com/watch?v=2Q_ZzBGPdqE')
        await bot.send_message(user_id, 'Вы забанены!')
        return

    DB.update_in_user(user_id, 'position', 0)
    await make_contact(user_id)


@rate_limit(limit=3)
@dp.message_handler(commands=['contact'], state='*')
async def contact(message: types.Message, state: FSMContext):
    await state.finish()
    user_id = message.from_user.id
    if message.chat.type == 'private':
        if not DB.user_exists(message.from_user.id):
            await bot.send_message(message.from_user.id, 'Для начала зарегистрируйся')
            await bot.send_message(message.from_user.id, config.t2)
            await Regist.name.set()
        else:
            isban = DB.user_ban_exists(user_id)
            if isban:
                await message.answer('https://www.youtube.com/watch?v=2Q_ZzBGPdqE')
                await bot.send_message(user_id, 'Вы забанены!')
                return
            else:
                await make_contact(user_id)

    else:
        await message.answer('Писать боту можно только в личку')


@rate_limit(limit=3)
@dp.message_handler(commands=['my_profile'], state='*')
async def my_profile(message: types.Message):
    if message.chat.type == 'private':
        user_id = message.from_user.id
        if not DB.user_exists(message.from_user.id):
            await bot.send_message(message.from_user.id, 'Для начала зарегистрируйся')
            await bot.send_message(message.from_user.id, config.t2)
            await Regist.name.set()
        isban = DB.user_ban_exists(user_id)
        if isban:
            await message.answer('https://www.youtube.com/watch?v=2Q_ZzBGPdqE')
            await bot.send_message(user_id, 'Вы забанены!')
            return
        else:
            key = profile_cls.change_profile()
            await send_profile(user_id, user_id, opening=True, reply_markup=key)


@dp.callback_query_handler(text_contains='change_profile')
async def callback_contact(call: types.CallbackQuery, state: FSMContext):
    action = call.data.split(':')[-1]
    user_id = call.from_user.id
    if action == 'yes':
        DB.delete_user(user_id)
        await bot.send_message(user_id, 'Напишите имя')
        await Regist.name.set()
    elif action == 'del':
        DB.delete_user(user_id)
        await bot.send_message(user_id, 'Ваш профиль был удален, чтобы опять пользоваться ботом нажмите \n'
                                        '/start')


@dp.callback_query_handler(text_contains='view_profile')
async def callback_contact(call: types.CallbackQuery):
    action = call.data.split(':')[-2]
    id_profile = int(call.data.split(':')[-1])
    user_id = call.from_user.id
    if action == 'yes':
        await call.message.edit_reply_markup(None)
        await bot.send_message(id_profile, 'Вами заинтересовались:')
        key = profile_cls.view2(id_profile)
        await send_profile(user_id, id_profile, opening=True, reply_markup=key)
        key = await Markup.choice_new_contact()
        await bot.send_message(user_id,
                               'Ваш профиль отправлен пользователю, он свяжется с вами, если пожелает. \n'
                               'Знакомимся еще?',
                               reply_markup=key)
    elif action == 'no':
        await call.message.edit_reply_markup(None)
        await make_contact(user_id)
    elif action == 'ban':
        await call.message.delete()
        key = profile_cls.make_ban(id_profile)
        await send_profile(id_profile, config.SUPPORT_ID, opening=True, reply_markup=key)
        await bot.send_message(user_id, "Спасибо за жалобу")
        await make_contact(user_id)


@dp.callback_query_handler(text_contains='confirm_new_contact')
async def confirm_new_contact(call: types.CallbackQuery):
    action = call.data.split(':')[-1]
    if action == 'yes':
        await call.message.edit_reply_markup(None)
        await make_contact(call.from_user.id)
    else:
        await call.message.edit_reply_markup(None)
        await bot.send_message(call.from_user.id, 'Надеюсь, я помог тебе завести новые знакомства. \n'
                               'Если захочешь еще с кем-то познакомиться, то вызови /contact')


@dp.callback_query_handler(text_contains='ban_profile')
async def callback_ban_profile(call: types.CallbackQuery):
    action = call.data.split(':')[-2]
    id_profile = int(call.data.split(':')[-1])
    if action == 'ban':
        DB.make_ban(id_profile)
        await bot.send_message(id_profile, 'Вы забанены пользователями!')
        await bot.send_message(config.SUPPORT_ID, f'Пользователь {id_profile} забанен')
    elif action == 'unban':
        DB.make_ban(id_profile, yes=False)
        await bot.send_message(id_profile, 'Вы разбанены')
        await bot.send_message(config.SUPPORT_ID, f'Пользователь {id_profile} разбанен')


# ----------------------------------- admin's handlers  -----------------------------------
class send_public(StatesGroup):
    send_publication = State()
    confirm_publication = State()


@dp.message_handler(commands=['public'])
async def public(message: types.Message):
    if await admins_test(message):
        await bot.send_message(message.from_user.id, 'Отправь публикацию')
        await send_public.send_publication.set()


@dp.message_handler(state=send_public.send_publication, content_types=['text', 'photo', 'document'])
async def give_task(message: types.Message, state: FSMContext):
    await state.update_data(task_message=message)
    key = await Markup.confirm_public()
    await message.reply('Подтвердите отправку', reply_markup=key)
    await send_public.confirm_publication.set()


@dp.callback_query_handler(text_contains='confirm_public_from_user', state=send_public.confirm_publication)
async def keyboard_subjects_task(call: types.CallbackQuery, state: FSMContext):
    data_call = call.data.split(':')[-1]
    task_data = await state.get_data()
    if data_call == 'yes':
        await call.message.edit_text('Отправка', reply_markup=None)
        send_list_id = DB.all_list_user_id()
        for i in send_list_id:
            try:
                await task_data['task_message'].send_copy(chat_id=i)
                await asyncio.sleep(0.1)
            except:
                pass
        await bot.send_message(call.from_user.id, 'Сообщения разосланы')
        await state.finish()
    elif data_call == 'no':
        await call.message.edit_text('Отправь публикацию', reply_markup=None)
        await send_public.send_publication.set()
    elif data_call == 'stop':
        await call.message.edit_text('Вы отменили отправку публикации', reply_markup=None)
        await state.finish()


@dp.message_handler(commands=['chat_info'])
async def chat_info(message: types.Message):
    if await admins_test(message):
        await bot.send_message(message.chat.id, message.chat.id)


@dp.message_handler(commands=['dump'])
async def dump(message: types.Message):
    if await admins_test(message):
        await make_dump()


@dp.message_handler(commands=['test'])
async def test(message: types.Message):
    if await admins_test(message):
        n1 = DB.get_user_photo(str(message.from_user.id))
        print(n1)
        n1 = DB.get_user_photo(str(message.from_user.id))
        print(n1)
        n1 = DB.get_user_photo(message.from_user.id)
        print(n1)
        n1 = DB.get_user_photo(message.from_user.id)
        print(n1)


@dp.message_handler(commands=['excel'])
async def exel(message: types.Message):
    if await admins_test(message):
        DB.make_xlsx()
        with open('build_network.xlsx', "rb") as f:
            await bot.send_document(config.EXEL, f)


@dp.message_handler(commands=['delete_user'])
async def delete_user_command(message: types.Message):
    if await admins_test(message):
        text = message.text.split()
        id_user = int(text[1])
        DB.delete_user(user_id=id_user)


@dp.message_handler(commands=['ban_user'])
async def ban_user_command(message: types.Message):
    if await admins_test(message):
        text = message.text.split()
        id_user = int(text[1])
        key = profile_cls.make_ban(id_user)
        await send_profile(id_user, config.SUPPORT_ID, opening=True, reply_markup=key)


@dp.message_handler(commands=['restart_data'])
async def restart_data(message: types.Message):
    if await admins_test(message):
        try:
            DB.close()
            DB.connect()
            await bot.send_message(config.admin_id, 'Перезагрузка завершена')
        except:
            await bot.send_message(config.admin_id, 'Ошибка перезагрузки')


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=start_bot, on_shutdown=stop_bot, skip_updates=False)
