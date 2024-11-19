from os import getenv

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv, find_dotenv

storage_bot = MemoryStorage()
storage_admin_bot = MemoryStorage()


load_dotenv(find_dotenv("../.env"))
token_design_level = getenv("MAIN_BOT_TOKEN")
token_admin_bot = getenv("ADMIN_BOT_TOKEN")
channel_id = "-1001906583847"


class InputMessage(StatesGroup):
    enter_time_notification = State()
    contact_us_state = State()
    answer_to_user = State()
    statistic = State()
    enter_message_mailing = State()
    enter_admin_id = State()
    enter_email = State()


start_message_caption = ("Привет! Я - твой персональный фитнес-ассистент 💪\n\nЯ умею рассчитывать калорийность,"
                         " БЖУ и другие полезные показатели твоего рациона по фото или текстовому описанию, а вечером "
                         "отправляю отчет (выключить данную функцию или изменить время отправки можно в меню) ! 🥑"
                         " Также ты можешь обратиться ко мне с любым вопросом на тему похудения, набора массы и фитнеса!"
                         "  \n\n🏋️ Я помогаю, а ты побеждаешь! 🏆\n\nПервые три дня бесплатно! 🔝")

start_message_photo_id = "AgACAgIAAxkBAAMKZvRAcGTWvgUjBRZGhKwX10vMAdAAAn_fMRsYSqBLwSHCZm0aRTgBAAMCAAN4AAM2BA"
sub_photo = "AgACAgIAAxkBAAICtGb752r_NGzTUjDPeAIZFJHJKIxQAAJ45TEbdavhS0pIZIARJdsuAQADAgADeQADNgQ"

import random

hints_and_tips = [
    "🤫 Подсказка!…\n\nЕду лучше фотографировать под прямым углом. Сверху всегда виднее 😉",
    "💡 Лайфхак!…\n\nЕсли вас не устроила оценка фото, вы всегда можете уточнить граммовку или состав блюда 🍏",
    "🤫 Подсказка!…\n\nЕсли хотите оценить продукт в заводской упаковке, лучше сфотографируйте этикетку с составом или КБЖУ 🥫",
    "💡 Совет!…\n\nЕсли фотографируете семейный ужин, можете уточнить что съели именно вы 🫶",
    "🤫 Подсказка!…\n\nЯ могу не только оценить калорийность, но и сам составить рецепт по вашему запросу 📋",
    "🤫 Лайфхак!…\n\nВы можете изменить время ежедневного отчета, для этого используйте соответствующий раздел Меню ↩️",
    "💡 Совет!…\n\nВы можете одним сообщением перечислить все блюда, которые ели за день, чтобы занести их в дневной рацион 🍏"
]

async def get_random_hint():
    return random.choice(hints_and_tips)


async def process_number(num):
    if num.is_integer():
        return int(num)
    else:
        return round(num, 1)


import re


MESSAGE_SPAM_TIMING = 1


async def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if re.match(email_regex, email):
        return True
    else:
        return False