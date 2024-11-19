import asyncio
import datetime
import traceback


from aiogram import Dispatcher, Bot
from data.keyboards import new_sub_keyboard
from db.engine import DatabaseEngine
from db.repository import subscriptions_repository, users_repository, days_repository
from handlers.user_handler import user_router, gpt_router
from settings import storage_bot, token_design_level, sub_photo, process_number
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from utils.rating_chat_gpt import FitGPT

main_bot = Bot(token=token_design_level, parse_mode='html')


async def edit_activation_sub():
    subs = await subscriptions_repository.select_all_subscriptions()
    for sub in subs:
        if (sub.active and
                (datetime.datetime.now() - sub.creation_date > datetime.timedelta(hours=24 * sub.time_limit_subscription))):
            try:
                await subscriptions_repository.deactivate_subscription(sub.id)
                await main_bot.send_photo(
                    caption="К сожалению, пробный период закончился. Необходимо оплатить подписку"
                            " на следующий месяц работы бота, стоимость которой всего 299 рублей 🍭",
                    photo=sub_photo,
                    chat_id=sub.user_id,
                    reply_markup=new_sub_keyboard.as_markup())
            except:
                await main_bot.send_message(chat_id=774127719, text=traceback.format_exc())
                continue


async def end_user_day():
    users = await users_repository.select_all_users()
    time_now = datetime.datetime.now().time()
    for user in users:
        try:
            time_notification = datetime.datetime.strptime(user.notification_time, "%H:%M").time()
            if time_now.hour == time_notification.hour and time_now.minute == time_notification.minute:
                await FitGPT(None).update_thread_id(user.user_id)
                day_number = user.day_now
                day_now = await days_repository.get_day_by_number_day_and_user_id(day_number=user.day_now,
                                                                                  user_id=user.user_id)
                total_calories = day_now.total_calories
                total_protein = day_now.total_protein
                total_fats = day_now.total_fats
                total_carbs = day_now.total_carbs
                if total_calories == 0:
                    try:
                        await main_bot.send_message(text='Кажется, ты не поделился со мной сегодняшним рационом'
                                                         ' 😔\n\nБуду ждать тебя завтра! 🍏',
                                                    chat_id=user.user_id)
                    except:
                        continue
                else:
                    await main_bot.send_message(
                        text=f"Количество набранных тобой калорий за сегодня"
                             f" - <b>{await process_number(total_calories)}</b>"
                        f" \n\n🧮 Данные БЖУ:\n\n﻿🍗"
                        f" белки - <b>{await process_number(total_protein)} грамм</b>\n﻿🧈 жиры"
                        f" - <b>{await process_number(total_fats)}"
                        f" грамм</b>\n﻿🥯 углеводы - <b>{await process_number(total_carbs)} грамм</b>\n\n"
                        f"Если хочешь отключить ежедневное уведомление, сделать это можно в меню ↩️",
                    chat_id=user.user_id)
                await days_repository.add_day(user_id=user.user_id, number_day=day_number + 1)
                await users_repository.update_day_by_user_id(user_id=user.user_id, day=day_number + 1)
        except:
            continue


async def main():
    db_engine = DatabaseEngine()
    await db_engine.proceed_schemas()
    print(await main_bot.get_me())
    await main_bot.delete_webhook(drop_pending_updates=True)
    dp = Dispatcher(storage=storage_bot)
    dp.include_routers(user_router, gpt_router)
    scheduler = AsyncIOScheduler()
    scheduler.add_job(func=edit_activation_sub, trigger="interval", minutes=3, max_instances=20, misfire_grace_time=120)
    scheduler.add_job(func=end_user_day, trigger="cron", second=0, max_instances=20, misfire_grace_time=120)
    scheduler.start()
    await dp.start_polling(main_bot, polling_timeout=3)


if __name__ == "__main__":
    asyncio.run(main())
