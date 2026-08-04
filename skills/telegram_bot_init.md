# Telegram Bot Init

## 說明...
使用 python-telegram-bot 套件初始化 Telegram Bot，包括設置 token、命令處理器、事件監聽等。

## 關鍵代碼片段
```python
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello!")

app.add_handler(CommandHandler("start", start))
app.run_polling()
```

## 常見錯誤及避免方法
- **錯誤：未設置 TELEGRAM_BOT_TOKEN 環境變數**
  - **解決方法**：在程式啟動時檢查環境變數是否存在，若不存在則提示用戶並退出程式。
- **錯誤：命令處理器未正確註冊**
  - **解決方法**：確保所有命令處理器都通過 `add_handler` 方法正確註冊，並檢查命令名稱是否正確。