# 🥗 Telegram Бот для Учёта Калорий с AI-Ассистентом

## 📌 Описание проекта

Данный Telegram-бот помогает вести учёт употреблённых калорий, анализирует рацион и даёт рекомендации с помощью AI-ассистента ChatGPT.

## 🚀 Функциональные возможности

- Учет калорий (обработка текста и фото)
- Отчёты о статистике за день, неделю, месяц
- AI-анализ продуктов и блюд
- Автоматические напоминания
- Оплачиваемые подписки (YooKassa)
- Административные возможности

## 🌐 Запуск проекта

### 1. Склонируйте репозиторий
```bash
git clone https://github.com/NikitosMetla/Calories_service.git
cd Calories_service
```

### 2. Установка зависимостей
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

### 3. Запуск ботов
```bash
python main_bot.py
python admin_bot.py
```

## 🔧 Переменные окружения (`.env`)

```ini
MAIN_BOT_TOKEN=your_telegram_bot_token
ADMIN_BOT_TOKEN=your_admin_bot_token
SECRET_KEY=your_secret_key
SHOP_ID=your_shop_id
GPT_TOKEN=your_openai_api_key
POSTGRES_DB=calories_db
ASSISTANT_ID=assistant_id
POSTGRES_USER=db_user
POSTGRES_PASSWORD=db_password
POSTGRES_PORT=5432
POSTGRES_HOST=db_host
```

## 💪 Используемые технологии
- **Python 3.10+**
- **Aiogram 3.0.0b7**
- **OpenAI API**
- **PostgreSQL + SQLAlchemy**
- **Asyncpg**
- **YooKassa API**

## 🎲 `requirements.txt`
```ini
SQLAlchemy==2.0.30
python-dotenv==1.0.0
aiogram==3.0.0b7
requests==2.32.3
yookassa==3.1.0
APScheduler~=3.10.4
openai~=1.46.1
```

## 💬 Обратная связь

📧 Email: your-email@example.com  
👉 Telegram: [@yourusername](https://t.me/yourusername)  
📚 GitHub: [NikitosMetla](https://github.com/NikitosMetla)  

