from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_IDS = [12345678]  # Ваши ID через запятую
    DB_URL = "sqlite:///database.db"  # Для PostgreSQL: postgresql://user:pass@localhost/dbname

settings = Settings()