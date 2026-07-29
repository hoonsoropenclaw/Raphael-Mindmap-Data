# telegram_bot_init

## 說明
這是一個基礎的 Telegram Bot 起手式模版。當你需要建立一個 Telegram Bot 時，請直接使用此模版，不需重新查閱官方文件。

## 關鍵程式碼
\\\python
import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Bot has started! (Built from SKILL_CATALOG)')

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'You said: {update.message.text}')

def main():
    token = os.getenv('TG_BOT_TOKEN')
    if not token:
        raise ValueError('TG_BOT_TOKEN not set')
    
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    print('Bot is running...')
    application.run_polling()

if __name__ == '__main__':
    main()
\\\

## 常見錯誤與防坑
- 錯誤 1: RuntimeError: This event loop is already running. 
  - 防坑: 如果在 jupyter/asyncio 裡面執行，不能用 un_polling()，必須自己寫 async loop。但在獨立的 .py 檔中直接使用 un_polling() 即可。
