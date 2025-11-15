# ПРЕДУПРЕЖДЕНИЕ - код создан ИИ. я не умею кодить просто
import discord
from discord.ext import commands
import unicodedata
from datetime import timedelta

TOKEN = "token"
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# Порог: 30%+ символов — шрифты → бан
UNICODE_RATIO = 0.3

def is_fancy_char(c):
    """Проверяет: это шрифт? (не кириллица, не латиница, не цифры, не знаки)"""
    code = ord(c)
    # Разрешаем:
    # - ASCII (0–127): a-z, A-Z, цифры, знаки
    # - Кириллица (1024–1279): а-я, А-Я
    # - Расширенная кириллица (1280–1327): ё, Ё и т.д.
    # - Пробелы, эмодзи — НЕ шрифты
    if code <= 127: return False
    if 0x0400 <= code <= 0x052F: return False  # кириллица + расширения
    if code in range(0x1F600, 0x1F650): return False  # эмодзи
    # Всё остальное — шрифты
    return True

def has_fancy_text(text):
    """Есть ли в тексте много шрифтов?"""
    total = len(text)
    if total == 0: return False
    fancy_count = sum(1 for c in text if is_fancy_char(c))
    return fancy_count / total > UNICODE_RATIO

@bot.event
async def on_message(message):
    if message.author.bot: return

    if has_fancy_text(message.content):
        # Нормализуем только для лога
        norm = ''.join(c for c in unicodedata.normalize('NFKD', message.content) 
                      if unicodedata.category(c) != 'Mn')

        await message.delete()
        await message.channel.send(
            f"{message.author.mention} — шрифты запрещены!",
            delete_after=5
        )
        await message.author.timeout(
            discord.utils.utcnow() + timedelta(minutes=1),
            reason="Шрифтовой спам"
        )
        print(f"БАН: {message.author} | {norm[:60]}...")

    await bot.process_commands(message)

bot.run(TOKEN)
