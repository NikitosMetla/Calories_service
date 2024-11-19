import asyncio
import time
import traceback
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from bot_admin import admin_bot
from db.repository import users_repository, admin_repository
from loader import logger
from settings import MESSAGE_SPAM_TIMING


class MessageSpamMiddleware(BaseMiddleware):
    def __init__(self, debug: bool = False):
        self.storage = {}
        self.debug = debug
        if self.debug:
            print("MessageSpamMiddleware initialized with debugging enabled.")

    def log(self, message: str) -> None:
        """Helper method to print logs if debugging is enabled."""
        if self.debug:
            print(message)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        admins = await admin_repository.select_all_admins()
        try:
            # Получение данных о пользователе
            user_data = await users_repository.get_user_by_tg_id(user_id=user_id)
            data['user_data'] = user_data

            # Если пользователь новый, добавляем его в базу данных и логируем
            if not user_data:
                await users_repository.add_user(user_id=user_id, username=event.from_user.username)
                for admin in admins:
                    await admin_bot.send_message(
                        chat_id=admin.admin_id,
                        text=f"<b>💜 Зарегистрирован новый пользователь:\n"
                             f"🔑 Telegram ID: <code>{user_id}</code>\n"
                             f"👤 Username: @{event.from_user.username}</b>"
                    )
                logger.log("JOIN", f"{user_id} | @{event.from_user.username}")
                self.log(f"New user registered: user_id={user_id}, username=@{event.from_user.username}")

            # Проверяем пользователя на спам
            check_user = self.storage.get(user_id)
            if check_user:
                if check_user['spam_block']:
                    self.log(f"Spam block active for user_id={user_id}, ignoring message.")
                    return

                if time.time() - check_user['timestamp'] <= MESSAGE_SPAM_TIMING:
                    self.storage[user_id]['timestamp'] = time.time()
                    self.storage[user_id]['spam_block'] = True
                    await event.answer(f'<b>Обнаружена подозрительная активность.</b>')
                    logger.log('SPAM', user_id)
                    self.log(f"Spam detected for user_id={user_id}, blocking temporarily.")
                    await asyncio.sleep(MESSAGE_SPAM_TIMING)
                    self.storage[user_id]['spam_block'] = False
                    return

            # Обновляем таймстамп и сбрасываем блокировку на спам
            self.storage[user_id] = {'timestamp': time.time(), 'spam_block': False}
            self.log(f"Updated storage for user_id={user_id}: {self.storage[user_id]}")

            # Вызываем основной хендлер
            return await handler(event, data)

        except Exception as e:
            self.log(f"Error while processing message for user_id={user_id}: {e}")
            try:
                for admin in admins:
                    await admin_bot.send_message(
                        chat_id=admin.admin_id,
                        text=f'<b>🚫 Ошибка в обработке сообщения: {traceback.format_exc()}</b>'
                    )
            except Exception as log_error:
                self.log(f"Failed to send error log to channel: {log_error}")

        finally:
            self.log(f"Final storage state for user_id={user_id}: {self.storage.get(user_id, 'No data')}")

