import asyncio

from aiogram import Router, types, Bot, F
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import any_state
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot import main_bot
from data.keyboards import admin_keyboard, add_delete_admin, cancel_keyboard, choice_bot_stat, back_to_bots_keyboard
from data.statistic import Statistic
from db.repository import admin_repository, users_repository, ai_requests_repository, operation_repository
from settings import InputMessage
from utils.is_main_admin import is_main_admin
from utils.list_admins_keyboard import Admins_kb

admin_router = Router()


# @admin_router.message(F.video_note, any_state)
# @is_main_admin
# async def admin_cancel(message: types.Message, state: FSMContext, bot: Bot):
#     print(message.video_note.file_id)
#
#
# @admin_router.message(F.photo, any_state)
# @is_main_admin
# async def admin_cancel(message: types.Message, state: FSMContext, bot: Bot):
#     print(message.photo[-1].file_id)


@admin_router.callback_query(Text(text="cancel"), any_state)
@is_main_admin
async def admin_cancel(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    await state.clear()
    await call.message.answer(text="Вы находитесь на стартовой панели, выберите свои дальнейшие действия", reply_markup=admin_keyboard)
    await call.message.delete()


@admin_router.callback_query(Text(startswith="answer_user|"), any_state)
@is_main_admin
async def admin_cancel(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    call_data = call.data.split("|")
    user_id = call_data[1]
    username = call_data[2]
    await call.message.edit_reply_markup()
    delete_message = await call.message.answer(f"Теперь вы отвечаете на вопрос пользователю с id: {user_id}, username: @{username}",
                              reply_markup=cancel_keyboard.as_markup())
    await state.set_state(InputMessage.answer_to_user)
    await state.update_data(user_id=user_id, username=username, delete_message_id=delete_message.message_id)


@admin_router.message(F.text, InputMessage.answer_to_user)
@is_main_admin
async def admin_cancel(message: types.Message, state: FSMContext, bot: Bot):
    state_data = await state.get_data()
    delete_message_id = state_data.get("delete_message_id")
    await bot.edit_message_reply_markup(chat_id=message.from_user.id, message_id=delete_message_id)
    text_to_user = (f"Ответ от администратора:\n\n{message.text}\n\nЕсли у тебя остались вопросы,"
                    f" то напиши мне в личку: @{message.from_user.username}")
    await main_bot.send_message(chat_id=state_data.get("user_id"), text=text_to_user)
    await message.answer("Ваш ответ успешно отправлен пользователю!")
    await state.clear()



@admin_router.callback_query(Text(text="back_to_bots"), InputMessage.statistic)
@is_main_admin
async def admin_cancel(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    await call.message.edit_text(text="Выберите раздел, о котором хотите посмотреть статистику📊",
                                 reply_markup=choice_bot_stat.as_markup())


@admin_router.callback_query(Text(text="back_to_bots"))
@is_main_admin
async def admin_cancel(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    await call.message.edit_text(text="Выберите бота, через которого хотите сделать рассылку✉️",
                                 reply_markup=choice_bot_stat.as_markup())


@admin_router.message(Text(text="/start"), any_state)
@is_main_admin
async def admin_start(message: types.Message, state: FSMContext, bot: Bot):
    await state.clear()
    await message.delete()
    await message.answer(text="Это Админ бот проекта FitsAi. С помощью него вы можете получать статистику,"
                              " а также делать дополнительные рассылки по пользователям🤖", reply_markup=admin_keyboard)


@admin_router.message(Text(text="Статистика"))
@is_main_admin
async def choice_bot_for_stat(message: types.Message, state: FSMContext, bot: Bot):
    await state.clear()
    await state.set_state(InputMessage.statistic)
    await message.answer(text="Выберите раздел, о котором хотите посмотреть статистику📊",
                         reply_markup=choice_bot_stat.as_markup())


@admin_router.callback_query(Text(startswith="statistic|"), InputMessage.statistic)
@is_main_admin
async def get_stat(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    service = call.data.split("|")[-1]
    if service == "new_users":
        users = await users_repository.select_all_users()
        stat = Statistic(users=users)
        try:
            stat_all = await stat.get_users_all_statistic()
            stat_day = await stat.get_users_statistic_by_timedelta(time_delta=1)
            stat_month = await stat.get_users_statistic_by_timedelta(time_delta=30)
        except:
            stat_all = 0
            stat_day = 0
            stat_month = 0
        text_message = (f"Количество новых пользователей:\n\n"
                        f"Статистика за день: <b>{stat_day}</b>\n"
                        f"Статистика за месяц: <b>{stat_month}</b>\n"
                        f"Статистика за все время <b>{stat_all}</b>")
        await call.message.edit_text(text=text_message,
                                     reply_markup=back_to_bots_keyboard.as_markup())
    elif service == "ai_requests":
        requests = await ai_requests_repository.select_all_requests()
        stat = Statistic(ai_requests=requests)
        try:
            stat_all = await stat.get_ai_requests_all_statistic()
            stat_day = await stat.get_ai_requests_statistic_by_timedelta(time_delta=1)
            stat_month = await stat.get_ai_requests_statistic_by_timedelta(time_delta=30)
        except:
            stat_all = 0
            stat_day = 0
            stat_month = 0
        text_message = (f"Количество всех запросов к GPT:\n\n"
                        f"Статистика за день: <b>{stat_day}</b>\n"
                        f"Статистика за месяц: <b>{stat_month}</b>\n"
                        f"Статистика за все время <b>{stat_all}</b>")
        await call.message.edit_text(text=text_message,
                                     reply_markup=back_to_bots_keyboard.as_markup())
    elif service == "photo_ai_requests":
        photo_requests = await ai_requests_repository.select_all_photo_requests()
        stat = Statistic(photo_ai_requests=photo_requests)
        try:
            stat_all = await stat.get_photo_ai_requests_all_statistic()
            stat_day = await stat.get_requests_with_photo_by_timedelta(time_delta=1)
            stat_month = await stat.get_requests_with_photo_by_timedelta(time_delta=30)
        except:
            stat_all = 0
            stat_day = 0
            stat_month = 0
        text_message = (f"Количество всех запросов с фото к GPT:\n\n"
                        f"Статистика за день: <b>{stat_day}</b>\n"
                        f"Статистика за месяц: <b>{stat_month}</b>\n"
                        f"Статистика за все время <b>{stat_all}</b>")
        await call.message.edit_text(text=text_message,
                                     reply_markup=back_to_bots_keyboard.as_markup())
    else:
        operations = await operation_repository.select_all_operations()
        stat = Statistic(operations=operations)
        try:
            stat_all = await stat.get_operations_all_statistic()
            stat_day = await stat.get_operations_statistic_by_timedelta(time_delta=1)
            stat_month = await stat.get_operations_statistic_by_timedelta(time_delta=30)
        except:
            stat_all, stat_day, stat_month = [0, 0], [0, 0], [0, 0]
        text_message = (f"Количество операций:\n\n"
                        f"Статистика за день: <b>{stat_day[0]}</b> из которых были оплачены <b>{stat_day[1]}</b>\n"
                        f"Статистика за месяц: <b>{stat_month[0]}</b> из которых были оплачены <b>{stat_month[1]}</b>\n"
                        f"Статистика за все время <b>{stat_all[0]}</b> из которых были оплачены <b>{stat_all[1]}</b>\n")
        await call.message.edit_text(text=text_message,
                                     reply_markup=back_to_bots_keyboard.as_markup())



@admin_router.message(Text(text="Сделать рассылку"))
@is_main_admin
async def new_mailing(message: types.Message, state: FSMContext, bot: Bot):
    await state.clear()
    message = await message.answer(text="Напиши сообщение, которое разошлется пользователям",
                                   reply_markup=cancel_keyboard.as_markup())
    await state.set_state(InputMessage.enter_message_mailing)
    await state.update_data(message_id=message.message_id)


@admin_router.message(F.text, InputMessage.enter_message_mailing)
@is_main_admin
async def enter_message_mailing(message: types.Message, state: FSMContext, bot: Bot):
    # if filename == "all_bots":
    state_data = await state.get_data()
    message_id = state_data.get("message_id")
    users = await users_repository.select_all_users()
    for user in users:
        try:
            await main_bot.send_message(chat_id=user.user_id, text=message.text)
        except:
            continue
    await message.answer(text="Ваша рассылка отправлена всем пользователям бота", reply_markup=admin_keyboard)
    await bot.delete_message(message_id=message_id, chat_id=message.from_user.id)
    await state.clear()


@admin_router.message(Text(text="Добавить / удалить админа"))
@is_main_admin
async def add_or_delete_admin(message: types.Message, state: FSMContext, bot: Bot):
    await state.clear()
    await message.answer(text="Выберите свои дальнейшие действия", reply_markup=add_delete_admin.as_markup())


@admin_router.callback_query(Text(text="add_admin"))
@is_main_admin
async def enter_new_admin_id(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    await call.message.edit_text(text="Отлично, теперь введи telegram id нового админа! Учти,"
                                      " что у нового админа должен быть чат с данным ботом",
                                 reply_markup=cancel_keyboard.as_markup())
    await state.set_state(InputMessage.enter_admin_id)


@admin_router.callback_query(Text(text="delete_admin"))
@is_main_admin
async def delete_old_admin(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    keyboard = await Admins_kb().generate_list()
    await call.message.edit_text(text="Отлично, теперь выбери из представленных админов, которого хочешь удалить",
                                 reply_markup=keyboard.as_markup())


@admin_router.callback_query(Text(startswith="admin|"))
@is_main_admin
async def actions_admin(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    admin_id = call.data.split("|")[1]
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="Удалить админа", callback_data=f"delete|{admin_id}"))
    keyboard.row(InlineKeyboardButton(text="Отмена", callback_data=f"cancel"))
    await call.message.edit_text(text="Выбери свои дальнейшие действия с админом!",
                                 reply_markup=keyboard.as_markup())


@admin_router.callback_query(Text(startswith="delete|"))
@is_main_admin
async def choice_delete_admin(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    admin_id = call.data.split("|")[1]
    await admin_repository.delete_admin_by_admin_id(int(admin_id))
    await call.message.answer(text=f"Отлично, вы удалили аднима с telegram id {admin_id},"
                                   f" выберите свои дальнейшие действия!", reply_markup=admin_keyboard)
    await call.message.delete()


@admin_router.message(F.text, InputMessage.enter_admin_id)
@is_main_admin
async def add_mew_admin(message: types.Message, state: FSMContext, bot: Bot):
    try:
        message_admin = await bot.send_message(chat_id=message.text, text="Вас добавили в данного бота, как админа!")
        await admin_repository.add_admin(admin_id=int(message.text), username=message_admin.chat.username)
        await message.answer(text="Отлично, вы успешно добавили нового админа!", reply_markup=admin_keyboard)
        await message.delete()
        await state.clear()
    except:
        await message.answer(text="Данного telegram id не существует или у нового админа нет чата с ботом, убедитесь"
                                  " в корректности данных и попробуйте снова!",
                             reply_markup=cancel_keyboard.as_markup())
