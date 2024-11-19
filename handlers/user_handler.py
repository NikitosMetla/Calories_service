import asyncio
import datetime
import io
import re

from aiogram import Router, types, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import any_state
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

import settings
from settings import process_number
from data.keyboards import main_keyboard, edit_delete_notification_keyboard, \
    edit_activate_notification_keyboard, new_sub_keyboard, cancel_keyboard, keyboard_for_pay
from db.repository import days_repository, users_repository, admin_repository, subscriptions_repository, \
    eating_repository, ai_requests_repository, operation_repository
from settings import InputMessage

from utils.payment_for_services import create_payment, check_payment
from utils.rating_chat_gpt import FitGPT

user_router = Router()


@user_router.message(F.text == "/connect_manager")
@user_router.message(F.text == "Связь с менеджером ☎️", any_state)
async def contact_us(message: types.Message, state: FSMContext, bot: Bot):
    await state.clear()
        # if not await users_repository.get_user_by_user_id(message.from_user.id):
        #     await users_repository.add_user(user_id=message.from_user.id, username=message.from_user.username)
    new_message = await message.answer(text="Напиши нам волнующий тебя вопрос! Это может быть как пожелания по улучшению"
                                        " бота, так и просьба о помощи с работой с ботом", reply_markup=cancel_keyboard.as_markup())
    await state.set_state(InputMessage.contact_us_state)
    await state.update_data(message_id=new_message.message_id)
    await message.delete()


@user_router.message(lambda message: message.text not in ["Изменить/отключить время отчета 🧮",
                                                         "Статистика на сегодня 📊",
                                                         "Связь с менеджером ☎️",
                                                          "/connect_manager",
                                                          "/start",
                                                          "/edit_or_deactivate_notification",
                                                          "/day_statistic"],
                     InputMessage.contact_us_state)
async def send_user_question(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await state.clear()
    message_id = data.get("message_id")
    await message.answer(text="Твой вопрос в скором времени просмотрит администратор"
                              " и постарается как можно раньше тебе ответить!")
    await bot.delete_message(message_id=message_id, chat_id=message.from_user.id)
    admins = await admin_repository.select_all_admins()
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="Ответить пользователю",
                                      callback_data=f"answer_user|{message.from_user.id}|{message.from_user.username}"))
    for admin in admins:
        try:
            from bot_admin import admin_bot
            await admin_bot.send_message(text=f"Вопрос от пользователя с id: {message.from_user.id},"
                                         f" username: @{message.from_user.username}\n\n<i>{message.text}</i>",
                                         chat_id=admin.admin_id,
                                         reply_markup=keyboard.as_markup())
        except:
            continue


@user_router.message(F.photo, any_state)
async def start_message(message: types.Message, bot: Bot, state: FSMContext):
    await state.clear()
    delete_message = await message.answer_photo(caption="⏳Секунду, анализирую блюдо…",
                                                photo="AgACAgIAAxkBAAMLZvRAsfDQrnVeJ89rF9Z-IRuVL20AAoXfMRsYSqBLS2Smu6RleoMBAAMCAAN4AAM2BA")
    await asyncio.sleep(2)
    second_delete_message = await message.answer(text=await settings.get_random_hint())
    user = await users_repository.get_user_by_user_id(message.from_user.id)
    user_subs = await subscriptions_repository.get_active_subscriptions_by_user_id(user_id=user.user_id)
    if user_subs is not None and len(user_subs) > 0:
        photo_bytes_io = io.BytesIO()
        photo_id = message.photo[-1].file_id
        await bot.download(message.photo[-1], destination=photo_bytes_io)
        user = await users_repository.get_user_by_user_id(message.from_user.id)
        thread_id = user.ai_threat_id
        answer = await FitGPT(thread_id=thread_id).send_message(text=message.caption, image_bytes=photo_bytes_io,
                                                                user_id=message.from_user.id)
        try:
            pattern = re.compile(r"Итого за данный прием пищи: \$\d+(\.\d+)?\$ калорий, \|\d+(\.\d+)?\| грамм"
                                 r" белка, @\d+(\.\d+)?@ грамм жиров и &\d+(\.\d+)?& грамм углеводов")
            if re.search(pattern, answer) or answer.split("\n")[-1].split("$")[-2].isdigit():
                calories = answer.split("\n")[-1].split("$")[-2]
                proteins = answer.split("\n")[-1].split("|")[-2]
                fats = answer.split("\n")[-1].split("@")[-2]
                carbohydrates = answer.split("\n")[-1].split("&")[-2]
                keyboard = InlineKeyboardBuilder()
                keyboard.row(InlineKeyboardButton(text="Внести в свой рацион",
                                                  callback_data=f"enter_calories|{float(calories)}|{float(proteins)}|{float(fats)}"
                                                                f"|{float(carbohydrates)}"))
                await message.reply(text=answer.replace("$", "").replace("|", "").replace("@", "").replace("&", ""),
                                    reply_markup=keyboard.as_markup())
            else:
                await message.reply(text=answer.replace("$", "").replace("|", "").replace("@", "").replace("&", ""))
        except:
            await message.reply(text=answer.replace("$", "").replace("|", "").replace("@", "").replace("&", ""))
        finally:
            await ai_requests_repository.add_request(user_id=message.from_user.id,
                                                     has_photo=True,
                                                     photo_id=photo_id,
                                                     answer_ai=answer)
    else:
        day_user = await days_repository.get_day_by_number_day_and_user_id(user_id=int(user.user_id),
                                                                           day_number=user.day_now)
        if day_user.send_free_message is False:
            photo_bytes_io = io.BytesIO()
            photo_id = message.photo[-1].file_id
            await bot.download(message.photo[-1], destination=photo_bytes_io)
            user = await users_repository.get_user_by_user_id(message.from_user.id)
            thread_id = user.ai_threat_id
            answer = await FitGPT(thread_id=thread_id).send_message(text=message.caption, image_bytes=photo_bytes_io,
                                                                    user_id=message.from_user.id)
            try:
                pattern = re.compile(r"Итого за данный прием пищи: \$\d+(\.\d+)?\$ калорий, \|\d+(\.\d+)?\| грамм"
                                     r" белка, @\d+(\.\d+)?@ грамм жиров и &\d+(\.\d+)?& грамм углеводов")
                if re.search(pattern, answer) or answer.split("\n")[-1].split("$")[-2].isdigit():
                    calories = answer.split("\n")[-1].split("$")[-2]
                    proteins = answer.split("\n")[-1].split("|")[-2]
                    fats = answer.split("\n")[-1].split("@")[-2]
                    carbohydrates = answer.split("\n")[-1].split("&")[-2]
                    keyboard = InlineKeyboardBuilder()
                    keyboard.row(InlineKeyboardButton(text="Внести в свой рацион",
                                                      callback_data=f"enter_calories|{float(calories)}|{float(proteins)}|{float(fats)}"
                                                                    f"|{float(carbohydrates)}"))
                    await message.reply(text=answer.replace("$", "").replace("|", "").replace("@", "").replace("&", ""),
                                        reply_markup=keyboard.as_markup())
                else:
                    await message.reply(text=answer.replace("$", "").replace("|", "").replace("@", "").replace("&", ""))
            except:
                await message.reply(text=answer.replace("$", "").replace("|", "").replace("@", "").replace("&", ""))
            finally:
                await ai_requests_repository.add_request(user_id=message.from_user.id,
                                                         has_photo=True,
                                                         photo_id=photo_id,
                                                         answer_ai=answer)
                await days_repository.update_send_free_message_by_day_id(day_id=day_user.id)
        else:
            await message.answer_photo(caption="К сожалению, период подписки закончился. Необходимо оплатить подписку"
                                      " на следующий месяц работы бота, стоимость которой всего 299 рублей 🍭",
                                       photo=settings.sub_photo,
                                       reply_markup=new_sub_keyboard.as_markup())
    await delete_message.delete()
    await asyncio.sleep(5)
    await second_delete_message.delete()


@user_router.message(F.text == "/start", any_state)
async def start_message(message: types.Message, state: FSMContext, bot: Bot):
    await state.clear()
    user = await users_repository.get_user_by_user_id(message.from_user.id)
    if user is None:
        await users_repository.add_user(user_id=message.from_user.id,
                                        username=message.from_user.username
                                        )
        await days_repository.add_day(user_id=message.from_user.id, number_day=1)
        await subscriptions_repository.add_subscription(user_id=message.from_user.id,
                                                        time_limit_subscription=3,
                                                        active=True,
                                                        trial_sub=True)
    await message.answer_photo(photo=settings.start_message_photo_id,
                                       caption=settings.start_message_caption)
    await asyncio.sleep(3)
    await message.answer(text="Также ты можешь выбрать следующие действия",
                                 reply_markup=main_keyboard)


@user_router.message(F.text == "/day_statistic")
@user_router.message(F.text == "Статистика на сегодня 📊", any_state)
async def get_day_statistic(message: types.Message, state: FSMContext, bot: Bot):
    await state.clear()
    user = await users_repository.get_user_by_user_id(message.from_user.id)
    now_day = await days_repository.get_day_by_number_day_and_user_id(day_number=user.day_now, user_id=message.from_user.id)
    total_calories = now_day.total_calories
    total_protein = now_day.total_protein
    total_fats = now_day.total_fats
    total_carbs = now_day.total_carbs
    if total_calories == 0:
        await message.answer('Если хочешь здесь видеть сводку по своему рациону'
                                        ' за день, просто отправляй мне фото блюд или опиши их! 🍕')
    else:
        await message.answer(f"Количество набранных тобой калорий за сегодня"
                             f"а - <b>{await process_number(total_calories)}</b>"
                             f" \n\n🧮 Данные БЖУ:\n\n﻿🍗"
                             f" белки - <b>{await process_number(total_protein)} грамм</b>\n﻿🧈 жиры"
                             f" - <b>{await process_number(total_fats)}"
                             f" грамм</b>\n﻿🥯 углеводы - <b>{await process_number(total_carbs)} грамм</b>\n\nЕсли хочешь"
                             f" добавить какое-то блюдо за сегодня, просто отправь мне его картинку или описание  📸")
    await message.delete()


@user_router.message(F.text == "/edit_or_deactivate_notification")
@user_router.message(F.text == "Изменить/отключить время отчета 🧮", any_state)
async def get_day_statistic(message: types.Message, state: FSMContext, bot: Bot):
    await state.clear()
    user = await users_repository.get_user_by_user_id(message.from_user.id)
    if user.notification:
        await message.answer("Выбери свои дальнейшие действия",
                                        reply_markup=edit_delete_notification_keyboard.as_markup())
    else:
        await message.answer("Выбери свои дальнейшие действия",
                                        reply_markup=edit_activate_notification_keyboard.as_markup())
    await message.delete()


@user_router.callback_query(F.data == "delete_notification", any_state)
async def get_day_statistic(message: types.CallbackQuery):
    await users_repository.deactivate_notification_by_user_id(user_id=message.from_user.id)
    await message.message.answer("Автоматическая отправка отчета отключена")
    await message.message.answer(text="Отправь мне картинку со съеденной тобой едой для подсчета калорий,"
                                      " напиши свой вопрос по теме питания или выбери свое"
                                      " дальнейшее действие из представленных", reply_markup=main_keyboard)
    await message.message.delete()


@user_router.callback_query(F.data == "cancel", any_state)
async def get_day_statistic(message: types.CallbackQuery, state: FSMContext, bot: Bot):
    await state.clear()
    try:
        await message.message.delete()
    except:
        return


@user_router.callback_query(F.data == "activate_notification", any_state)
async def get_day_statistic(message: types.CallbackQuery):
    await users_repository.activate_notification_by_user_id(user_id=message.from_user.id)
    await message.message.answer("Автоматическая отправка отчета включена")
    await message.message.answer(text="Отправь мне картинку со съеденной тобой едой для подсчета калорий,"
                                      " напиши свой вопрос по теме питания или выбери свое"
                                      " дальнейшее действие из представленных",
                                 reply_markup=main_keyboard)
    try:
        await message.message.delete()
    except:
        return


@user_router.callback_query(F.data == "edit_notification" , any_state)
async def get_day_statistic(message: types.CallbackQuery, state: FSMContext):
    await message.message.delete()
    await message.message.answer("Введи время по Москве, в которое автоматически будет приходить отчет о твоем дне\n\n"
                                 "<b>Например: 23:00</b>")
    await state.set_state(InputMessage.enter_time_notification)


@user_router.message(F.text, InputMessage.enter_time_notification)
async def start_message(message: types.Message, state: FSMContext):
    time_notification = message.text
    try:
        if ((message.text[-3] == ":" and (5 >= len(message.text) > 3) and
                message.text[:-3].isdigit() and message.text[-2:].isdigit()) and
                int(message.text.replace(":", "")) < 2359):
            await users_repository.update_time_notification_by_user_id(user_id=message.from_user.id,
                                                                       time_notification=message.text)
            await message.answer(f"Новое время по Москве({message.text}) установлено для отправки отчета",
                                 reply_markup=main_keyboard)
            await state.clear()
        else:
            await message.answer("Ты неправильно ввел время, попробуй еще раз\n\n"
                                 "<b>Например: 23:00</b>")

    except:
        await message.answer("Ты неправильно ввел время, попробуй еще раз\n\n"
                             "<b>Например: 23:00</b>")


@user_router.callback_query(F.data.startswith("enter_calories|") , any_state)
async def get_day_statistic(message: types.CallbackQuery, state: FSMContext):
    message_data = message.data.split("|")
    new_calories = float(message_data[1])
    protein = float(message_data[2])
    fats = float(message_data[3])
    carbs = float(message_data[4])
    user = await users_repository.get_user_by_user_id(message.from_user.id)
    day = await days_repository.get_day_by_number_day_and_user_id(user_id=int(message.from_user.id), day_number=user.day_now)
    eating_id = await eating_repository.add_eating(user_id=int(message.from_user.id), day_id=day.id, calories=new_calories,
                                                   protein=protein, fats=fats, carbs=carbs)
    await days_repository.update_day_params_by_day_id(day_id=day.id, added_calories=new_calories,
                                                      added_protein=protein, added_fats=fats, added_carbs=carbs)
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="Отменить внесение",
                                      callback_data=f"cancel_adding|{eating_id}|{new_calories}|{protein}|{fats}|{carbs}"))
    await message.message.answer(f"Отлично! Занесли в твой дневной рацион {await process_number(new_calories)} калорий 🍕\n\n"
                                 f" Ты также можешь отменить это действие кнопкой и попросить меня новый расчет,"
                                 f" если появятся правки 🍏",
                                 reply_markup=keyboard.as_markup())
    await message.message.edit_reply_markup()


@user_router.callback_query(F.data.startswith("cancel_adding|") , any_state)
async def get_day_statistic(message: types.CallbackQuery, state: FSMContext):
    message_data = message.data.split("|")
    delete_eating_id = int(message_data[1])
    calories = float(message_data[2])
    protein = float(message_data[3])
    fats = float(message_data[4])
    carbs = float(message_data[5])
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="Да", callback_data=f"full_delete|{delete_eating_id}|{calories}|{protein}|{fats}|{carbs}"))
    keyboard.row(InlineKeyboardButton(text="Нет", callback_data=f"cancel_delete|{delete_eating_id}|{calories}|{protein}|{fats}|{carbs}"))
    await message.message.edit_text(text=f"Ты уверени, что хочешь отменить внесение {await process_number(calories)} калорий?",
                                    reply_markup=keyboard.as_markup())


@user_router.callback_query(F.data.startswith("full_delete|") , any_state)
async def get_day_statistic(message: types.CallbackQuery, state: FSMContext):
    message_data = message.data.split("|")
    delete_eating_id = int(message_data[1])
    calories = float(message_data[2])
    protein = float(message_data[3])
    fats = float(message_data[4])
    carbs = float(message_data[5])
    await eating_repository.delete_eating_by_id(eating_id=delete_eating_id)
    user = await users_repository.get_user_by_user_id(message.from_user.id)
    day_now = await days_repository.get_day_by_number_day_and_user_id(user_id=user.user_id, day_number=user.day_now)
    # await days_repository.update_day_calories_by_day_id(day_id=day_now.id, added_calories=-calories)
    # await days_repository.update_day_protein_by_day_id(day_id=day_now.id, added_protein=-protein)
    await days_repository.update_day_params_by_day_id(day_id=day_now.id, added_calories= -calories,
                                                      added_protein= -protein, added_fats= -fats, added_carbs= -carbs)
    await message.message.edit_text(text=f"Внесение {await process_number(calories)} калорий отменено")
    try:
        await message.message.edit_reply_markup()
    finally:
        return



@user_router.callback_query(F.data.startswith("cancel_delete|") , any_state)
async def get_day_statistic(message: types.CallbackQuery, state: FSMContext):
    message_data = message.data.split("|")
    eating_id = int(message_data[1])
    new_calories = float(message_data[2])
    protein = float(message_data[3])
    fats = float(message_data[4])
    carbs = float(message_data[5])
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="Отменить внесение",
                                      callback_data=f"cancel_adding|{eating_id}|{new_calories}|{protein}|{fats}|{carbs}"))
    await message.message.edit_text(f"Отлично! Занесли в твой дневной рацион {await process_number(new_calories)} калорий 🍕")
    await message.message.edit_reply_markup(reply_markup=keyboard.as_markup())


gpt_router = Router()


@gpt_router.message(lambda message: message.text not in ["Изменить/отключить время отчета 🧮",
                                                         "Статистика на сегодня 📊",
                                                         "Связь с менеджером ☎️",
                                                          "/connect_manager",
                                                          "/start",
                                                          "/edit_or_deactivate_notification",
                                                          "/day_statistic"])
async def enter_ai_question(message: types.Message, state: FSMContext):
    # delete_message = await message.answer(text="⏳Секунду, анализирую твое сообщение…")
    user = await users_repository.get_user_by_user_id(message.from_user.id)
    user_subs = await subscriptions_repository.get_active_subscriptions_by_user_id(user_id=user.user_id)
    if user_subs is not None and len(user_subs) > 0:
        thread_id = user.ai_threat_id
        answer = await FitGPT(thread_id=thread_id).send_message(text=message.text, user_id=message.from_user.id)
        try:
            pattern = re.compile(r"Итого за данный прием пищи: \$\d+(\.\d+)?\$ калорий, \|\d+(\.\d+)?\| грамм"
                                 r" белка, @\d+(\.\d+)?@ грамм жиров и &\d+(\.\d+)?& грамм углеводов")
            if re.search(pattern, answer) or answer.split("\n")[-1].split("$")[-2].isdigit():
                calories = answer.split("\n")[-1].split("$")[-2]
                proteins = answer.split("\n")[-1].split("|")[-2]
                fats = answer.split("\n")[-1].split("@")[-2]
                carbohydrates = answer.split("\n")[-1].split("&")[-2]
                keyboard = InlineKeyboardBuilder()
                keyboard.row(InlineKeyboardButton(text="Внести в свой рацион",
                                                  callback_data=f"enter_calories|{float(calories)}|{float(proteins)}|{float(fats)}"
                                                                f"|{float(carbohydrates)}"))
                await message.reply(text=answer.replace("$", "").replace("|", "").replace("@", "").replace("&", ""),
                                    reply_markup=keyboard.as_markup())
            else:
                await message.reply(text=answer.replace("$", "").replace("|", "").replace("@", "").replace("&", ""))
        except:
            await message.reply(text=answer.replace("$", "").replace("|", "").replace("@", "").replace("&", ""))
        finally:
            await ai_requests_repository.add_request(user_id=message.from_user.id,
                                                     has_photo=False,
                                                     answer_ai=answer)
    else:
        day_user = await days_repository.get_day_by_number_day_and_user_id(user_id=int(user.user_id),
                                                                           day_number=user.day_now)
        if day_user.send_free_message is False:
            thread_id = user.ai_threat_id
            answer = await FitGPT(thread_id=thread_id).send_message(text=message.text, user_id=message.from_user.id)
            try:
                pattern = re.compile(r"Итого за данный прием пищи: \$\d+(\.\d+)?\$ калорий, \|\d+(\.\d+)?\| грамм"
                                     r" белка, @\d+(\.\d+)?@ грамм жиров и &\d+(\.\d+)?& грамм углеводов")
                if re.search(pattern, answer) or answer.split("\n")[-1].split("$")[-2].isdigit():
                    calories = answer.split("\n")[-1].split("$")[-2]
                    proteins = answer.split("\n")[-1].split("|")[-2]
                    fats = answer.split("\n")[-1].split("@")[-2]
                    carbohydrates = answer.split("\n")[-1].split("&")[-2]
                    keyboard = InlineKeyboardBuilder()
                    keyboard.row(InlineKeyboardButton(text="Внести в свой рацион",
                                                      callback_data=f"enter_calories|{float(calories)}|{float(proteins)}|{float(fats)}"
                                                                    f"|{float(carbohydrates)}"))
                    await message.reply(text=answer.replace("$", "").replace("|", "").replace("@", "").replace("&", ""),
                                        reply_markup=keyboard.as_markup())
                else:
                    await message.reply(text=answer.replace("$", "").replace("|", "").replace("@", "").replace("&", ""))
            except:
                await message.reply(text=answer.replace("$", "").replace("|", "").replace("@", "").replace("&", ""))
            finally:
                await ai_requests_repository.add_request(user_id=message.from_user.id,
                                                         has_photo=False,
                                                         answer_ai=answer)
                await days_repository.update_send_free_message_by_day_id(day_id=day_user.id)
        else:
            await message.answer_photo(caption="К сожалению, период подписки закончился. Необходимо оплатить подписку"
                                               " на следующий месяц работы бота, стоимость которой всего 299 рублей 🍭",
                                       photo=settings.sub_photo,
                                       reply_markup=new_sub_keyboard.as_markup())


@user_router.callback_query(F.data == "get_new_sub", any_state)
async def get_day_statistic(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    user = await users_repository.get_user_by_user_id(call.from_user.id)
    if user.email is None:
        await state.set_state(InputMessage.enter_email)
        await call.message.answer("Для проведения оплаты нам понадобиться адрес электронной почты,"
                                  " чтобы направить чек о покупке 🧾\n\nПожалуйста, введи свой email 🍏")
        try:
            await call.message.delete()
        finally:
            return
    payment = await create_payment(user.email)
    await operation_repository.add_operation(operation_id=payment[0], user_id=call.from_user.id, is_paid=False,
                                                     url=payment[1])
    operation = await operation_repository.get_operation_by_operation_id(payment[0])
    keyboard = await keyboard_for_pay(operation_id=operation.id, url=payment[1], time_limit=30)
    await call.message.answer(text=f'Для дальнейше работы ассистента нужно приобрести подписку'
                                 f' за 299 рублей.\n\nПосле проведения платежа нажми на кнопку "Оплата произведена",'
                                 ' чтобы подтвердить платеж', reply_markup=keyboard.as_markup())
    try:
        await call.message.delete()
    finally:
        return


@user_router.message(lambda message: message.text not in ["Изменить/отключить время отчета 🧮",
                                                         "Статистика на сегодня 📊",
                                                         "Связь с менеджером ☎️",
                                                          "/connect_manager",
                                                          "/start",
                                                          "/edit_or_deactivate_notification",
                                                          "/day_statistic"], InputMessage.enter_email)
async def enter_user_email(message: types.Message, state: FSMContext, bot: Bot):
    if await settings.is_valid_email(email=message.text):
        data = await state.update_data()
        await state.clear()
        await message.answer("Отлично, мы сохранили твой email для следующих покупок")
        await asyncio.sleep(1)
        await users_repository.update_email_by_user_id(user_id=message.from_user.id, email=message.text)
        user = await users_repository.get_user_by_user_id(message.from_user.id)
        payment = await create_payment(user.email)
        await operation_repository.add_operation(operation_id=payment[0], user_id=message.from_user.id, is_paid=False,
                                                 url=payment[1])
        operation = await operation_repository.get_operation_by_operation_id(payment[0])
        keyboard = await keyboard_for_pay(operation_id=operation.id, url=payment[1], time_limit=30)
        await message.answer(text=f'Для дальнейше работы ассистента нужно приобрести подписку'
                                       f' за 299 рублей.\n\nПосле проведения платежа нажми на кнопку "Оплата произведена",'
                                       ' чтобы подтвердить платеж', reply_markup=keyboard.as_markup())
        try:
            del_message_id = int(data.get("del_message_id"))
            await bot.delete_message(chat_id=message.from_user.id, message_id=del_message_id)
        except:
            return
    else:
        try:
            data = await state.update_data()
            del_message_id = int(data.get("del_message_id"))
            await bot.delete_message(chat_id=message.from_user.id, message_id=del_message_id)
        except:
            print()
        finally:
            del_message = await message.answer("Введеный тобой email некорректен, попробуй еще раз",
                                               reply_markup=cancel_keyboard.as_markup())
            await state.update_data(del_message_id=del_message.message_id)




@user_router.callback_query(F.data == "delete_notification", any_state)
async def get_day_statistic(message: types.CallbackQuery):
    await users_repository.deactivate_notification_by_user_id(user_id=message.from_user.id)
    await message.message.answer("Автоматическая отправка отчета отключена")
    await message.message.answer(text="Отправь мне картинку со съеденной тобой едой для подсчета калорий,"
                                      " напиши свой вопрос по теме питания или выбери свое"
                                      " дальнейшее действие из представленных", reply_markup=main_keyboard)
    await message.message.delete()


@user_router.callback_query(F.data.startswith("is_paid|"), any_state)
async def check_payment_callback(message: types.CallbackQuery, state: FSMContext, bot: Bot):
    data = message.data.split("|")
    operation_id = data[1]
    user = await users_repository.get_user_by_user_id(message.from_user.id)
    operation = await operation_repository.get_operation_info_by_id(int(operation_id))
    payment_id = operation.operation_id
    if await check_payment(payment_id):
        await operation_repository.update_paid_by_operation_id(payment_id)
        date_now = datetime.datetime.now()
        await subscriptions_repository.add_subscription(user_id=message.from_user.id,
                                                        trial_sub=False,
                                                        time_limit_subscription=30,
                                                        active=True)
        if not user.donate:
            await users_repository.update_donate_by_user_id(user_id=message.from_user.id)
        await message.message.delete()
        await message.message.answer("Подписка успешно оформлена ✅")
    else:
        try:
            payment = await operation_repository.get_operation_by_operation_id(payment_id)
            keyboard = await keyboard_for_pay(operation_id=operation_id, url=payment.url, time_limit=30)
            await message.message.edit_text("Пока мы не видим, чтобы оплата была произведена( Погоди"
                                            " еще немного времени и убедись,"
                                            " что ты действительно произвел оплату. Если что-то пошло не так, свяжись"
                                            " с нами с помощью команды /connect_manager",
                                            reply_markup=keyboard.as_markup())
        finally:
            return