import asyncio
from aiogram import types
from middlewares import ThrottlingMiddleware
from loader import *
import Markup


async def start_bot(dp):
    try:
        await bot.send_message(str(config.admin_id), 'Бот запущен')
    except:
        pass
    await setup(dp)

    scheduler.add_job(make_dump, 'cron',
                      day_of_week='mon-sun',
                      hour=config.hour_scheduler,
                      minute=config.minute_scheduler + 6)
    # https://telegra.ph/Zapusk-funkcij-v-bote-po-tajmeru-11-28
    scheduler.start()


async def stop_bot(dp):
    """ Выключение бота """
    DB.close()
    await bot.send_message(str(config.admin_id), 'Бот выключен')


async def setup(dp: Dispatcher):
    dp.middleware.setup(ThrottlingMiddleware())


async def admins_test(message):
    """ Проверка id на админа  """
    if message.from_user.id in config.admins_list:
        return True
    else:
        return False


async def make_dump():
    mess = DB.backup()
    if mess:
        with open('backup.db', "rb") as f:
            await bot.send_document(config.DUMP_ID, f)
    else:
        bot.send_message(config.DUMP_ID, f"Ошибка при резервном копировании: \n {mess}")


async def make_contact(user_id):
    profiles_list = DB.get_list_id_acs()
    position = DB.get_user_position(user_id)
    try:
        if len(profiles_list) <= position:
            await bot.send_message(user_id, "Пока всё, вы просмотрели всех пользователей. \n"
                                            "Можете подождать, пока зарегистрируются новые пользователи, "
                                            "или просмотреть все профили заново \n/restart")
        else:
            id_profile = profiles_list[position]
            if id_profile != user_id:
                DB.update_in_user(user_id, 'position', position + 1)
                key = profile_cls.view(id_profile)
                await send_profile(id_profile, user_id, opening=False, reply_markup=key)

            elif id_profile == user_id:
                DB.update_in_user(user_id, 'position', position + 2)
                if len(profiles_list) > position+1:
                    id_profile = profiles_list[position + 1]
                    key = profile_cls.view(id_profile+1)
                    await send_profile(id_profile, user_id, opening=False, reply_markup=key)
                else:
                    await bot.send_message(user_id, "Пока всё, вы просмотрели всех пользователей. \n"
                                                    "Можете подождать, пока зарегистрируются новые пользователи, "
                                                    "или просмотреть все профили заново \n/restart")

    except:
        await bot.send_message(user_id, 'Упс, кажется что-то пошло не так, попробуйте еще раз \n/contact')


async def send_profile(id_profile, send_id, opening=True, reply_markup=None):
    """
    id_profile - чей профиль отправляем
    send_id - кому отправляем
    """
    src = DB.get_user_photo(id_profile)
    # print(f'src {src}')
    name = DB.get_user_name(id_profile)
    # print(f'name {name}')
    contact = DB.get_user_contact(id_profile)
    # print(f'contact {contact}')
    description = DB.get_user_description(id_profile)
    # print(f'description {description}')
    if opening:
        mess = f'Имя: {name} \n' \
               f'Связь: {contact} \n' \
               f'Описание: \n{description}'
        with open(src, 'rb') as f:
            await bot.send_photo(send_id, f, caption=mess, reply_markup=reply_markup)
    else:
        mess = f'Имя: {name} \n' \
               f'Описание: \n{description}'
        with open(src, 'rb') as f:
            await bot.send_photo(send_id, f, caption=mess, reply_markup=reply_markup)


