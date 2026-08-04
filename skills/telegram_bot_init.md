# Telegram Bot Init

## 說明...
初始化 Telegram Bot 的基本設置，包括設置環境變量、配置日誌記錄以及建立與 Telegram API 的連接。

## 關鍵代碼片段
```python
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

def start(update: Update, context):
    update.message.reply_text('Bot started!')

def main():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    application.run_polling()

if __name__ == '__main__':
    main()
```

## 常見錯誤及避免方法
- **錯誤**: `TELEGRAM_BOT_TOKEN` 未設置，導致連接失敗。
  **解決方法**: 確保在運行環境中設置了 `TELEGRAM_BOT_TOKEN` 環境變量。
- **錯誤**: 權限不足，無法接收更新。
  **解決方法**: 在 Telegram 中確認機器人具有接收消息和命令的權限。