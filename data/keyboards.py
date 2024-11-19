from imghdr import tests

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, WebAppInfo, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


main_kb = [
        [KeyboardButton(text="Изменить/отключить время отчета 🧮")],
        [KeyboardButton(text="Статистика на сегодня 📊")],
        [KeyboardButton(text="Связь с менеджером ☎️")]
    ]
main_keyboard = ReplyKeyboardMarkup(keyboard=main_kb, resize_keyboard=True)



# main_keyboard = InlineKeyboardBuilder()
# main_keyboard.row(InlineKeyboardButton(text="Изменить/отключить время отчета 🧮",
#                                        callback_data="edit_activate|delete_notification"))
# main_keyboard.row(InlineKeyboardButton(text="Статистика на сегодня 📊",
#                                        callback_data="day_statistic"))
# main_keyboard.row(InlineKeyboardButton(text="Связь с менеджером ☎️",
#                                        callback_data="connect_manager"))
admin_kb = [
        [KeyboardButton(text='Статистика')],
        [KeyboardButton(text="Сделать рассылку")],
        [KeyboardButton(text="Добавить / удалить админа")]
    ]
admin_keyboard = ReplyKeyboardMarkup(keyboard=admin_kb, resize_keyboard=True)

edit_delete_notification_keyboard = InlineKeyboardBuilder()
edit_delete_notification_keyboard.row(InlineKeyboardButton(text="Изменить время отчета",
                                                           callback_data="edit_notification"))
edit_delete_notification_keyboard.row(InlineKeyboardButton(text="Отключить авто-отчет",
                                                           callback_data="delete_notification"))
edit_delete_notification_keyboard.row(InlineKeyboardButton(text="Отмена", callback_data="cancel"))


edit_activate_notification_keyboard = InlineKeyboardBuilder()
edit_activate_notification_keyboard.row(InlineKeyboardButton(text="Включить автоматическую отправку отчета",
                                                           callback_data="activate_notification"))
edit_activate_notification_keyboard.row(InlineKeyboardButton(text="В меню", callback_data="start_menu"))



menu_keyboard = InlineKeyboardBuilder()
menu_keyboard.row(InlineKeyboardButton(text="В меню", callback_data="start_menu"))

buy_sub_keyboard = InlineKeyboardBuilder()
buy_sub_keyboard.row(InlineKeyboardButton(text="Купить подписку", callback_data="buy_sub"))


new_sub_keyboard = InlineKeyboardBuilder()
new_sub_keyboard.row(InlineKeyboardButton(text="Продлить подписку", callback_data="get_new_sub"))


async def keyboard_for_pay(operation_id: str, url: str, time_limit: int):
    pay_ai_keyboard = InlineKeyboardBuilder()
    pay_ai_keyboard.row(InlineKeyboardButton(text="Оплатить", web_app=WebAppInfo(url=url)))
    pay_ai_keyboard.row(InlineKeyboardButton(text="Оплата произведена",
                                             callback_data=f"is_paid|{operation_id}|{time_limit}"))
    return pay_ai_keyboard


add_delete_admin = InlineKeyboardBuilder()
add_delete_admin.row(InlineKeyboardButton(text="Добавить админа", callback_data="add_admin"))
add_delete_admin.row(InlineKeyboardButton(text="Удалить админа", callback_data="delete_admin"))

choice_bot_stat = InlineKeyboardBuilder()
choice_bot_stat.row(InlineKeyboardButton(text="Количество новых пользователей", callback_data="statistic|new_users"))
choice_bot_stat.row(InlineKeyboardButton(text="Количество всех запросов в GPT", callback_data="statistic|ai_requests"))
choice_bot_stat.row(InlineKeyboardButton(text="Количество запросов с фото в GPT", callback_data="statistic|photo_ai_requests"))
choice_bot_stat.row(InlineKeyboardButton(text="Количество операций по оплате", callback_data="statistic|operations"))
choice_bot_stat.row(InlineKeyboardButton(text="Отмена", callback_data="cancel"))

choice_bot_send = InlineKeyboardBuilder()
choice_bot_send.row(InlineKeyboardButton(text="Рассылка в боте", callback_data="mailing|all_bots"))
choice_bot_send.row(InlineKeyboardButton(text="Отмена", callback_data="cancel"))

cancel_keyboard = InlineKeyboardBuilder()
cancel_keyboard.row(InlineKeyboardButton(text="Отмена", callback_data="cancel"))

back_to_bots_keyboard = InlineKeyboardBuilder()
back_to_bots_keyboard.row(InlineKeyboardButton(text="Назад к выбору ботов", callback_data="back_to_bots"))