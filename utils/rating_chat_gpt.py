import traceback
from os import getenv
from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

from db.repository import users_repository

load_dotenv(find_dotenv("../.env"))
api_key = getenv("GPT_TOKEN")
assistant_id=getenv("ASSISTANT_ID")

class FitGPT:
    def __init__(self, thread_id):
        self.client = OpenAI(api_key=api_key)
        self.assistant = self.client.beta.assistants.retrieve(assistant_id=assistant_id)
        self.thread_id = thread_id

    async def update_thread_id(self, user_id: int):
        thread = self.client.beta.threads.create()
        self.thread_id = thread.id
        await users_repository.update_thread_id_by_user_id(user_id=user_id, thread_id=self.thread_id)
        return thread

    async def send_message(self, user_id, text: str | None = None, image_bytes = None):
        try:
            if self.thread_id is None:
                thread = await self.update_thread_id(user_id=user_id)
            else:
                thread = self.client.beta.threads.retrieve(thread_id=self.thread_id)
            if text is None and image_bytes is None:
                return None
            elif image_bytes is None:
                content = text
            else:
                if text is None:
                    text = "Вот моя еда"
                image_bytes.seek(0)
                user_file = self.client.files.create(
                    file=("image.png", image_bytes),
                    purpose="vision"
                )
                content = [
                            {
                                "type": "text",
                                "text": text
                            },
                            {
                                "type": "image_file",
                                "image_file": {"file_id": user_file.id}
                            }
                        ]

            thread_message = self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=content,
            )
            run = self.client.beta.threads.runs.create_and_poll(
                thread_id=thread.id,
                assistant_id=self.assistant.id
            )
            if run.status == 'completed':
                messages = self.client.beta.threads.messages.list(
                    thread_id=thread.id
                )
                return messages.data[0].content[0].text.value.replace("**", "").replace('"', "'").replace("#", "")
            else:
                print(run.status)
                return "Произошла непредвиденная ошибка, попробуй еще раз!"
        except:
            return "Произошла непредвиденная ошибка, попробуй еще раз!"
            print(traceback.format_exc())