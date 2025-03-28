from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging
from styles.font_styles import generate_fancy_name, generate_example_styles

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    try:
        data = query.data.split(':')
        if len(data) < 2:
            await query.message.reply_text("Invalid button data")
            return
            
        button_type = data[0]
        
        if button_type == 'style':
            if len(data) < 3:
                await query.message.reply_text("Style data incomplete")
                return
                
            style_name = data[1]
            text = data[2]
            
            try:
                styled_text = generate_fancy_name(text)
                await query.message.reply_text(f"Here's your styled text:\n{styled_text}")
            except Exception as e:
                logging.error(f"Error applying style: {str(e)}")
                await query.message.reply_text("Sorry, there was an error applying the style")
                
        elif button_type == 'bio':
            if len(data) < 3:
                await query.message.reply_text("Bio data incomplete")
                return
                
            style_name = data[1]
            text = data[2]
            
            try:
                styled_text = generate_fancy_name(text)
                await query.message.reply_text(f"Here's your styled bio:\n{styled_text}")
            except Exception as e:
                logging.error(f"Error applying bio style: {str(e)}")
                await query.message.reply_text("Sorry, there was an error applying the bio style")
                
        else:
            await query.message.reply_text("Unknown button type")
            
    except Exception as e:
        logging.error(f"Error in button callback: {str(e)}")
        await query.message.reply_text("Sorry, there was an error processing your request") 