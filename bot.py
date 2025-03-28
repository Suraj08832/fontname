import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from styles.font_styles import generate_fancy_name, generate_example_styles
from handlers.button_handler import button_callback
from utils.helpers import setup_logging, safe_execute, create_inline_keyboard, validate_text

# Setup logging
logger = setup_logging()

# Bot token
TOKEN = os.getenv('BOT_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = """
Welcome to the Font Bot! 🎨

I can help you create fancy text styles for your messages. Here's what I can do:

1. Create fancy names with various styles
2. Generate stylish bios
3. Show you different font examples

Use these commands:
/name <text> - Create fancy name styles
/bio <text> - Generate stylish bio
/help - Show this help message

Let's get started! Send me some text to style. 😊
    """
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
Here are all the available commands:

/name <text> - Create fancy name styles
/bio <text> - Generate stylish bio
/help - Show this help message

For example:
/name John
/bio Living life to the fullest
    """
    await update.message.reply_text(help_text)

async def name_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide some text to style. Example: /name John")
        return
        
    text = ' '.join(context.args)
    if not validate_text(text):
        await update.message.reply_text("Please provide valid text (max 100 characters)")
        return
        
    try:
        styled_texts = generate_example_styles(text)
        buttons = []
        
        for i, styled_text in enumerate(styled_texts):
            buttons.append({
                'text': f"Style {i+1}",
                'callback_data': f"style:{i}:{text}"
            })
            
        keyboard = create_inline_keyboard(buttons)
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Here are some style options for your text:",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error in name_command: {str(e)}")
        await update.message.reply_text("Sorry, there was an error processing your request")

async def bio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide some text for your bio. Example: /bio Living life to the fullest")
        return
        
    text = ' '.join(context.args)
    if not validate_text(text):
        await update.message.reply_text("Please provide valid text (max 100 characters)")
        return
        
    try:
        styled_texts = generate_example_styles(text)
        buttons = []
        
        for i, styled_text in enumerate(styled_texts):
            buttons.append({
                'text': f"Bio Style {i+1}",
                'callback_data': f"bio:{i}:{text}"
            })
            
        keyboard = create_inline_keyboard(buttons)
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Here are some style options for your bio:",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error in bio_command: {str(e)}")
        await update.message.reply_text("Sorry, there was an error processing your request")

def main():
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("name", name_command))
    application.add_handler(CommandHandler("bio", bio_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main() 