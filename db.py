import config
import sqlite3
import datetime
from xlsxwriter.workbook import Workbook
import os


class BotDB:

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.name_db = db_file
        self.session_date = datetime.datetime.now(tz=config.tz).date()

    def user_exists(self, user_id):
        """Проверяем, есть ли пользователь БД True/False"""
        result = self.cursor.execute("SELECT `id` FROM `user` WHERE `telegram_id` = ?", (user_id,))
        return bool(len(result.fetchall()))

    def user_ban_exists(self, user_id):
        result = self.cursor.execute("SELECT `ban` FROM `user` WHERE `telegram_id` = ?", (user_id,))
        result = result.fetchall()
        if type(result) == list:
            return bool(result[0][0])
        else:
            print(result)

    def all_list_user_id(self):
        """ Достает список всех пользователей """
        result = self.cursor.execute("SELECT `telegram_id` FROM `user`")
        return [x[0] for x in result.fetchall()]

    def make_ban(self, user_id, yes=True):
        """ Бан или разбан по id """
        if yes:
            self.cursor.execute('UPDATE user SET ban = True WHERE telegram_id = ?', (user_id,))
        else:
            self.cursor.execute('UPDATE user SET ban = False WHERE telegram_id = ?', (user_id,))

        return self.conn.commit()

    def new_row_user(self, telegram_id, photo, name, contact, description):
        """Добавляем нового пользователя в БД"""
        self.cursor.execute("INSERT INTO `user` (`telegram_id`, `photo`, `name`, `contact`, `description`) VALUES (?, ?, ?, ?, ?)",
                            (telegram_id, photo, name, contact, description))
        return self.conn.commit()

    def get_list_id_acs(self):
        """ Достает список всех пользователей по порядку возрастания ID"""
        result = self.cursor.execute("SELECT `telegram_id` FROM `user` WHERE ban != True ORDER BY id ASC")
        return [x[0] for x in result.fetchall()]

    def update_in_user(self, user_id, col_name, value):
        """ Изменяет значения в user по id """
        self.cursor.execute(f'UPDATE user SET {col_name} = ? WHERE telegram_id = ?',
                            (value, user_id, ))
        return self.conn.commit()

    def get_user_id(self, id_key):
        """ Достаем user_id юзера в базе по его id"""
        result = self.cursor.execute("SELECT `telegram_id` FROM `user` WHERE `id` = ?", (id_key,))
        return result.fetchone()[0]

    def get_user_photo(self, user_id):
        result = self.cursor.execute("SELECT `photo` FROM `user` WHERE `telegram_id` = ?", (user_id,))
        return result.fetchone()[0]

    def get_user_name(self, user_id):
        result = self.cursor.execute("SELECT `name` FROM `user` WHERE `telegram_id` = ?", (user_id,))
        result = result.fetchone()[0]
        return result

    def get_user_contact(self, user_id):
        result = self.cursor.execute("SELECT `contact` FROM `user` WHERE `telegram_id` = ?", (user_id,))
        result = result.fetchone()[0]
        return result

    def get_user_description(self, user_id):
        result = self.cursor.execute("SELECT `description` FROM `user` WHERE `telegram_id` = ?", (user_id,))
        result = result.fetchone()[0]
        return result

    def get_user_position(self, user_id):
        result = self.cursor.execute("SELECT `position` FROM `user` WHERE `telegram_id` = ?", (user_id,))
        result = result.fetchone()[0]
        return result

    def backup(self):
        backup_con = sqlite3.connect('backup.db')
        try:
            with backup_con:
                self.conn.backup(backup_con, pages=3)
            mess = True
        except sqlite3.Error as error:
            mess = error
        finally:
            if (backup_con):
                backup_con.close()
        return mess

    def delete_user(self, user_id):
        """ Удаление по telegram_id """
        path = self.get_user_photo(user_id)
        if os.path.isfile(path):
            os.remove(path)
        self.cursor.execute(f"DELETE FROM user WHERE telegram_id = {user_id}")
        return self.conn.commit()

    def close(self):
        """ Закрываем соединение с БД """
        self.conn.close()

    def connect(self):
        """ Подключаемся к БД """
        self.conn = sqlite3.connect(self.name_db)
        self.cursor = self.conn.cursor()

    def make_xlsx(self):
        workbook = Workbook('build_network.xlsx')
        worksheet = workbook.add_worksheet()
        mysel = self.cursor.execute("SELECT * FROM user")
        for i, row in enumerate(mysel):
            for j, value in enumerate(row):
                worksheet.write(i, j, value)
        workbook.close()





