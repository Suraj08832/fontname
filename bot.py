import logging
import os
import random
import string
import unicodedata
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import re
# Add these imports for web server
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot token
TOKEN = os.environ.get('TOKEN', '8033666584:AAESfSuR7uaPLSpjgzM65rR2My8Oqfon1wo')

# Special characters for fancy fonts
SPECIAL_CHARS = [
    '𐏓', '𝅥', '𝆬', '꯭', 'ᷟ', '𝐣', '➥', '𝗭', '𝗲', '𝗳', '𝗿', '𝗼', '𝗻',
    '🔥', '❰', '⎯', 'ꭗ', '𝕯', '𝕰', '𝕱', '𝕲', '𝕳', '𝕴', '𝕵', '𝕶', '𝕷',
    '𝕸', '𝕹', '𝕺', '𝕻', '𝕼', '𝕽', '𝕾', '𝕿', '𝖀', '𝖁', '𝖂', '𝖃', '𝖄', '𝖅',
    '꧁', '༺', '༒', '᭄', '࿐', '⃟', '⃤', '⃢', '⃠', '★', '✰', '☆', '✫', '✬', '✭', '✮', '✯',
    '✩', '✪', '✦', '✧', '✱', '✲', '✵', '✶', '✷', '✸', '❦', '❧', '☙', '♞', '♠', '♥',
    '♦', '♣', '☢', '☣', '⚔', '⚒', '⚚', '⚛', '⚜', '⚝', '✿', '❀', '❁',
    '🍁', '💫', '⚡', '🌟', '⭐', '✨', '🌠', '🌌', '🔆', '💎', '💠', '💙', '❄️', '🌺', '🌼', '🌻',
    '٭', '𝆹', '𝅥', '𝅲', '༎ࠫ', '𝆺', '𔘓', '𖥫', '•◡̈⃝', '⃨', '⃖', '⃯', '⃗', '͟', '⃪', '•◡̈⃝', '🚩',
    '🍃', '↉', '</𝟑', '❛', '𝁘ໍ', '♡', '𝙃', '𝜩', '༗', '🥀', '𝚴', '❍', '𝚩'
]

# Connector chars
CONNECTORS = ['‌➥‌', '‌꯭', ' ‌⎯꯭ ', ' ꭗ‌ ', ' ‌🔥❰⎯꯭ ', '⚜️', '✦', '➤', '→', '⇨', '⇒', '⊰', '⊱',
             ' ⁀➴', '✧═══', '×͜×', '✧★', '⎯❅⎯', '⟫', '⟪', '┊', '❥', '⇝', '⇜', '☯',
             '⋆⎯꯭̽', '𝅃꯭᳚', '𝆺𝅥༎ࠫ', '༎ࠫ٭⃪꯭💙', '𖥫꯭', '⎯꯭̽🔥', ', ~ ', ' ♡ ', '༗🥀']

# Combining characters for extra styling
COMBINING_CHARS = ["\u0301", "\u0302", "\u0303", "\u0304", "\u0305", "\u0306", "\u0307", "\u0308", "\u0309", "\u030A", "\u030B", "\u030C", "\u030D", "\u030E", "\u030F", "\u0310", "\u0311", "\u0312", "\u0313", "\u0314", "\u0315", "\u031A", "\u033E", "\u033F", "\u0340", "\u0341", "\u0342", "\u0343", "\u0344", "\u0346", "\u034A", "\u034B", "\u034C", "\u0350", "\u0351", "\u0352", "\u0357", "\u0358", "\u035B", "\u035D", "\u035E", "\u035F", "\u0360", "\u0361", "\u0362", "\u0363", "\u0364", "\u0365", "\u0366", "\u0367", "\u0368", "\u0369", "\u036A", "\u036B", "\u036C", "\u036D", "\u036E", "\u036F", "\u0653", "\u0654", "\u0655", "\u0656"]

# Different font styles for characters
FONT_STYLES = {
    # 1. Bold
    'bold': lambda c: chr(ord('𝗔') + ord(c) - ord('A')) if 'A' <= c <= 'Z' else chr(ord('𝗮') + ord(c) - ord('a')) if 'a' <= c <= 'z' else c,
    
    # 2. Italic
    'italic': lambda c: chr(ord('𝘈') + ord(c) - ord('A')) if 'A' <= c <= 'Z' else chr(ord('𝘢') + ord(c) - ord('a')) if 'a' <= c <= 'z' else c,
    
    # 3. Script
    'script': lambda c: chr(ord('𝓐') + ord(c) - ord('A')) if 'A' <= c <= 'Z' else chr(ord('𝓪') + ord(c) - ord('a')) if 'a' <= c <= 'z' else c,
    
    # 4. Double-struck
    'double_struck': lambda c: chr(ord('𝔸') + ord(c) - ord('A')) if 'A' <= c <= 'Z' else chr(ord('𝕒') + ord(c) - ord('a')) if 'a' <= c <= 'z' else c,
    
    # 5. Fraktur
    'fraktur': lambda c: chr(ord('𝕬') + ord(c) - ord('A')) if 'A' <= c <= 'Z' else chr(ord('𝖆') + ord(c) - ord('a')) if 'a' <= c <= 'z' else c,
    
    # 6. Monospace
    'monospace': lambda c: chr(ord('𝙰') + ord(c) - ord('A')) if 'A' <= c <= 'Z' else chr(ord('𝚊') + ord(c) - ord('a')) if 'a' <= c <= 'z' else c,
    
    # 7. Bold Italic
    'bold_italic': lambda c: chr(ord('𝘼') + ord(c) - ord('A')) if 'A' <= c <= 'Z' else chr(ord('𝙖') + ord(c) - ord('a')) if 'a' <= c <= 'z' else c,
    
    # 8. Serif Bold
    'serif_bold': lambda c: chr(ord('𝐀') + ord(c) - ord('A')) if 'A' <= c <= 'Z' else chr(ord('𝐚') + ord(c) - ord('a')) if 'a' <= c <= 'z' else c,
    
    # 9. Serif Italic
    'serif_italic': lambda c: chr(ord('𝐴') + ord(c) - ord('A')) if 'A' <= c <= 'Z' else chr(ord('𝑎') + ord(c) - ord('a')) if 'a' <= c <= 'z' else c,
    
    # 10. Serif Bold Italic
    'serif_bold_italic': lambda c: chr(ord('𝑨') + ord(c) - ord('A')) if 'A' <= c <= 'Z' else chr(ord('𝒂') + ord(c) - ord('a')) if 'a' <= c <= 'z' else c,
    
    # 11. Sans Serif
    'sans_serif': lambda c: chr(ord('𝖠') + ord(c) - ord('A')) if 'A' <= c <= 'Z' else chr(ord('𝖺') + ord(c) - ord('a')) if 'a' <= c <= 'z' else c,
    
    # 12. Cursive
    'cursive': lambda c: chr(ord('𝒜') + ord(c) - ord('A')) if 'A' <= c <= 'Z' else c if not 'a' <= c <= 'z' else chr(ord('𝒶') + ord(c) - ord('a')) if c not in 'hklm' else chr(ord('𝒽') + ord(c) - ord('h')),
    
    # 13. Small Caps
    'small_caps': lambda c: c if not 'a' <= c <= 'z' else chr(ord('ᴀ') + ord(c) - ord('a')),
    
    # 14. Bubbles
    'bubbles': lambda c: '🅐🅑🅒🅓🅔🅕🅖🅗🅘🅙🅚🅛🅜🅝🅞🅟🅠🅡🅢🅣🅤🅥🅦🅧🅨🅩'[ord(c.upper()) - ord('A')] if 'A' <= c.upper() <= 'Z' else c,
    
    # 15. Squares
    'squares': lambda c: '🄰🄱🄲🄳🄴🄵🄶🄷🄸🄹🄺🄻🄼🄽🄾🄿🅀🅁🅂🅃🅄🅅🅆🅇🅈🅉'[ord(c.upper()) - ord('A')] if 'A' <= c.upper() <= 'Z' else c,
    
    # 16. Circled
    'circled': lambda c: 'ⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏ'[ord(c.upper()) - ord('A')] if 'A' <= c.upper() <= 'Z' else c,
    
    # 17. Sparkles Style
    'sparkles': lambda c: '✦' + c if c.isalpha() else c,
    
    # 18. Decorative Brackets
    'decorative_brackets': lambda c: '『' + c + '』' if c.isalpha() else c,
    
    # 19. Line Bars
    'line_bars': lambda c: '|' + c + '|' if c.isalpha() else c,
    
    # 20. Aesthetic Style
    'aesthetic': lambda c: c if not c.isalpha() else c.upper(),
    
    # 21. Hearts Style
    'hearts': lambda c: c + '♥' if c.isalpha() else c,
    
    # 22. Rock Dots
    'rock_dots': lambda c: c.translate(str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
                                                   'ÄḄĊḊЁḞĠḦЇJḲḶṀṄÖṖQṚṠṪÜṾẄẌŸŻäḅċḋëḟġḧïjḳḷṁṅöṗqṛṡẗüṿẅẍÿż')),
    
    # 23. Medieval
    'medieval': lambda c: c.translate(str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
                                                  'ǟɮƈɖɛʄɢɦɨʝӄʟʍռօքզʀֆȶʊʋաӼʏʐǟɮƈɖɛʄɢɦɨʝӄʟʍռօքզʀֆȶʊʋաӼʏʐ')),
    
    # 24. Curvy
    'curvy': lambda c: c.translate(str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
                                              'αвcdєfgнιjklмиσpqяsтυvωxүzαвcdєfgнιjklмиσpqяsтυvωxүz')),
    
    # 25. Ancient
    'ancient': lambda c: c.translate(str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
                                                'ልጌርዕቿቻኗዘጎጋጕረሠክዐየዒዪነፕሁሀሠሸሃጊልጌርዕቿቻኗዘጎጋጕረሠክዐየዒዪነፕሁሀሠሸሃጊ')),
    
    # 26. Faux Cyrillic
    'faux_cyrillic': lambda c: c.translate(str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
                                                      'АВСDЕFGНІЈКLМNОРQЯЅТUVWХYZавсdеfgніјкlмnорqяѕтuvwхуz')),
    
    # 27. Math Sans
    'math_sans': lambda c: chr(ord('𝖠') + ord(c) - ord('A')) if 'A' <= c <= 'Z' else chr(ord('𝖺') + ord(c) - ord('a')) if 'a' <= c <= 'z' else c,
    
    # 28. Negative Bubbles
    'negative_bubbles': lambda c: '🅓' if c.upper() == 'D' else '🅔' if c.upper() == 'E' else '🅕' if c.upper() == 'F' else '🅖' if c.upper() == 'G' else '🅗' if c.upper() == 'H' else '🅘' if c.upper() == 'I' else '🅙' if c.upper() == 'J' else '🅚' if c.upper() == 'K' else '🅛' if c.upper() == 'L' else '🅜' if c.upper() == 'M' else '🅝' if c.upper() == 'N' else '🅞' if c.upper() == 'O' else '🅟' if c.upper() == 'P' else '🅠' if c.upper() == 'Q' else '🅡' if c.upper() == 'R' else '🅢' if c.upper() == 'S' else '🅣' if c.upper() == 'T' else '🅤' if c.upper() == 'U' else '🅥' if c.upper() == 'V' else '🅦' if c.upper() == 'W' else '🅧' if c.upper() == 'X' else '🅨' if c.upper() == 'Y' else '🅩' if c.upper() == 'Z' else '🅐' if c.upper() == 'A' else '🅑' if c.upper() == 'B' else '🅒' if c.upper() == 'C' else c,
    
    # 29. Greek Math - 𝚮𝚺𝚺𝚪 style
    'greek_math': lambda c: '𝚺' if c.upper() == 'S' else '𝚻' if c.upper() == 'T' else '𝚼' if c.upper() == 'U' else '𝚽' if c.upper() == 'F' else '𝚾' if c.upper() == 'X' else '𝚿' if c.upper() == 'PS' else '𝛀' if c.upper() == 'O' else '𝚪' if c.upper() == 'G' else '𝚫' if c.upper() == 'D' else '𝚬' if c.upper() == 'E' else '𝚭' if c.upper() == 'Z' else '𝚮' if c.upper() == 'H' else '𝚯' if c.upper() == 'TH' else '𝚰' if c.upper() == 'I' else '𝚱' if c.upper() == 'K' else '𝚲' if c.upper() == 'L' else '𝚳' if c.upper() == 'M' else '𝚴' if c.upper() == 'N' else '𝚵' if c.upper() == 'KS' else '𝚷' if c.upper() == 'P' else '𝚸' if c.upper() == 'R' else '𝚨' if c.upper() == 'A' else '𝚩' if c.upper() == 'B' else '🙹' if c.upper() == 'J' else '🙺' if c.upper() == 'W' else '🙻' if c.upper() == 'Y' else '🙼' if c.upper() == 'Z' else '🙽' if c.upper() == 'X' else '🙾' if c.upper() == 'V' else '🙿' if c.upper() == 'Q' else c,
    
    # 30. Tribal Letters
    'tribal': lambda c: c.translate(str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
                                              'ᎪᎴᏨᏧᏋᎴᎶᏂᎥᏠᏦᏝᎷᏁᎾᏢᏅᏒᏕᎿᏌᏉᏔᎱᎩᏃᎪᎴᏨᏧᏋᎴᎶᏂᎥᏠᏦᏝᎷᏁᎾᏢᏅᏒᏕᎿᏌᏉᏔᎱᎩᏃ')),
    
    # 31. Blocks Font - ℍ𝔼𝔼ℝ style
    'blocks': lambda c: 'ℍ' if c.upper() == 'H' else '𝔼' if c.upper() in 'E' else 'ℝ' if c.upper() == 'R' else c,
    
    # 32. Rounded Bold - 𝗛𝗘𝗘𝗥 style
    'rounded_bold': lambda c: chr(ord('𝗔') + ord(c) - ord('A')) if 'A' <= c <= 'Z' else chr(ord('𝗮') + ord(c) - ord('a')) if 'a' <= c <= 'z' else c,
    
    # 33. Squiggle Font - 𝙃𝙀𝙀𝙍 style
    'squiggle': lambda c: '𝙲' if c.upper() == 'C' else '𝙳' if c.upper() == 'D' else '𝙴' if c.upper() == 'E' else '𝙵' if c.upper() == 'F' else '𝙶' if c.upper() == 'G' else '𝙷' if c.upper() == 'H' else '𝙸' if c.upper() == 'I' else '𝙹' if c.upper() == 'J' else '𝙺' if c.upper() == 'K' else '𝙻' if c.upper() == 'L' else '𝙼' if c.upper() == 'M' else '𝙽' if c.upper() == 'N' else '𝙾' if c.upper() == 'O' else '𝙿' if c.upper() == 'P' else '𝚀' if c.upper() == 'Q' else '𝚁' if c.upper() == 'R' else '𝚂' if c.upper() == 'S' else '𝚃' if c.upper() == 'T' else '𝚄' if c.upper() == 'U' else '𝚅' if c.upper() == 'V' else '𝚆' if c.upper() == 'W' else '𝚇' if c.upper() == 'X' else '𝚈' if c.upper() == 'Y' else '𝚉' if c.upper() == 'Z' else '𝙰' if c.upper() == 'A' else '𝙱' if c.upper() == 'B' else c,
    
    # 34. Kana Style - 𝝨𝝖𝝣𝝙𝝚𝝚𝝥 style
    'kana': lambda c: '𝝨' if c.upper() == 'S' else '𝝖' if c.upper() == 'A' else '𝝣' if c.upper() == 'N' else '𝝙' if c.upper() == 'D' else '𝝚' if c.upper() == 'E' else '𝝥' if c.upper() == 'P' else '𝝧' if c.upper() == 'R' else '𝝩' if c.upper() == 'T' else '𝝪' if c.upper() == 'U' else '𝝟' if c.upper() == 'J' else '𝝗' if c.upper() == 'B' else '𝝘' if c.upper() == 'C' else '𝝜' if c.upper() == 'G' else '𝝝' if c.upper() == 'H' else '𝝞' if c.upper() == 'I' else '𝝠' if c.upper() == 'K' else '𝝡' if c.upper() == 'L' else '𝝢' if c.upper() == 'M' else '𝝤' if c.upper() == 'O' else '𝝦' if c.upper() == 'Q' else '𝝫' if c.upper() == 'V' else '𝝬' if c.upper() == 'W' else '𝝭' if c.upper() == 'X' else '𝝮' if c.upper() == 'Y' else '𝝯' if c.upper() == 'Z' else c,
    
    # 35. Runic Font - ꑛꍟꍟꋪ style
    'runic': lambda c: 'ᛋ' if c.upper() == 'S' else 'ᚢ' if c.upper() == 'U' else 'ᚱ' if c.upper() == 'R' else 'ᚨ' if c.upper() == 'A' else 'ᛃ' if c.upper() == 'J' else 'ᚦ' if c.upper() == 'TH' else 'ᚾ' if c.upper() == 'N' else 'ᛞ' if c.upper() == 'D' else 'ᛖ' if c.upper() == 'E' else 'ᛈ' if c.upper() == 'P' else 'ᛏ' if c.upper() == 'T' else 'ᚹ' if c.upper() == 'W' else 'ᛒ' if c.upper() == 'B' else 'ᚳ' if c.upper() == 'C' else 'ᚷ' if c.upper() == 'G' else 'ᚻ' if c.upper() == 'H' else 'ᛁ' if c.upper() == 'I' else 'ᚲ' if c.upper() == 'K' else 'ᛚ' if c.upper() == 'L' else 'ᛗ' if c.upper() == 'M' else 'ᛟ' if c.upper() == 'O' else 'ᛩ' if c.upper() == 'Q' else 'ᛔ' if c.upper() == 'V' else 'ᛪ' if c.upper() == 'X' else 'ᚤ' if c.upper() == 'Y' else 'ᛎ' if c.upper() == 'Z' else c,
    
    # 36. Asian Style - ん乇乇尺 style
    'asian': lambda c: '丂' if c.upper() == 'S' else 'ﾑ' if c.upper() == 'A' else '刀' if c.upper() == 'N' else 'り' if c.upper() == 'D' else '乇' if c.upper() == 'E' else 'ｱ' if c.upper() == 'P' else '尺' if c.upper() == 'R' else 'ｲ' if c.upper() == 'T' else 'ひ' if c.upper() == 'U' else 'ﾌ' if c.upper() == 'J' else '乃' if c.upper() == 'B' else 'ᄃ' if c.upper() == 'C' else 'ム' if c.upper() == 'G' else 'ん' if c.upper() == 'H' else 'ﾉ' if c.upper() == 'I' else 'ズ' if c.upper() == 'K' else 'ﾚ' if c.upper() == 'L' else 'ﾶ' if c.upper() == 'M' else 'の' if c.upper() == 'O' else 'ゐ' if c.upper() == 'Q' else '√' if c.upper() == 'V' else 'W' if c.upper() == 'W' else '〤' if c.upper() == 'X' else 'ﾘ' if c.upper() == 'Y' else '乙' if c.upper() == 'Z' else c,
    
    # 37. Lowercase Style - нєєя style
    'lowercase': lambda c: c.translate(str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
                                                  'αвcdєfgнιjklмησpqrѕтυvwxyzαвcdєfgнιjklмησpqrѕтυvwxyz')),
    
    # 38. Mixed Case Style - ＨᗴＥᖇ style
    'mixed_case': lambda c: c.translate(str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
                                                   'ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺᗩᗷᑕᗪᗴᖴᘜᕼＩᒍＫＬᗰＮＯＰＱᖇＳＴＵＶＷＸＹＺ')),
    
    # 39. Gothic Style - 𝙃𝙀𝙀𝙍 style
    'gothic': lambda c: '𝔄' if c.upper() == 'A' else '𝔅' if c.upper() == 'B' else 'ℭ' if c.upper() == 'C' else '𝔇' if c.upper() == 'D' else '𝔈' if c.upper() == 'E' else '𝔉' if c.upper() == 'F' else '𝔊' if c.upper() == 'G' else 'ℌ' if c.upper() == 'H' else 'ℑ' if c.upper() == 'I' else '𝔍' if c.upper() == 'J' else '𝔎' if c.upper() == 'K' else '𝔏' if c.upper() == 'L' else '𝔐' if c.upper() == 'M' else '𝔑' if c.upper() == 'N' else '𝔒' if c.upper() == 'O' else '𝔓' if c.upper() == 'P' else '𝔔' if c.upper() == 'Q' else 'ℜ' if c.upper() == 'R' else '𝔖' if c.upper() == 'S' else '𝔗' if c.upper() == 'T' else '𝔘' if c.upper() == 'U' else '𝔙' if c.upper() == 'V' else '𝔚' if c.upper() == 'W' else '𝔛' if c.upper() == 'X' else '𝔜' if c.upper() == 'Y' else 'ℨ' if c.upper() == 'Z' else c,
    
    # 40. Diamonds Style - 𝕳𝕰𝕰𝕽 style
    'diamonds': lambda c: '♦' if c.isalpha() else c,
    
    # 41. Double-Struck Italic - ᕼᗴᗴᖇ style
    'double_struck_italic': lambda c: c.translate(str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
                                                            'ᗩᗷᑕᗪᗴᖴᘜᕼＩᒍＫＬᗰＮＯＰＱᖇＳＴＵＶＷＸＹＺᗩᗷᑕᗪᗴᖴᘜᕼＩᒍＫＬᗰＮＯＰＱᖇＳＴＵＶＷＸＹＺ')),
    
    # 42. Coptic Style - ⲎⲈⲈⲄ style
    'coptic': lambda c: 'Ⲏ' if c.upper() == 'H' else 'Ⲉ' if c.upper() in 'E' else 'Ⲅ' if c.upper() == 'R' else c,
}

# Map style numbers to style names
STYLE_NAMES = {
    1: 'bold',
    2: 'italic',
    3: 'script',
    4: 'double_struck',
    5: 'fraktur',
    6: 'monospace',
    7: 'bold_italic',
    8: 'serif_bold',
    9: 'serif_italic',
    10: 'serif_bold_italic',
    11: 'sans_serif',
    12: 'cursive',
    13: 'small_caps',
    14: 'bubbles',
    15: 'squares',
    16: 'circled',
    17: 'sparkles',
    18: 'decorative_brackets',
    19: 'line_bars',
    20: 'aesthetic',
    21: 'hearts',
    22: 'rock_dots',
    23: 'medieval',
    24: 'curvy',
    25: 'ancient',
    26: 'faux_cyrillic',
    27: 'math_sans',
    28: 'negative_bubbles',
    29: 'greek_math',
    30: 'tribal',
    31: 'blocks',
    32: 'rounded_bold',
    33: 'squiggle',
    34: 'kana',
    35: 'runic',
    36: 'asian',
    37: 'lowercase',
    38: 'mixed_case',
    39: 'gothic',
    40: 'diamonds',
    41: 'double_struck_italic',
    42: 'coptic'
}

# Decorative text transformations
def underline_text(text):
    """Add underline combining characters to text"""
    return ''.join(c + '\u0332' for c in text)

def strikethrough_text(text):
    """Add strikethrough combining characters to text"""
    return ''.join(c + '\u0336' for c in text)

def bubble_wrap(text):
    """Wrap text in bubble-like characters"""
    return f"˗ˏˋ {text} ˎˊ˗"

def star_wrap(text):
    """Wrap text in stars"""
    return f"✧⋆｡°✩ {text} ✩°｡⋆✧"

def dot_wrap(text):
    """Add dots around text"""
    return f"░░ {text} ░░"

def custom_frame(text):
    """Create a custom frame around the text."""
    # Use specific styling for different letters to match the example
    styled_text = ""
    for char in text:
        # Convert to uppercase for consistent styling
        char_upper = char.upper()
        
        # Special styling for specific letters
        if char_upper == 'S':
            styled_text += 'Ｓ'
        elif char_upper == 'U':
            styled_text += 'Ｕ'
        elif char_upper == 'R':
            styled_text += 'ᖇ'
        elif char_upper == 'A':
            styled_text += 'ᗩ'
        elif char_upper == 'J':
            styled_text += 'ᒍ'
        elif 'A' <= char_upper <= 'Z':
            # Fullwidth for other letters
            styled_text += chr(ord('Ａ') + ord(char_upper) - ord('A'))
        else:
            styled_text += char
    
    # Get frame width based on text length
    text_length = len(styled_text)
    padding = max(0, (14 - text_length) // 2)
    
    # Create borders with appropriate width
    top_border = "╭─━━━━━━━━━━━━━━╮"
    bottom_border = "╰─━━━━━━━━━━━━━━╯"
    
    # Apply padding for center alignment
    padded_text = " " * padding + styled_text
    
    return f"{top_border}\n   {padded_text}\n{bottom_border}"

def random_combine_chars(text):
    """Add random combining characters to each letter"""
    result = ""
    for char in text:
        result += char
        # Add 1-3 random combining characters to each letter
        combine_count = random.randint(1, 3)
        for _ in range(combine_count):
            if random.random() < 0.3:  # 30% chance to add combining chars
                result += random.choice(COMBINING_CHARS)
    return result

def prinxe_style(text):
    """Create the '⋆⎯꯭̽𝅃꯭᳚𝆺𝅥༎ࠫ𝆺꯭𝅥𝐏ʀ⃨⃖ι‌ɴ‌¢⃯⃗є͟༎ࠫ٭⃪꯭💙𝆺꯭𝅥𔘓𖥫꯭ •◡̈⃝🚩' style"""
    # Convert to combining character rich text with special styles
    prefix = "⋆⎯꯭̽𝅃꯭᳚𝆺𝅥༎ࠫ𝆺꯭𝅥"
    suffix = "༎ࠫ٭⃪꯭💙𝆺꯭𝅥𔘓𖥫꯭ •◡̈⃝🚩"
    
    # Process the text character by character with special styling
    styled_text = ""
    for i, char in enumerate(text):
        if char.lower() in 'aeiou':  # Special treatment for vowels
            styled_text += char + "⃯⃗"
        elif char.isalpha():
            # First letter gets special treatment
            if i == 0 and char.isupper():
                styled_text += char + "⃨⃖"
            else:
                styled_text += char + "͟"
        else:
            styled_text += char
            
    return f"{prefix}{styled_text}{suffix}"

def elaborate_style(text):
    """Create an elaborate style with multiple decorative elements"""
    # Choose a base font style
    base_style = random.choice(list(FONT_STYLES.values()))
    styled_text = ''.join(base_style(char) if char.isalpha() else char for char in text)
    
    # Add decorative elements
    prefix = ''.join(random.choice(SPECIAL_CHARS) for _ in range(random.randint(2, 4)))
    suffix = ''.join(random.choice(SPECIAL_CHARS) for _ in range(random.randint(2, 4)))
    
    # Add random combining characters
    styled_text = random_combine_chars(styled_text)
    
    return f"{prefix} {styled_text} {suffix}"

def no_option_style(text):
    """Create the '⎯꯭̽🔥𝐍͟σ͟ 𝐎͟ᴘ͟т͟ι͟σ͟η↉꯭🍃' style"""
    prefix = "⎯꯭̽🔥"
    suffix = "↉꯭🍃"
    
    # Process the text character by character with special styling
    styled_text = ""
    for char in text:
        if char.isalpha():
            # Apply special styling to each letter
            if char.isupper():
                styled_char = FONT_STYLES['serif_bold'](char) + "͟"
            else:
                styled_char = FONT_STYLES['serif_italic'](char) + "͟"
            styled_text += styled_char
        else:
            styled_text += char
            
    return f"{prefix}{styled_text}{suffix}"

def nobody_style(text):
    """Create fancy style with decorative brackets"""
    prefix = ""
    suffix = " </𝟑"
    
    # Style the text with serif bold font only
    styled_text = prefix
    for char in text:
        if char.isalpha():
            styled_text += FONT_STYLES['serif_bold'](char)
        else:
            styled_text += char
            
    return styled_text + suffix

def heart_style(text):
    """Create fancy style with alternating character styles"""
    prefix = "❛.𝁘ໍ  ♡ "
    suffix = "༗🥀"
    
    # Style each letter of the text individually with alternating fonts
    styled_text = ""
    for i, char in enumerate(text):
        if char.isalpha():
            # Add alternating font style for each character
            if i % 3 == 0:
                styled_text += FONT_STYLES['serif_bold'](char) + ' '
            elif i % 3 == 1:
                styled_text += FONT_STYLES['sans_serif'](char) + ' '
            else:
                styled_text += FONT_STYLES['serif_italic'](char) + ' '
        else:
            styled_text += char + ' '
                
    return f"{prefix}{styled_text.strip()}{suffix}"

def stylish_bio_accent(text):
    """Create a stylish bio name with accent elements and floral patterns."""
    prefix = "◄⏤͟͟͞🫧⃝⃪🦋⃪꯭"
    suffix = "꯭ 𝅥ͦ ◡̈⃝ ا۬͢🌸᪳𝆺꯭𝅥⎯꯭꯭᪵̽⎯꯭"
    styled_text = ""
    for i, char in enumerate(text):
        if char.isalpha():
            # Add combining characters for extra stylistic effect
            styled_text += char + "꯭"
            # Add random superscript numbers to some characters
            if i % 3 == 0:
                styled_text += "ͥ"
            elif i % 3 == 1:
                styled_text += "ͣ"
            elif i % 3 == 2:
                styled_text += "ͫ"
        else:
            styled_text += char
    
    return f"{prefix}{styled_text}{suffix}"

def stylish_bio_clone(text):
    """Create a stylish bio name with the 'clone' theme."""
    prefix = "⎯᪵⎯꯭̽💀⃪꯭᪳"
    suffix = "⃪🔥͎᪳᪳𝆺꯭𝅥⎯꯭̽⎯꯭"
    styled_text = ""
    for i, char in enumerate(text):
        if char.isalpha():
            styled_text += char + "꯭"
            # Alternate with cursive style letters
            if i % 2 == 0 and ord('a') <= ord(char.lower()) <= ord('z'):
                styled_text += "𞂵"  # Stylistic modifier
            elif i % 3 == 0:
                styled_text += "͕֟፝"  # Combining characters for decoration
        else:
            styled_text += char
    
    return f"{prefix}{styled_text}{suffix}"

def stylish_bio_sanatan(text):
    """Create a stylish bio name with the 'sanatan' theme."""
    prefix = "⎯᪵⎯꯭̽🫧᪵᪳ ⃪꯭ "
    suffix = " ⃪🍃꯭͎᪳᪳𝆺꯭𝅥⎯꯭̽⎯꯭"
    styled_text = ""
    for char in text:
        if char.isalpha():
            # Create special Latin-like characters with combining marks
            styled_text += char.upper() + "Λ꯭"
        else:
            styled_text += char
    
    return f"{prefix}{styled_text}{suffix}"

def stylish_bio_anjali(text):
    """Create a stylish bio name with the 'anjali' theme."""
    prefix = "𝆺𝅥⃝🤍͓͢°⃪✦꯭"
    suffix = "✦°꯭🍃꯭᪳𝆺꯭𝅥⎯꯭̽⎯꯭"
    styled_text = ""
    
    for i, char in enumerate(text):
        if char.isalpha():
            # Mix regular and stylized characters
            if i % 3 == 0:
                styled_text += char.lower() + "꯭"
            elif i % 3 == 1:
                styled_text += "ℑ⃪꯭"
            else:
                styled_text += char.lower() + "ı"
        else:
            styled_text += char
    
    return f"{prefix}{styled_text}{suffix}"

def stylish_bio_misty(text):
    """Create a stylish bio name with the 'misty' theme."""
    prefix = "𝆺𝅥⃝🤍𝅃꯭᳚"
    suffix = "↽꯭̽𓆩𓂍𓆪꯭°‌⁪꯭˗˗𝅃꯭᳚🥀"
    styled_text = ""
    
    # Create spaced out letters with combining characters
    for char in text:
        if char.isalpha():
            styled_text += char.upper() + " ꯭"
        else:
            styled_text += char + " "
    
    return f"{prefix}{styled_text}{suffix}"

def stylish_bio_butterfly(text):
    """Create a stylish bio name with a butterfly theme."""
    prefix = "◄⏤͟͟͞🦋⃝⃪🍃꯭"
    suffix = "˶֟፝͟͝⏎͟𝐱̌͟𝗗᪵͢⃤"
    styled_text = ""
    
    for char in text:
        if char.isalpha():
            # Use mathematical sans-serif bold capital letters
            styled_text += char.upper() + "꯭"
        else:
            styled_text += char
    
    return f"{prefix}{styled_text}{suffix}"

def stylish_bio_premium(text):
    """Create a stylish bio name with the 'premium' theme."""
    prefix = "𝆺𝅥⃝🤍⃮×⃪͜‌ "
    suffix = " ⃪🐍᪳᪳‌᪳𝆺꯭𝅥⎯꯭ͯ⟶"
    styled_text = ""
    
    for i, char in enumerate(text):
        if char.isalpha():
            if i % 4 == 0:
                styled_text += "𝐏" if i == 0 else char.upper()
            elif i % 4 == 1:
                styled_text += char + "꯭‌"
            elif i % 4 == 2:
                styled_text += "𝝾⃪" if i == 2 else char
            elif i % 4 == 3:
                styled_text += "꯭‌" + char.lower()
        else:
            styled_text += char
    
    return f"{prefix}{styled_text}{suffix}"

def stylish_bio_joker(text):
    """Create a stylish bio name with the 'joker' theme."""
    prefix = "🝐꯭𐏓꯭꯭ ⃪🤍𝄄𝄀꯭𝄄꯭ ⃪͢"
    suffix = "  ̶꯭𝅥ͦ𝆬🍫 ̶꯭𝅥ͦ𝆬 ⃪𝄄𝄀꯭𝄄꯭⎯꯭ͯ⟶⋆"
    
    styled_text = ""
    for i, char in enumerate(text):
        if char.isalpha():
            if i % 5 == 0:
                styled_text += char.upper() + "❍꯭"
            elif i % 5 == 1:
                styled_text += "𝆭" + char
            elif i % 5 == 2:
                styled_text += char + "ا۬"
            elif i % 5 == 3:
                styled_text += "Ξ͢" + char
            else:
                styled_text += char + "  ̶"
        else:
            styled_text += char
    
    return f"{prefix}{styled_text}{suffix}"

def stylish_bio_prashant(text):
    """Create a stylish bio name with the 'prashant' theme."""
    prefix = "𝆺𝅥⃝🎧⃮×⃪͜‌ "
    suffix = " ◡̈⃝⟶📻"
    
    styled_text = ""
    for i, char in enumerate(text):
        if char.isalpha():
            # All caps with alternating styles
            if i % 3 == 0:
                styled_text += "𝐏" if i == 0 else "𝐏"
            elif i % 3 == 1:
                styled_text += "𝐑⃮∆" if i == 1 else "𝐑"
            else:
                styled_text += "𝐒⃯∆" if i == 2 else "𝐒"
        else:
            styled_text += char
    
    styled_text = text.upper().replace("P", "𝐏").replace("R", "𝐑").replace("A", "∆").replace("S", "𝐒").replace("H", "𝐇").replace("N", "𝐍").replace("T", "𝐓")
    
    return f"{prefix}{styled_text}{suffix}"

def stylish_bio_innocent(text):
    """Create a stylish bio name with the 'innocent girl' theme."""
    prefix = "◄⏤͟͞🦋꯭𝆺𝅥⃝꯭"
    suffix = " ◡̈⃝꯭🍃⃪⵿𝐆꯭𝗶𝗿̌𝗹꯭𐏓꯭ ᷞ ͦ ͮ ͕ͤ "
    
    styled_text = ""
    for i, char in enumerate(text):
        if char.isalpha():
            styled_text += char + "꯭"
            if i % 4 == 0:
                styled_text += "ͥ"
            elif i % 4 == 1:
                styled_text += "⵿̌"
            elif i % 4 == 2:
                styled_text += "ͫ"
            elif i % 4 == 3:
                styled_text += "፝֟"
        else:
            styled_text += char
    
    return f"{prefix}{styled_text}{suffix}"

def stylish_bio_isi_u(text):
    """Create a stylish bio name with the 'I S I U' theme."""
    styled_text = ""
    
    # Process each character with spaces and capital letters
    for char in text:
        if char.isalpha():
            styled_text += f"𝐒┣{char.upper()} "
        else:
            styled_text += char + " "
    
    return f"ㅤㅤ❛ .𝁘ໍ - {styled_text}𓂃• ‹𝟹"

def stylish_bio_special(text):
    """Create a stylish bio name with special characters and ornaments."""
    prefix = "𝆺𝅥⃝🦋𝅃꯭᳚"
    suffix = "↽꯭̽𓆩𓂍𓆪꯭°‌⁪꯭˗˗𝅃꯭᳚🦚ⷥ⥴🪈"
    
    styled_text = ""
    for i, char in enumerate(text):
        if char.isalpha():
            if i % 3 == 0:
                styled_text += "𝝨 " if i == 0 else char
            elif i % 3 == 1:
                styled_text += "𞂵" + char + "꯭̌ "
            else:
                styled_text += "꯭" + char + " "
        else:
            styled_text += char
    
    return f"{prefix}{styled_text}{suffix}"

def stylish_bio_miss(text):
    """Create a stylish bio name with the 'MISS' theme."""
    prefix = "◄⏤͟͞ꭙ𝄟⃝🦋̶̶꯭ꤴ"
    suffix = "͓⃖⏎͟𝐱̌͟𝗗᪵͢⃤"
    
    styled_text = ""
    for i, char in enumerate(text):
        if char.isalpha():
            if i % 4 == 0:
                styled_text += "𝐌꯭"
            elif i % 4 == 1:
                styled_text += "𝐈꯭"
            elif i % 4 == 2:
                styled_text += "𝐒̸͕"
            else:
                styled_text += "𝐒͢ ꤴ"
        else:
            styled_text += char
    
    # Override with specific text if it matches certain patterns
    if text.upper() == "MISS SUNAMI":
        styled_text = "𝐌꯭𝐈꯭𝐒̸͕𝐒͢ ꤴ𝐒꯭𝐔̸꯭𝐍፝֟𝚨̸꯭͕𝐌꯭𝐈"
    
    return f"{prefix}{styled_text}{suffix}"

def stylish_bio_prachi(text):
    """Create a stylish bio name with the 'PRACHI' theme."""
    prefix = "◄⏤͟͞ꭙ𝆺𝅥⃝🌙⃪꯭꯭🇵̶꯭ࠪ"
    suffix = "ᯓ꯭̽🦋𝆺𝅥⃝👑⇢"
    
    styled_text = ""
    for i, char in enumerate(text):
        if char.isalpha():
            styled_text += char.lower() + "꯭"
            
            # Add decorative elements
            if i % 3 == 0:
                styled_text += "ͥ"
            elif i % 3 == 1:
                styled_text += "ͣ"
            elif i % 3 == 2:
                styled_text += "ͫ"
                
        else:
            styled_text += char
    
    return f"{prefix}{styled_text}{suffix}"

def stylish_bio_jasmine(text):
    """Create a stylish bio name with the 'JASMINE' theme."""
    styled_text = ""
    for i, char in enumerate(text):
        if 'A' <= char.upper() <= 'Z':
            # Use mathematical sans-serif bold capital letters
            styled_text += chr(ord('𝗔') + ord(char.upper()) - ord('A'))
        else:
            styled_text += char
    
    return f"ᯓᡣ𐭩{styled_text} 𓆪⤹ꨄ •𓂃°"

def stylish_bio_sath(text):
    """Create a stylish bio name with the 'SATH' theme."""
    styled_text = ""
    for i, char in enumerate(text):
        if char.isalpha():
            if i % 5 == 0:
                styled_text += "ᴊ❍ "
            elif i % 5 == 1:
                styled_text += char.lower() + "aʈɦ "
            elif i % 5 == 2:
                styled_text += "𝆭" + char.lower() + "͢Ə "
            elif i % 5 == 3:
                styled_text += "Ꮚ" + char.lower() + "꯭ɦ"
            else:
                styled_text += char.lower() + "ᮃ"
        else:
            styled_text += char
    
    return f"⃟🌿{styled_text} 📌 ⃟🤲ɑᴘ𝆭𝝶ɑ Ɓαʞ͞ı͢ı͞ saᮃ🐬 ⃟🕊️sɑ꯭𝆭ᴘ𝝶ɑ 𝆺𝅥𝆺𝅥♛"

def stylish_bio_heart(text):
    """Create a stylish bio name with the 'HEART' theme."""
    styled_text = ""
    for i, char in enumerate(text):
        if char.isalpha():
            if i % 3 == 0:
                styled_text += char.lower() + "ᵉ꯭"
            elif i % 3 == 1:
                styled_text += "ᵃʳ"
            elif i % 3 == 2:
                styled_text += "✞︎⃮" + char.lower()
        else:
            styled_text += char
    
    return f"◄⏤͟͟͞🖤⃝⃪🇭{styled_text}ᭃ꯭꯭⤹𓆪ꪾ⇝"

def stylish_bio_dark(text):
    """Create a stylish bio name with the 'DARK' theme."""
    styled_text = ""
    
    for i, char in enumerate(text):
        if char.isalpha():
            if i % 4 == 0:
                styled_text += "🅳꯭𝆬"
            elif i % 4 == 1:
                styled_text += "𝐀"
            elif i % 4 == 2:
                styled_text += "𝐑̸꯭"
            elif i % 4 == 3:
                styled_text += "𝐊𝆭"
            styled_text += char.upper()
        else:
            styled_text += char
    
    return f"✶❥͜͡𝄟⃟{styled_text} 𝆺𝅥⃝𝄟⸙⇝"

def stylish_bio_viskl(text):
    """Create a stylish bio name with elegant Greek-like letters."""
    greek_map = {
        'a': '𝛂', 'b': '𝛃', 'c': '𝛄', 'd': '𝛅', 'e': '𝛆', 'f': '𝛇', 'g': '𝛈', 
        'h': '𝛉', 'i': '𝛊', 'j': '𝛋', 'k': '𝛌', 'l': '𝛍', 'm': '𝛎', 'n': '𝛏', 
        'o': '𝛐', 'p': '𝛑', 'q': '𝛒', 'r': '𝛓', 's': '𝛔', 't': '𝛕', 'u': '𝛖', 
        'v': '𝛗', 'w': '𝛘', 'x': '𝛙', 'y': '𝛚', 'z': '𝛛'
    }
    
    styled_text = ""
    for char in text:
        if char.lower() in greek_map:
            styled_text += greek_map[char.lower()] + " "
        else:
            styled_text += char + " "
    
    return f"𓂃❛ ⟶̽ {styled_text}❜ 🌙⤹🤍"

def stylish_bio_black_heart(text):
    """Create a stylish bio name with the 'BLACK HEART' theme."""
    styled_text = ""
    
    for i, char in enumerate(text):
        if char.isalpha():
            if i % 3 == 0:
                styled_text += "𝚩" + char.upper()
            elif i % 3 == 1:
                styled_text += "𝐋" + char.upper()
            elif i % 3 == 2:
                styled_text += "𝚲" + char.upper()
        else:
            styled_text += char
    
    return f"◄⏤͟͟͞🍸⃝⃪🖤{styled_text}᭓┣𝐥𝚵𝚲𝐑𝚻𔘓⃭𓆩🖤𓆪"

def stylish_bio_infinity(text):
    """Create a stylish bio name with infinity style."""
    prefix = "⋆⎯꯭̽𝅃꯭᳚𝆺𝅥༎ࠫ𝆺꯭𝅥"
    suffix = "༎ࠫ٭⃪꯭💙𝆺꯭𝅥𔘓𖥫꯭ •◡̈⃝🚩"
    
    styled_text = ""
    for i, char in enumerate(text):
        if char.isalpha():
            styled_text += "✦" + char.lower() + "͟"
        else:
            styled_text += char
    
    return f"{prefix}{styled_text}{suffix}"

def stylish_bio_abstract(text):
    """Create a stylish bio name with abstract characters."""
    prefix = "⋆⎯꯭̽𝅃꯭᳚𝆺𝅥༎ࠫ𝆺꯭𝅥"
    suffix = "༎ࠫ٭⃪꯭💙𝆺꯭𝅥𔘓𖥫꯭ •◡̈⃝🚩"
    
    # Map for abstract characters
    abstract_map = {
        'a': 'ᴀ', 'b': 'ᴂ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 
        'f': 'ꜰ', 'g': 'ɢ', 'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ', 
        'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ', 
        'p': 'ᴘ', 'q': 'ꞯ', 'r': 'ʀ', 's': 'ꜱ', 't': 'ᴛ',
        'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 
        'z': 'ᴢ'
    }
    
    styled_text = ""
    for i, char in enumerate(text):
        if char.lower() in abstract_map:
            styled_text += abstract_map[char.lower()] + "͟"
        else:
            styled_text += char
    
    return f"{prefix}{styled_text}{suffix}"

def stylish_bio_arrow_style(text):
    """Create a stylish bio name with arrow style."""
    styled_text = ""
    for char in text.lower():
        if char.isalpha():
            styled_text += char
        else:
            styled_text += char
    
    return f"✧⇜{styled_text}⇜✧"

def stylish_bio_crystal(text):
    """Create a stylish bio name with crystal style."""
    prefix = "◆━━━━━━━━◆"
    suffix = "◆━━━━━━━━◆"
    
    styled_text = ""
    for char in text:
        if char.isalpha():
            styled_text += "♢" + char.upper() + "♢"
        else:
            styled_text += char
    
    return f"{prefix}\n   {styled_text}\n{suffix}"

def stylish_bio_waves(text):
    """Create a stylish bio name with wave style."""
    prefix = "≽^•⩊•^≼"
    suffix = "≽^•⩊•^≼"
    
    # Wave symbols
    waves = ["⌇", "⌇", "≋", "≈", "≋", "⌇"]
    
    styled_text = ""
    for i, char in enumerate(text):
        if char.isalpha():
            wave = waves[i % len(waves)]
            styled_text += wave + char.upper() + wave
        else:
            styled_text += char
    
    return f"{prefix} {styled_text} {suffix}"

def stylish_bio_neon(text):
    """Create a stylish bio name with neon sign style."""
    prefix = "▒█▀▀█ "
    suffix = " █▄▄█▀"
    
    styled_text = text.upper()
    
    return f"{prefix}{styled_text}{suffix}"

def stylish_bio_royal(text):
    """Create a stylish bio name with royal style."""
    prefix = "⎝⎝✧GͥOͣDͫ✧⎠⎠"
    suffix = "⎝⎝✧GͥOͣDͫ✧⎠⎠"
    
    styled_text = ""
    for i, char in enumerate(text):
        if char.isalpha():
            if i % 3 == 0:
                styled_text += char.upper() + "ͥ"
            elif i % 3 == 1:
                styled_text += char.upper() + "ͣ"
            else:
                styled_text += char.upper() + "ͫ"
        else:
            styled_text += char
    
    return f"{prefix} {styled_text} {suffix}"

def stylish_bio_gaming(text):
    """Create a stylish bio name with gaming style."""
    prefix = "ᗩᒪᖴᗩ࿐☦︎"
    suffix = "☦︎࿐ᘜᗩᘻᘿᖇ"
    
    styled_text = ""
    for char in text:
        if char.isalpha():
            # Use small caps for gaming style
            if char.lower() == 'a':
                styled_text += "ᗩ"
            elif char.lower() == 'b':
                styled_text += "ᗷ"
            elif char.lower() == 'c':
                styled_text += "ᑕ"
            elif char.lower() == 'd':
                styled_text += "ᗪ"
            elif char.lower() == 'e':
                styled_text += "ᘿ"
            elif char.lower() == 'f':
                styled_text += "ᖴ"
            elif char.lower() == 'g':
                styled_text += "ᘜ"
            elif char.lower() == 'h':
                styled_text += "ᕼ"
            elif char.lower() == 'i':
                styled_text += "ᓰ"
            elif char.lower() == 'j':
                styled_text += "ᒚ"
            elif char.lower() == 'k':
                styled_text += "ᖽᐸ"
            elif char.lower() == 'l':
                styled_text += "ᒪ"
            elif char.lower() == 'm':
                styled_text += "ᘻ"
            elif char.lower() == 'n':
                styled_text += "ᘉ"
            elif char.lower() == 'o':
                styled_text += "ᓍ"
            elif char.lower() == 'p':
                styled_text += "ᖘ"
            elif char.lower() == 'q':
                styled_text += "ᕴ"
            elif char.lower() == 'r':
                styled_text += "ᖇ"
            elif char.lower() == 's':
                styled_text += "S"
            elif char.lower() == 't':
                styled_text += "ᖶ"
            elif char.lower() == 'u':
                styled_text += "ᑘ"
            elif char.lower() == 'v':
                styled_text += "ᐺ"
            elif char.lower() == 'w':
                styled_text += "ᘺ"
            elif char.lower() == 'x':
                styled_text += "᙭"
            elif char.lower() == 'y':
                styled_text += "ᖻ"
            elif char.lower() == 'z':
                styled_text += "ᗱ"
            else:
                styled_text += char.upper()
        else:
            styled_text += char
    
    return f"{prefix} {styled_text} {suffix}"

def stylish_bio_angel(text):
    """Create a stylish bio name with angel wings."""
    prefix = "꧁༺"
    suffix = "༻꧂"
    
    styled_text = ""
    for char in text:
        if char.isalpha():
            styled_text += char.upper()
        else:
            styled_text += char
    
    return f"{prefix}{styled_text}{suffix}"

def stylish_bio_fire_ice(text):
    """Create a stylish bio name with fire and ice theme."""
    prefix = "❄️🔥"
    suffix = "🔥❄️"
    
    styled_text = ""
    for i, char in enumerate(text):
        if char.isalpha():
            if i % 2 == 0:
                styled_text += "❄" + char.upper() + "❄"
            else:
                styled_text += "🔥" + char.upper() + "🔥"
        else:
            styled_text += char
    
    return f"{prefix} {styled_text} {suffix}"

def stylish_bio_cute(text):
    """Create a stylish bio name with cute theme."""
    prefix = "˚ ༘♡ ⋆｡˚"
    suffix = "˚ ༘♡ ⋆｡˚"
    
    styled_text = ""
    for char in text:
        if char.isalpha():
            styled_text += "♡" + char.lower() + "♡"
        else:
            styled_text += char
    
    return f"{prefix} {styled_text} {suffix}"

def stylish_bio_diamond_crown(text):
    """Create a stylish bio name with diamond and crown theme."""
    prefix = "👑💎"
    suffix = "💎👑"
    
    styled_text = ""
    for char in text:
        if char.isalpha():
            styled_text += "💠" + char.upper() + "💠"
        else:
            styled_text += char
    
    return f"{prefix} {styled_text} {suffix}"

def stylish_bio_elegant(text):
    """Create an elegant stylish bio name."""
    prefix = "•°¯`•• "
    suffix = " ••`¯°•"
    
    styled_text = ""
    for char in text:
        if char.isalpha():
            styled_text += char.upper()
        else:
            styled_text += char
    
    return f"{prefix}{styled_text}{suffix}"

def stylish_bio_fancy_border(text):
    """Create a stylish bio name with fancy border."""
    top_border = "╔══╗"
    bottom_border = "╚══╝"
    
    styled_text = ""
    for char in text:
        if char.isalpha():
            styled_text += char.upper()
        else:
            styled_text += char
    
    return f"{top_border}\n{styled_text}\n{bottom_border}"

def stylish_bio_shadow(text):
    """Create a stylish bio name with shadow effect."""
    styled_text = ""
    for char in text:
        if char.isalpha():
            styled_text += char.upper() + "̷"
        else:
            styled_text += char
    
    return f"⸻⃤꙰ {styled_text} ꙰⃤⸻"

def stylish_bio_galaxy(text):
    """Create a stylish bio name with galaxy theme."""
    prefix = "✧༺࿐"
    suffix = "࿐༻✧"
    
    styled_text = ""
    for i, char in enumerate(text):
        if char.isalpha():
            if i % 3 == 0:
                styled_text += "✦" + char.upper() + "✧"
            elif i % 3 == 1:
                styled_text += "⋆" + char.upper() + "⋆"
            else:
                styled_text += "✫" + char.upper() + "✫"
        else:
            styled_text += char
    
    return f"{prefix} {styled_text} {suffix}"

def stylish_bio_glitch(text):
    """Create a stylish bio name with glitch effect."""
    prefix = "g̷̞̓l̵̘̿ȉ̶̙t̶̝̚c̴̲̕h̴͕̍"
    suffix = "ḛ̸̓f̵̭̂f̵̞̓e̴̳̒c̷͖̔t̸͖͐"
    
    styled_text = ""
    for char in text:
        if char.isalpha():
            styled_text += char + "̶̢̟̞͐̓͒̀̇͗̚"
        else:
            styled_text += char
    
    return f"{prefix} {styled_text} {suffix}"

def stylish_bio_magic(text):
    """Create a stylish bio name with magic theme."""
    prefix = "✮✮✮"
    suffix = "✮✮✮"
    
    magic_symbols = ["⋇", "⋆", "✧", "⋄", "∗", "☽", "✴"]
    
    styled_text = ""
    for i, char in enumerate(text):
        if char.isalpha():
            symbol1 = magic_symbols[i % len(magic_symbols)]
            symbol2 = magic_symbols[(i + 2) % len(magic_symbols)]
            styled_text += f"{symbol1}{char.upper()}{symbol2}"
        else:
            styled_text += char
    
    return f"{prefix} {styled_text} {suffix}"

def stylish_bio_retro(text):
    """Create a stylish bio name with retro vaporwave aesthetic."""
    prefix = "【"
    suffix = "】"
    
    styled_text = ""
    for char in text:
        if char.isalpha():
            # Use fullwidth characters for vaporwave aesthetic
            if 'a' <= char.lower() <= 'z':
                # Convert to fullwidth letters
                styled_text += chr(ord(char.upper()) + 0xFEE0)
            else:
                styled_text += char
        else:
            styled_text += char
    
    return f"{prefix}{styled_text}{suffix}"

def stylish_bio_tech(text):
    """Create a stylish bio name with tech/hacker theme."""
    prefix = "<⁄"
    suffix = "⧹>"
    
    tech_map = {
        'a': '4', 'b': '8', 'e': '3', 'i': '1', 'l': '1',
        'o': '0', 's': '5', 't': '7', 'z': '2'
    }
    
    styled_text = ""
    for char in text:
        if char.lower() in tech_map:
            styled_text += tech_map[char.lower()]
        else:
            styled_text += char
    
    return f"{prefix} {styled_text} {suffix}"

def stylish_bio_cursed(text):
    """Create a stylish bio name with cursed/zalgo text effect."""
    combining_above = [
        '\u0300', '\u0301', '\u0302', '\u0303', '\u0304', '\u0305',
        '\u0306', '\u0307', '\u0308', '\u0309', '\u030A', '\u030B',
        '\u030C', '\u030D', '\u030E', '\u030F'
    ]
    
    combining_middle = [
        '\u0315', '\u031B', '\u0340', '\u0341', '\u0358', '\u0321',
        '\u0322', '\u0327', '\u0328', '\u0334', '\u0335', '\u0336'
    ]
    
    combining_below = [
        '\u0316', '\u0317', '\u0318', '\u0319', '\u031C', '\u031D',
        '\u031E', '\u031F', '\u0320', '\u0324', '\u0325', '\u0326',
        '\u0329', '\u032A', '\u032B', '\u032C', '\u032D', '\u032E',
        '\u032F', '\u0330', '\u0331', '\u0332', '\u0333', '\u0339'
    ]
    
    styled_text = ""
    for char in text:
        if char.isalpha():
            # Add the character
            styled_text += char
            
            # Add 1-3 random combining characters above
            for _ in range(random.randint(1, 3)):
                styled_text += random.choice(combining_above)
                
            # Add 0-2 random combining characters in the middle
            for _ in range(random.randint(0, 2)):
                styled_text += random.choice(combining_middle)
                
            # Add 1-3 random combining characters below
            for _ in range(random.randint(1, 3)):
                styled_text += random.choice(combining_below)
        else:
            styled_text += char
    
    return f"{styled_text}"

def stylish_bio_medieval(text):
    """Create a stylish bio name with medieval/gothic theme."""
    prefix = "†"
    suffix = "†"
    
    gothic_map = {
        'a': '𝔞', 'b': '𝔟', 'c': '𝔠', 'd': '𝔡', 'e': '𝔢', 'f': '𝔣',
        'g': '𝔤', 'h': '𝔥', 'i': '𝔦', 'j': '𝔧', 'k': '𝔨', 'l': '𝔩',
        'm': '𝔪', 'n': '𝔫', 'o': '𝔬', 'p': '𝔭', 'q': '𝔮', 'r': '𝔯',
        's': '𝔰', 't': '𝔱', 'u': '𝔲', 'v': '𝔳', 'w': '𝔴', 'x': '𝔵',
        'y': '𝔶', 'z': '𝔷',
        'A': '𝔄', 'B': '𝔅', 'C': 'ℭ', 'D': '𝔇', 'E': '𝔈', 'F': '𝔉',
        'G': '𝔊', 'H': 'ℌ', 'I': 'ℑ', 'J': '𝔍', 'K': '𝔎', 'L': '𝔏',
        'M': '𝔐', 'N': '𝔑', 'O': '𝔒', 'P': '𝔓', 'Q': '𝔔', 'R': 'ℜ',
        'S': '𝔖', 'T': '𝔗', 'U': '𝔘', 'V': '𝔙', 'W': '𝔚', 'X': '𝔛',
        'Y': '𝔜', 'Z': 'ℨ'
    }
    
    styled_text = ""
    for char in text:
        if char in gothic_map:
            styled_text += gothic_map[char]
        else:
            styled_text += char
    
    return f"{prefix} {styled_text} {suffix}"

def stylish_bio_boxed(text):
    """Create a stylish bio name with boxed letters."""
    boxed_map = {
        'a': '🄰', 'b': '🄱', 'c': '🄲', 'd': '🄳', 'e': '🄴', 
        'f': '🄵', 'g': '🄶', 'h': '🄷', 'i': '🄸', 'j': '🄹', 
        'k': '🄺', 'l': '🄻', 'm': '🄼', 'n': '🄽', 'o': '🄾', 
        'p': '🄿', 'q': '🅀', 'r': '🅁', 's': '🅂', 't': '🅃', 
        'u': '🅄', 'v': '🅅', 'w': '🅆', 'x': '🅇', 'y': '🅈', 
        'z': '🅉'
    }
    
    styled_text = ""
    for char in text:
        if char.lower() in boxed_map:
            styled_text += boxed_map[char.lower()]
        else:
            styled_text += char
    
    return styled_text

def stylish_bio_cool(text):
    """Create a stylish bio name with cool dots under letters."""
    styled_text = ""
    for char in text:
        if char.isalpha():
            styled_text += char.upper() + "̤"
        else:
            styled_text += char
    
    return f"꧁༒☬ {styled_text} ☬༒꧂"

def stylish_bio_circled(text):
    """Create a stylish bio name with circled letters."""
    circled_map = {
        'a': 'ⓐ', 'b': 'ⓑ', 'c': 'ⓒ', 'd': 'ⓓ', 'e': 'ⓔ', 
        'f': 'ⓕ', 'g': 'ⓖ', 'h': 'ⓗ', 'i': 'ⓘ', 'j': 'ⓙ', 
        'k': 'ⓚ', 'l': 'ⓛ', 'm': 'ⓜ', 'n': 'ⓝ', 'o': 'ⓞ', 
        'p': 'ⓟ', 'q': 'ⓠ', 'r': 'ⓡ', 's': 'ⓢ', 't': 'ⓣ', 
        'u': 'ⓤ', 'v': 'ⓥ', 'w': 'ⓦ', 'x': 'ⓧ', 'y': 'ⓨ', 
        'z': 'ⓩ',
        'A': 'Ⓐ', 'B': 'Ⓑ', 'C': 'Ⓒ', 'D': 'Ⓓ', 'E': 'Ⓔ', 
        'F': 'Ⓕ', 'G': 'Ⓖ', 'H': 'Ⓗ', 'I': 'Ⓘ', 'J': 'Ⓙ', 
        'K': 'Ⓚ', 'L': 'Ⓛ', 'M': 'Ⓜ', 'N': 'Ⓝ', 'O': 'Ⓞ', 
        'P': 'Ⓟ', 'Q': 'Ⓠ', 'R': 'Ⓡ', 'S': 'Ⓢ', 'T': 'Ⓣ', 
        'U': 'Ⓤ', 'V': 'Ⓥ', 'W': 'Ⓦ', 'X': 'Ⓧ', 'Y': 'Ⓨ', 
        'Z': 'Ⓩ'
    }
    
    styled_text = ""
    for char in text:
        if char in circled_map:
            styled_text += circled_map[char]
        else:
            styled_text += char
    
    return f"『 {styled_text} 』"

def stylish_bio_sparkles(text):
    """Create a stylish bio name with sparkles."""
    styled_text = ""
    for char in text:
        if char.isalpha():
            styled_text += "✨" + char.upper() + "✨"
        else:
            styled_text += char
    
    return styled_text

def stylish_bio_fireworks(text):
    """Create a stylish bio name with fireworks theme."""
    prefix = "🎆"
    suffix = "🎆"
    
    styled_text = ""
    for i, char in enumerate(text):
        if char.isalpha():
            if i % 2 == 0:
                styled_text += "💫" + char.upper() + "💫"
            else:
                styled_text += "✨" + char.upper() + "✨"
        else:
            styled_text += char
    
    return f"{prefix} {styled_text} {suffix}"

def stylish_bio_double_struck(text):
    """Create a stylish bio name with double-struck letters."""
    double_struck_map = {
        'a': '𝕒', 'b': '𝕓', 'c': '𝕔', 'd': '𝕕', 'e': '𝕖', 
        'f': '𝕗', 'g': '𝕘', 'h': '𝕙', 'i': '𝕚', 'j': '𝕛', 
        'k': '𝕜', 'l': '𝕝', 'm': '𝕞', 'n': '𝕟', 'o': '𝕠', 
        'p': '𝕡', 'q': '𝕢', 'r': '𝕣', 's': '𝕤', 't': '𝕥', 
        'u': '𝕦', 'v': '𝕧', 'w': '𝕨', 'x': '𝕩', 'y': '𝕪', 
        'z': '𝕫',
        'A': '𝔸', 'B': '𝔹', 'C': 'ℂ', 'D': '𝔻', 'E': '𝔼', 
        'F': '𝔽', 'G': '𝔾', 'H': 'ℍ', 'I': '𝕀', 'J': '𝕁', 
        'K': '𝕂', 'L': '𝕃', 'M': '𝕄', 'N': 'ℕ', 'O': '𝕆', 
        'P': 'ℙ', 'Q': 'ℚ', 'R': 'ℝ', 'S': '𝕊', 'T': '𝕋', 
        'U': '𝕌', 'V': '𝕍', 'W': '𝕎', 'X': '𝕏', 'Y': '𝕐', 
        'Z': 'ℤ'
    }
    
    styled_text = ""
    for char in text:
        if char in double_struck_map:
            styled_text += double_struck_map[char]
        else:
            styled_text += char
    
    return f"⟦ {styled_text} ⟧"

def stylish_bio_cyrillic(text):
    """Create a stylish bio name with faux Cyrillic letters."""
    cyrillic_map = {
        'a': 'а', 'b': 'б', 'c': 'с', 'd': 'д', 'e': 'е', 
        'f': 'ф', 'g': 'г', 'h': 'н', 'i': 'и', 'j': 'й', 
        'k': 'к', 'l': 'л', 'm': 'м', 'n': 'н', 'o': 'о', 
        'p': 'п', 'q': 'я', 'r': 'г', 's': 'с', 't': 'т', 
        'u': 'у', 'v': 'в', 'w': 'ш', 'x': 'х', 'y': 'у', 
        'z': 'з'
    }
    
    styled_text = ""
    for char in text:
        if char.lower() in cyrillic_map:
            if char.isupper():
                styled_text += cyrillic_map[char.lower()].upper()
            else:
                styled_text += cyrillic_map[char.lower()]
        else:
            styled_text += char
    
    return f"⟬ {styled_text} ⟭"

def stylish_bio_script_bold(text):
    """Create a stylish bio name with bold script letters."""
    script_bold_map = {
        'a': '𝓪', 'b': '𝓫', 'c': '𝓬', 'd': '𝓭', 'e': '𝓮', 
        'f': '𝓯', 'g': '𝓰', 'h': '𝓱', 'i': '𝓲', 'j': '𝓳', 
        'k': '𝓴', 'l': '𝓵', 'm': '𝓶', 'n': '𝓷', 'o': '𝓸', 
        'p': '𝓹', 'q': '𝓺', 'r': '𝓻', 's': '𝓼', 't': '𝓽', 
        'u': '𝓾', 'v': '𝓿', 'w': '𝔀', 'x': '𝔁', 'y': '𝔂', 
        'z': '𝔃',
        'A': '𝓐', 'B': '𝓑', 'C': '𝓒', 'D': '𝓓', 'E': '𝓔', 
        'F': '𝓕', 'G': '𝓖', 'H': '𝓗', 'I': '𝓘', 'J': '𝓙', 
        'K': '𝓚', 'L': '𝓛', 'M': '𝓜', 'N': '𝓝', 'O': '𝓞', 
        'P': '𝓟', 'Q': '𝓠', 'R': '𝓡', 'S': '𝓢', 'T': '𝓣', 
        'U': '𝓤', 'V': '𝓥', 'W': '𝓦', 'X': '𝓧', 'Y': '𝓨', 
        'Z': '𝓩'
    }
    
    styled_text = ""
    for char in text:
        if char in script_bold_map:
            styled_text += script_bold_map[char]
        else:
            styled_text += char
    
    return f"✿ {styled_text} ✿"

def generate_fancy_name(name: str) -> str:
    """Generate a fancy font name using special characters."""
    # Add new stylish bio functions to the available styles
    bio_styles = [
        stylish_bio_accent,
        stylish_bio_clone,
        stylish_bio_sanatan,
        stylish_bio_anjali,
        stylish_bio_misty,
        stylish_bio_butterfly,
        stylish_bio_premium,
        stylish_bio_joker,
        stylish_bio_prashant,
        stylish_bio_innocent,
        stylish_bio_isi_u,
        stylish_bio_special,
        stylish_bio_miss,
        stylish_bio_prachi,
        stylish_bio_jasmine,
        stylish_bio_sath,
        stylish_bio_heart,
        stylish_bio_dark,
        stylish_bio_viskl,
        stylish_bio_black_heart,
        stylish_bio_infinity,
        stylish_bio_abstract,
        stylish_bio_arrow_style,
        stylish_bio_crystal,
        stylish_bio_waves,
        stylish_bio_neon,
        stylish_bio_royal,
        stylish_bio_gaming,
        stylish_bio_angel,
        stylish_bio_fire_ice,
        stylish_bio_cute,
        stylish_bio_diamond_crown,
        stylish_bio_elegant,
        stylish_bio_fancy_border,
        stylish_bio_shadow,
        stylish_bio_galaxy,
        stylish_bio_glitch,
        stylish_bio_magic,
        stylish_bio_retro,
        stylish_bio_tech,
        stylish_bio_cursed,
        stylish_bio_medieval,
        stylish_bio_boxed,
        stylish_bio_cool,
        stylish_bio_circled,
        stylish_bio_sparkles,
        stylish_bio_fireworks,
        stylish_bio_double_struck,
        stylish_bio_cyrillic,
        stylish_bio_script_bold,
        fancy_stylish_bio1,
        fancy_stylish_bio2,
        fancy_stylish_bio3,
        fancy_stylish_bio4,
        fancy_stylish_bio5,
        fancy_stylish_bio6,
        fancy_stylish_bio7,
        custom_frame
    ]
    
    # Choose a random style function from the bio styles or use a font style
    if random.random() < 0.7:  # 70% chance of using a bio style
        style_func = random.choice(bio_styles)
        return style_func(name)
    else:
        # Choose a random style from font styles
        style = random.choice(list(FONT_STYLES.values()))
        
        # Create stylish prefix and suffix
        prefix_count = random.randint(2, 4)
        suffix_count = random.randint(2, 4)
        
        prefix = ''.join(random.choice(SPECIAL_CHARS) for _ in range(prefix_count))
        suffix = ''.join(random.choice(SPECIAL_CHARS) for _ in range(suffix_count))
        
        # Add a connector
        connector = random.choice(CONNECTORS)
        
        # Convert name to stylish font
        stylish_name = ''
        for char in name:
            if char.isalpha():
                stylish_name += style(char)
            else:
                stylish_name += char
        
        # Apply random decorative transformation (25% chance)
        if random.random() < 0.25:
            decorations = [underline_text, strikethrough_text, bubble_wrap, star_wrap, dot_wrap, random_combine_chars]
            stylish_name = random.choice(decorations)(stylish_name)
        
        # Create several style options
        styles = [
            f"{prefix} {stylish_name} {suffix}",
            f"{prefix}{connector}{stylish_name} {suffix}",
            f"꧁{stylish_name}꧂",
            f"༺{stylish_name}༻",
            f"{prefix} {stylish_name} {connector} {suffix}",
            f"{stylish_name} 🔥❰⎯꯭ ꭗ‌",
            f"★彡[{stylish_name}]彡★",
            f"░▒▓█ {stylish_name} █▓▒░",
            f"✧{connector}{stylish_name}{connector}✧",
            f"ıllıllı {stylish_name} ıllıllı",
            f"↫ {stylish_name} ↬",
            custom_frame(stylish_name),
            prinxe_style(stylish_name),
            elaborate_style(stylish_name),
            f"⋆⎯꯭̽𝅃꯭᳚𝆺𝅥༎ࠫ𝆺꯭𝅥𔘓𖥫꯭ •◡̈⃝🚩",
            no_option_style(stylish_name),
            nobody_style(stylish_name),
            heart_style(stylish_name)
        ]
        
        return random.choice(styles)

def generate_example_styles(name: str) -> list:
    """Generate multiple fancy style examples for a name."""
    examples = []
    
    # Generate styles with different font types - now using 12 font styles
    for style_name, style_func in list(FONT_STYLES.items())[:12]:  # Using 12 font styles
        try:
            stylish_name = ''.join(style_func(char) if char.isalpha() else char for char in name)
            prefix = ''.join(random.choice(SPECIAL_CHARS) for _ in range(random.randint(1, 3)))
            suffix = ''.join(random.choice(SPECIAL_CHARS) for _ in range(random.randint(1, 3)))
            connector = random.choice(CONNECTORS)
            
            # Choose a random presentation style
            presentation = random.choice([
                f"{prefix} {stylish_name} {suffix}",
                f"{prefix}{connector}{stylish_name} {suffix}",
                f"꧁{stylish_name}꧂",
                f"༺{stylish_name}༻",
                f"{stylish_name} 🔥❰⎯꯭ ꭗ‌",
                f"★彡[{stylish_name}]彡★"
            ])
            
            examples.append(presentation)
        except Exception as e:
            logging.error(f"Error with style {style_name} in generate_example_styles: {e}")
            # Add a fallback version for this style
            examples.append(f"[{style_name}] {name}")
    
    # Add specific example styles with combining characters
    try:
        style = FONT_STYLES['bold']
        stylish_name = ''.join(style(char) if char.isalpha() else char for char in name)
        examples.append(f"𐏓  𝅥‌꯭𝆬ᷟ{stylish_name}‌🔥❰⎯꯭ ꭗ‌")
    except Exception:
        examples.append(f"★ {name} ★")
    
    # Add the requested prinxe style
    try:
        examples.append(prinxe_style(name))
    except Exception:
        examples.append(f"✨ {name} ✨")
    
    # Add a style with random combining characters
    try:
        examples.append(f"⋆⎯꯭̽𝅃꯭᳚𝆺𝅥༎ࠫ𝆺꯭𝅥{random_combine_chars(name)}༎ࠫ٭⃪꯭💙𝆺꯭𝅥𔘓𖥫꯭ •◡̈⃝🚩")
    except Exception:
        examples.append(f"⋆⎯ {name} ⎯⋆")
    
    # Add the requested no option style
    try:
        examples.append(no_option_style(name))
    except Exception:
        examples.append(f"⎯꯭̽🔥 {name} 🍃")
    
    # Add the requested nobody style
    try:
        examples.append(nobody_style(name))
    except Exception:
        examples.append(f"𝚴❍𝚩 {name}")
    
    # Add the requested heart style
    try:
        examples.append(heart_style(name))
    except Exception:
        examples.append(f"♡ {name} ♡")
    
    # Add an elaborate style
    try:
        examples.append(elaborate_style(name))
    except Exception:
        examples.append(f"✧ {name} ✧")
    
    # Add another variant of the prinxe style
    try:
        example_name = name
        if len(name) >= 1 and name[0].isalpha():
            # Capitalize the first letter
            example_name = name[0].upper() + name[1:].lower()
        
        first_char = example_name[0] + "⃨⃖"
        rest_chars = ''.join(c + (random.choice(["⃯⃗", "͟"]) if c.isalpha() else "") for c in example_name[1:])
        examples.append(f"⋆⎯꯭̽𝅃꯭᳚𝆺𝅥༎ࠫ𝆺꯭𝅥{first_char}{rest_chars}༎ࠫ٭⃪꯭💙𝆺꯭𝅥𔘓𖥫꯭ •◡̈⃝🚩")
    except Exception:
        examples.append(f"⋆⎯꯭̽ {name} •◡̈⃝")
    
    return examples

def fancy_stylish_bio1(text):
    """Create a fancy stylish bio with decorative elements"""
    prefix = "◄⏤͟͟͞🫧⃝⃪🦋⃪꯭"
    suffix = "𝅥ͦ ◡̈⃝ ا۬͢🌸᪳𝆺꯭𝅥⎯꯭꯭᪵̽⎯꯭"
    
    # Style the text with serif bold font + combining chars
    styled_text = ""
    for char in text:
        if char.isalpha():
            styled_char = FONT_STYLES['serif_bold'](char)
            styled_text += styled_char + "꯭"
        else:
            styled_text += char
            
    return f"{prefix}{styled_text}{suffix}"

def fancy_stylish_bio2(text):
    """Create a fancy stylish bio with dark theme and skull emoji"""
    prefix = "⎯᪵⎯꯭̽💀⃪꯭᪳"
    suffix = "⃪🔥͎᪳᪳𝆺꯭𝅥⎯꯭̽⎯꯭"
    
    # Style the text with serif bold font + decorations
    styled_text = ""
    for i, char in enumerate(text):
        if char.isalpha():
            styled_char = FONT_STYLES['serif_bold'](char)
            if i % 2 == 0:
                styled_text += styled_char + "꯭"
            else:
                styled_text += styled_char + "͕֟፝"
        else:
            styled_text += char
            
    return f"{prefix}{styled_text}{suffix}"

def fancy_stylish_bio3(text):
    """Create a stylish bio with the 'Λ꯭' style for specific letters"""
    prefix = "⎯᪵⎯꯭̽🫧᪵᪳ ⃪꯭ "
    suffix = " ⃪🍃꯭͎᪳᪳𝆺꯭𝅥⎯꯭̽⎯꯭"
    
    # Style with mixed Latin and Greek-like characters
    styled_text = ""
    for char in text:
        if char.lower() == 'a':
            styled_text += "Λ꯭"
        elif char.lower() == 'e':
            styled_text += "Σ꯭"
        elif char.lower() == 'n':
            styled_text += "Ň꯭"
        elif char.lower() == 't':
            styled_text += "Т꯭"
        elif char.isalpha():
            styled_text += char.upper() + "꯭"
        else:
            styled_text += char
            
    return f"{prefix}{styled_text}{suffix}"

def fancy_stylish_bio4(text):
    """Create a stylish bio with the 'α꯭' style for specific letters"""
    prefix = "𝆺𝅥⃝🤍͓͢°⃪✦꯭"
    suffix = "✦°꯭🍃꯭᪳𝆺꯭𝅥⎯꯭̽⎯꯭"
    
    # Style with lowercase Greek-like letters
    styled_text = ""
    for char in text:
        if char.lower() == 'a':
            styled_text += "α꯭"
        elif char.lower() == 'n':
            styled_text += "и꯭"
        elif char.lower() == 'i':
            styled_text += "ℑ⃪꯭"
        elif char.lower() == 'l':
            styled_text += "l꯭"
        elif char.isalpha():
            styled_text += char.lower() + "꯭"
        else:
            styled_text += char
            
    return f"{prefix}{styled_text}{suffix}"

def fancy_stylish_bio5(text):
    """Create stylish bio with butterfly style"""
    prefix = "◄⏤͟͞🦋꯭𝆺𝅥⃝꯭"
    suffix = " ◡̈⃝꯭🍃⃪⵿𝐆꯭𝗶𝗿̌𝗹꯭𐏓꯭ ᷞ ͦ ͮ ͕ͤ "
    
    # Style with mixed font weights and combining marks
    styled_text = ""
    for i, char in enumerate(text):
        if char.isalpha():
            if i % 3 == 0:
                styled_text += FONT_STYLES['serif_bold'](char) + "⵿̌"
            elif i % 3 == 1:
                styled_text += FONT_STYLES['serif_bold'](char) + "꯭ͥ"
            else:
                styled_text += FONT_STYLES['serif_bold'](char) + "ͫ"
            
            # Add decoration
            if i % 2 == 0:
                styled_text += "꯭"
            else:
                styled_text += "፝֟"
        else:
            styled_text += char
            
    return f"{prefix}{styled_text}{suffix}"

def fancy_stylish_bio6(text):
    """Create ISI style bio"""
    prefix = "ㅤㅤ❛ .𝁘ໍ - "
    suffix = " 𓂃• ‹𝟹"
    
    # Style with uppercase serif bold
    styled_text = ""
    for i, char in enumerate(text):
        if char.isalpha():
            styled_text += FONT_STYLES['serif_bold'](char.upper())
            # Add separator every other character
            if i < len(text) - 1 and i % 2 == 0:
                styled_text += "┣"
        else:
            styled_text += char
            
    return f"{prefix}{styled_text}{suffix}"

def fancy_stylish_bio7(text):
    """Create stylish black heart bio"""
    prefix = "◄⏤͟͟͞🍸⃝⃪🖤𝚩𝐋𝚲𝐂𝐊᭓┣𝚵𝚲𝐑𝚻𔘓⃭𓆩🖤𓆪"
    suffix = ""
    
    # Style with mixed characters
    styled_text = ""
    for i, char in enumerate(text):
        if char.isalpha():
            if char.lower() == 'a':
                styled_text += "𝚲"
            elif char.lower() == 'c':
                styled_text += "𐐕"
            elif char.lower() == 'e':
                styled_text += "𝐄"
            elif char.lower() == 'h':
                styled_text += "𝚮"
            elif char.lower() == 'l':
                styled_text += "𝐋"
            elif char.lower() == 'r':
                styled_text += "𝚪"
            elif char.lower() == 't':
                styled_text += "𝚻"
            else:
                # Alternate between styles
                if i % 2 == 0:
                    styled_text += FONT_STYLES['greek_math'](char.upper())
                else:
                    styled_text += FONT_STYLES['serif_bold'](char.upper())
        else:
            styled_text += char
            
    return f"{prefix}{styled_text}{suffix}"

# Add a command handler for bio styles
async def bio_styles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate fancy bio-style text for Telegram profiles."""
    if not context.args:
        await update.message.reply_text("Please provide a name after the command.\nExample: /bio_styles Aisha")
        return
    
    name = ' '.join(context.args)
    
    # Generate bio styles
    fancy_bios = [
        stylish_bio_accent(name),
        stylish_bio_clone(name),
        stylish_bio_sanatan(name),
        stylish_bio_anjali(name),
        stylish_bio_misty(name),
        stylish_bio_butterfly(name),
        stylish_bio_premium(name),
        stylish_bio_joker(name),
        stylish_bio_prashant(name),
        stylish_bio_innocent(name),
        stylish_bio_isi_u(name),
        stylish_bio_special(name),
        stylish_bio_miss(name),
        stylish_bio_prachi(name),
        stylish_bio_jasmine(name),
        stylish_bio_sath(name),
        stylish_bio_heart(name),
        stylish_bio_dark(name),
        stylish_bio_viskl(name),
        stylish_bio_black_heart(name),
        stylish_bio_infinity(name),
        stylish_bio_abstract(name),
        stylish_bio_arrow_style(name),
        stylish_bio_crystal(name),
        stylish_bio_waves(name),
        stylish_bio_neon(name),
        stylish_bio_royal(name),
        stylish_bio_gaming(name),
        stylish_bio_angel(name),
        stylish_bio_fire_ice(name),
        stylish_bio_cute(name),
        stylish_bio_diamond_crown(name),
        stylish_bio_elegant(name),
        stylish_bio_fancy_border(name),
        stylish_bio_shadow(name),
        stylish_bio_galaxy(name),
        stylish_bio_glitch(name),
        stylish_bio_magic(name),
        stylish_bio_retro(name),
        stylish_bio_tech(name),
        stylish_bio_cursed(name),
        stylish_bio_medieval(name),
        stylish_bio_boxed(name),
        stylish_bio_cool(name),
        stylish_bio_circled(name),
        stylish_bio_sparkles(name),
        stylish_bio_fireworks(name),
        stylish_bio_double_struck(name),
        stylish_bio_cyrillic(name),
        stylish_bio_script_bold(name),
        fancy_stylish_bio1(name),
        fancy_stylish_bio2(name),
        fancy_stylish_bio3(name),
        fancy_stylish_bio4(name),
        fancy_stylish_bio5(name),
        fancy_stylish_bio6(name),
        fancy_stylish_bio7(name),
        custom_frame(name)
    ]
    
    # Store the fancy bio texts for callback access
    context.user_data['fancy_bios'] = fancy_bios
    
    # Create keyboard with direct tap-to-copy functionality for each styled bio
    keyboard = []
    
    # Create a 4×4 grid layout for bio styles
    current_row = []
    for i, bio_text in enumerate(fancy_bios):
        display_text = bio_text[:20]  # Truncate to first 20 chars for display
        if len(bio_text) > 20:
            display_text += "..."
            
        button = InlineKeyboardButton(
            f"{i+1}. {display_text}", 
            callback_data=f"bio_{i}"
        )
        
        current_row.append(button)
        
        # If we have 4 buttons or this is the last bio, add the row to keyboard
        if len(current_row) == 4 or i == len(fancy_bios) - 1:
            keyboard.append(current_row)
            current_row = []
    
    # Add any remaining buttons if we didn't reach a multiple of 4
    if current_row:
        keyboard.append(current_row)
    
    await update.message.reply_text(
        f"✨ 𝗦𝗧𝗬𝗟𝗜𝗦𝗛 𝗕𝗜𝗢 𝗡𝗔𝗠𝗘 🇮🇳🍁 for '{name}':\n\nTap on any style to copy it!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Modified button_callback handler to handle bio styles
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks for copying styled text."""
    query = update.callback_query
    await query.answer()
    
    # Parse the callback data to determine what to copy
    data = query.data.split('_')
    
    if data[0] == 'font':
        # Handle font style copying
        style_index = int(data[1])
        styled_text = context.user_data.get('styled_fonts', [])[style_index]
        await query.message.reply_text(styled_text)
    elif data[0] == 'name':
        # Handle fancy name copying
        name_index = int(data[1])
        styled_name = context.user_data.get('styled_names', [])[name_index]
        await query.message.reply_text(styled_name)
    elif data[0] == 'letter':
        # Handle single letter copying
        letter_index = int(data[1])
        styled_letter = context.user_data.get('styled_letters', [])[letter_index]
        await query.message.reply_text(styled_letter)
    elif data[0] == 'bio':
        # Handle bio style copying
        bio_index = int(data[1])
        styled_bio = context.user_data.get('fancy_bios', [])[bio_index]
        await query.message.reply_text(styled_bio)
    elif data[0] == 'style':
        # Handle style font copying
        style_name = data[1]
        name = data[2]
        style_func = FONT_STYLES[style_name]
        styled_name = ''.join(style_func(c) for c in name)
        await query.message.reply_text(styled_name)
    else:
        await query.message.reply_text("Unknown button type.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_text = (
        "🤖 *Font Styles Bot Commands* 🤖\n\n"
        "/fancy [name] - Generate a random fancy stylized name\n"
        "/name_fonts [name] - Show all available font styles for a name\n"
        "/alphabet - Display the full alphabet in a random font style\n"
        "/letter [letter] - Show all font styles for a single letter\n"
        "/bio_styles [name] - Generate fancy stylish bios for Telegram\n"
        "/help - Show this help message"
    )
    await update.message.reply_text(help_text)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when the command /start is issued."""
    welcome_text = (
        "👋 Welcome to the Font Styles Bot! 🎨\n\n"
        "I can help you create fancy text styles for your name or any text.\n\n"
        "Try these commands:\n"
        "/fancy [name] - Get a random fancy styled name\n"
        "/name_fonts [name] - See your name in all available styles\n"
        "/bio_styles [name] - Get fancy bio styles for Telegram\n\n"
        "Type /help to see all available commands."
    )
    await update.message.reply_text(welcome_text)

async def fancy_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate a fancy styled name."""
    if not context.args:
        await update.message.reply_text("Please provide a name after /fancy\nExample: /fancy John")
        return

    name = ' '.join(context.args)
    
    # Generate multiple fancy names with emphasis on stylish bio designs
    fancy_names = []
    
    # Complete list of all bio styles
    bio_styles = [
        stylish_bio_accent,
        stylish_bio_clone,
        stylish_bio_sanatan,
        stylish_bio_anjali,
        stylish_bio_misty,
        stylish_bio_butterfly,
        stylish_bio_premium,
        stylish_bio_joker,
        stylish_bio_prashant,
        stylish_bio_innocent,
        stylish_bio_special,
        stylish_bio_miss,
        stylish_bio_prachi,
        stylish_bio_infinity,
        stylish_bio_abstract,
        stylish_bio_arrow_style,
        stylish_bio_crystal,
        stylish_bio_waves,
        stylish_bio_neon,
        stylish_bio_royal,
        stylish_bio_gaming,
        stylish_bio_angel,
        stylish_bio_fire_ice,
        stylish_bio_cute,
        stylish_bio_diamond_crown,
        stylish_bio_elegant,
        stylish_bio_fancy_border,
        stylish_bio_shadow,
        stylish_bio_galaxy,
        stylish_bio_glitch,
        stylish_bio_magic,
        stylish_bio_retro,
        stylish_bio_tech,
        stylish_bio_cursed,
        stylish_bio_medieval,
        stylish_bio_boxed,
        stylish_bio_cool,
        stylish_bio_circled,
        stylish_bio_sparkles,
        stylish_bio_fireworks,
        stylish_bio_double_struck,
        stylish_bio_cyrillic,
        stylish_bio_script_bold,
        fancy_stylish_bio1,
        fancy_stylish_bio2,
        fancy_stylish_bio3,
        fancy_stylish_bio4,
        fancy_stylish_bio5,
        fancy_stylish_bio6,
        custom_frame
    ]
    
    # Add some fixed special designs that don't need the actual name
    special_designs = [
        stylish_bio_isi_u(name),
        stylish_bio_jasmine(name),
        stylish_bio_sath(name),
        stylish_bio_heart(name),
        stylish_bio_dark(name),
        stylish_bio_viskl(name),
        stylish_bio_black_heart(name),
        custom_frame(name)
    ]
    
    # Add the special designs first
    fancy_names.extend(special_designs)
    
    # Add all bio styles one by one to ensure variety
    for style_func in bio_styles:
        fancy_names.append(style_func(name))
    
    # Store the fancy names in user_data for callback retrieval
    context.user_data['styled_names'] = fancy_names
    
    # Create inline keyboard with buttons arranged in a grid (4 buttons per row)
    keyboard = []
    current_row = []
    
    for i, fancy_text in enumerate(fancy_names):
        # Create a button for this fancy name
        display_text = fancy_text[:20]  # Truncate to first 20 chars for display
        if len(fancy_text) > 20:
            display_text += "..."
            
        button = InlineKeyboardButton(
            f"{i+1}. {display_text}", 
            callback_data=f"name_{i}"
        )
        
        # Add to current row
        current_row.append(button)
        
        # If we have 4 buttons or this is the last name, add the row to keyboard
        if len(current_row) == 4 or i == len(fancy_names) - 1:
            keyboard.append(current_row)
            current_row = []
    
    # Add any remaining buttons if we didn't reach a multiple of 4
    if current_row:
        keyboard.append(current_row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"𝗦𝗧𝗬𝗟𝗜𝗦𝗛 𝗡𝗔𝗠𝗘 🇮🇳🍁 for '{name}':",
        reply_markup=reply_markup
    )

async def show_alphabet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the alphabet in a random font style."""
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    style_name = random.choice(list(STYLE_NAMES.values()))
    style_function = FONT_STYLES[style_name]
    styled_alphabet = ''.join(style_function(c) for c in alphabet)
    
    await update.message.reply_text(
        f"Alphabet in {style_name.replace('_', ' ')} style:\n{styled_alphabet}"
    )

async def az_fonts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show a letter in all available font styles."""
    if not context.args or len(context.args[0]) != 1:
        await update.message.reply_text("Please provide a single letter after /letter\nExample: /letter A")
        return
    
    letter = context.args[0].upper()
    if not letter.isalpha():
        await update.message.reply_text("Please provide a valid letter (A-Z).")
        return
    
    results = []
    for style_num, style_name in STYLE_NAMES.items():
        style_func = FONT_STYLES[style_name]
        styled_letter = style_func(letter)
        results.append(f"{style_num}. {styled_letter}")
    
    await update.message.reply_text(f"Letter {letter} in all styles:\n" + "\n".join(results))

async def name_all_fonts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show a name in all available font styles."""
    if not context.args:
        await update.message.reply_text("Please provide a name after /name_fonts\nExample: /name_fonts John")
        return

    name = ' '.join(context.args)
    
    # Create inline keyboard with buttons arranged in a grid (4 buttons per row)
    keyboard = []
    current_row = []
    
    for style_num, style_name in STYLE_NAMES.items():
        try:
            style_func = FONT_STYLES[style_name]
            styled_name = ''.join(style_func(c) for c in name)
            
            # Create a button for this style
            button = InlineKeyboardButton(
                f"{style_num}. {styled_name}", 
                callback_data=f"style_{style_name}_{name}"
            )
            
            # Add to current row
            current_row.append(button)
            
            # If we have 4 buttons or this is the last style, add the row to keyboard
            if len(current_row) == 4 or style_num == max(STYLE_NAMES.keys()):
                keyboard.append(current_row)
                current_row = []
                
        except Exception as e:
            # If a style fails, skip it
            continue
    
    # Add any remaining buttons if we didn't reach a multiple of 4
    if current_row:
        keyboard.append(current_row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"Choose a style for '{name}':",
        reply_markup=reply_markup
    )

# Simple HTTP request handler for health checks
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is running')

def run_http_server():
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 8080))
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"Starting HTTP server on port {port}...")
    httpd.serve_forever()

# Update main function to register the new handler
def main():
    """Start the bot."""
    # Create the Application and pass it your bot's token
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("fancy", fancy_name))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("alphabet", show_alphabet))
    application.add_handler(CommandHandler("letter", az_fonts))
    application.add_handler(CommandHandler("name_fonts", name_all_fonts))
    application.add_handler(CommandHandler("bio_styles", bio_styles))
    
    # Add callback query handler for the buttons
    application.add_handler(CallbackQueryHandler(button_callback))

    # Start HTTP server in a separate thread for Render
    server_thread = threading.Thread(target=run_http_server)
    server_thread.daemon = True
    server_thread.start()

    # Start the Bot
    print("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 