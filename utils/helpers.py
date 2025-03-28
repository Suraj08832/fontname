import logging
from typing import List, Dict, Any
import asyncio

def setup_logging():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    return logging.getLogger(__name__)

def safe_execute(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logging.error(f"Error executing function {func.__name__}: {str(e)}")
        return None

def create_inline_keyboard(buttons: List[Dict[str, Any]], columns: int = 2) -> List[List[InlineKeyboardButton]]:
    keyboard = []
    row = []
    
    for button in buttons:
        row.append(InlineKeyboardButton(
            text=button['text'],
            callback_data=button['callback_data']
        ))
        
        if len(row) == columns:
            keyboard.append(row)
            row = []
            
    if row:
        keyboard.append(row)
        
    return keyboard

def format_error_message(error: Exception) -> str:
    return f"An error occurred: {str(error)}"

def validate_text(text: str, max_length: int = 100) -> bool:
    if not text or len(text.strip()) == 0:
        return False
    if len(text) > max_length:
        return False
    return True

async def rate_limit(user_id: int, context: Dict[str, Any], limit: int = 5, window: int = 60):
    current_time = asyncio.get_event_loop().time()
    
    if user_id not in context:
        context[user_id] = []
        
    # Remove old timestamps
    context[user_id] = [t for t in context[user_id] if current_time - t < window]
    
    if len(context[user_id]) >= limit:
        return False
        
    context[user_id].append(current_time)
    return True 