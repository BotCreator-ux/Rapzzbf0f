import warnings
import requests
import random
import string
import time
import os
import json
import codecs
import base64
import sys
import hashlib
import secrets
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import deque, Counter
import urllib3

# Menonaktifkan peringatan SSL / HTTP
warnings.filterwarnings('ignore')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

REGION_CHOICE = 1
THREAD_COUNT = 222
REQUEST_DELAY = 0
FAIL_SLEEP = 1

WATERMARK = 'VITIAN TEAM'
VERSION = 'v12'

consecutive_fails = 0
fail_lock = threading.Lock()
rate_limit_shown = False
last_success_time = time.time()
stuck_warning_shown = False
json_lock = threading.Lock()
ids_lock = threading.Lock()

generated_ids = []

# Kumpulan simbol untuk pembuatan nama acak
SYMBOLS = ['~', '!', '@', '#', '$', '%', '^', '&', '*', '-', '_', '+', '=', '|', '?', '/', '\\', '[', ']', '{', '}', '(', ')', '<', '>', '`', "'", '"', ':', ';', '.', ',', 'あ', 'い', 'う', 'え', 'お', 'か', 'き', 'く', 'け', 'こ', 'さ', 'し', 'す', 'せ', 'そ', 'た', 'ち', 'つ', 'て', 'と', 'な', 'に', 'ぬ', 'ね', 'の', 'は', 'ひ', 'ふ', 'へ', 'ほ', 'ま', 'み', 'む', 'め', 'も', '야', '유', '요', '라', '리', '루', '레', '로', '와', '워', 'ン', 'ァ', 'ィ', 'ゥ', 'ェ', 'ォ', 'ッ', 'ャ', 'ュ', 'ョ', '☆', '★', '○', '●', '◎', '◇', '◆', '□', '■', '♯', '♪', '♫', '♬', '♡', '♥', '♠', '♣', '♦', '✨', '⚡', '🔥', '💀', '🎮', '👑', '⭐', '🌟', '的', '一', '是', '了', '我', '不', '人', '在', '他', '有', '这', '个', '上', '们', '来', '到', '时', '大', '地', '为', '子', '中', '你', '说', '生', '国', '年', '着', '就', '那', '和', '要', '她', '出', '也', '得', '里', '后', '自', '以', '会', '家', '可', '下', '装', '过', '天', '去', '能', '对', '小', '多', '然', '于', '心', '学', '么', '之', '都', '好', '看', '起', '发', '当', '没', '成', '只', '如', '事', '把', '还', '用', '第', '样', '道', '想', '作', '种', '开', '手', '爱', '情', '王', '龙', '虎', '凤', '皇', '帝', '君', '子', '义', '武', '神', '仙', '魔', '鬼', '妖', '灵', '圣', '贤', 'ก', 'ข', 'ฃ', 'ค', 'ฅ', 'ฆ', 'ง', 'จ', 'ฉ', 'ช', 'ซ', 'ฌ', 'ญ', 'ฎ', 'ฏ', 'ฐ', 'ฑ', 'ฒ', 'ณ', 'ด', 'ต', 'ถ', 'ท', 'ธ', 'น', 'บ', 'ป', 'ผ', 'ฝ', 'พ', 'ฟ', 'ภ', 'ม', 'ย', 'ร', 'ฤ', 'ล', 'ว', 'ศ', 'ษ', 'ส', 'ห', 'ฬ', 'อ', 'ฮ', 'ะ', 'า', 'ำ', 'ิ', 'ี', 'à', 'á', 'ả', 'ã', 'ạ', 'ă', 'ằ', 'ắ', 'ẳ', 'ẵ', 'ặ', 'â', 'ầ', 'ấ', 'ẩ', 'ẫ', 'ậ', 'è', 'é', 'ẻ', 'ẽ', 'ẹ', 'ê', 'ề', 'ế', 'ể', 'ễ', 'ệ', 'ì', 'í', 'ỉ', 'ĩ', 'ị', 'ò', 'ó', 'ỏ', 'õ', 'ọ', 'ô', 'ồ', 'ố', 'ổ', 'ỗ', 'ộ', 'ơ', 'ờ', 'ớ', 'ở', 'ỡ', 'ợ', '가', '나', '다', '라', '마', '바', '사', '아', '자', '차', '카', '타', '파', '하', '갸', '냐', '댜', '랴', '먀', '뱌', '샤', '야', '쟈', '챠', '커', '터', '퍼', '허', '거', '너', '더', '러', '머', '버', '서', '어', '저', '처', '커', '터', '퍼', 'А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'З', 'И', 'Й', 'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У', 'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ъ', 'Ы', 'Ь', 'Э', 'Ю', 'Я', 'а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'ا', 'ب', 'ت', 'ث', 'ج', 'ح', 'خ', 'د', 'ذ', 'ر', 'ز', 'س', 'ش', 'ص', 'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ك', 'ل', 'م', 'ن', 'अ', 'आ', 'इ', 'ई', 'उ', 'ऊ', 'ऋ', 'ए', 'ऐ', '오', 'औ', 'क', 'ख', 'ग', 'घ', 'ङ', 'च', 'छ', 'ज', 'झ', 'ञ', 'ट', 'ठ', 'ڈ', 'ढ', '♛', '♚', '♔', '♕', '♦', '◊', '♤', '♧', '⭕', '❌', '❎', '🌀', '🌊', '🔥', '❄', '☀', '🌙', '☁', '🌈', '☔', '⚙', '🔧', '🔨', '⚒', '🔪', '⚔', '🛡', '🏹', '🔮', '💎', '🀄', '🃏', '🎯', '🏆', '🎖']

class Colors:
    RESET = '\x1b[0m'
    BOLD = '\x1b[1m'
    BLINK = '\x1b[5m'
    BG_BLACK = '\x1b[40m'
    BG_RED = '\x1b[41m'
    BG_GREEN = '\x1b[42m'
    BG_YELLOW = '\x1b[43m'
    BG_BLUE = '\x1b[44m'
    BG_MAGENTA = '\x1b[45m'
    BG_CYAN = '\x1b[46m'
    BG_WHITE = '\x1b[47m'
    BG_BRIGHT_RED = '\x1b[101m'
    BG_BRIGHT_GREEN = '\x1b[102m'
    BG_BRIGHT_YELLOW = '\x1b[103m'
    BG_BRIGHT_BLUE = '\x1b[104m'
    BG_BRIGHT_MAGENTA = '\x1b[105m'
    BG_BRIGHT_CYAN = '\x1b[106m'
    BLACK = '\x1b[30m'
    RED = '\x1b[31m'
    GREEN = '\x1b[32m'
    YELLOW = '\x1b[33m'
    BLUE = '\x1b[34m'
    MAGENTA = '\x1b[35m'
    CYAN = '\x1b[36m'
    WHITE = '\x1b[37m'
    BRIGHT_WHITE = '\x1b[97m'

C = Colors()

def generate_cool_name():
    base = 'Vitian'
    num = random.randint(10, 999)
    pattern = random.choice([1, 2, 3, 4, 5, 6])
    
    if pattern == 1:
        s = random.choice(SYMBOLS)
        name = f"{s}{base}{num}"
    elif pattern == 2:
        s = random.choice(SYMBOLS)
        name = f"{base}{num}{s}"
    elif pattern == 3:
        s1 = random.choice(SYMBOLS)
        s2 = random.choice(SYMBOLS)
        name = f"{s1}{s2}{base}{num}"
    elif pattern == 4:
        s1 = random.choice(SYMBOLS)
        s2 = random.choice(SYMBOLS)
        name = f"{base}{num}{s1}{s2}"
    elif pattern == 5:
        s = random.choice(SYMBOLS)
        name = f"{s}{base}{num}{s}"
    else:
        name = f"{base}{num}"
        
    if random.random() > 0.85:
        name = name.upper()
    elif random.random() > 0.7:
        name = name.lower()
        
    if len(name) > 12:
        name = name[:12]
    return name

def generate_password():
    digits = ''.join(random.choices(string.digits, k=random.randint(4, 6)))
    letters = ''.join(random.choices(string.ascii_uppercase, k=random.randint(3, 5)))
    return f"VITIAN{digits}{letters}"

def get_color_for_digit(count):
    if count >= 11:
        return C.BLINK + C.BG_BRIGHT_MAGENTA + C.BRIGHT_WHITE + C.BOLD
    if count >= 10:
        return C.BLINK + C.BG_BRIGHT_RED + C.BRIGHT_WHITE + C.BOLD
    if count >= 9:
        return C.BG_BRIGHT_MAGENTA + C.BRIGHT_WHITE + C.BOLD
    if count >= 8:
        return C.BG_BRIGHT_RED + C.BRIGHT_WHITE + C.BOLD
    if count >= 7:
        return C.BG_RED + C.BRIGHT_WHITE + C.BOLD
    if count >= 6:
        return C.BG_MAGENTA + C.BRIGHT_WHITE + C.BOLD
    if count >= 5:
        return C.BG_BRIGHT_YELLOW + C.BLACK + C.BOLD
    if count >= 4:
        return C.BG_YELLOW + C.BLACK + C.BOLD
    return C.WHITE

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DEVICE_FILE = os.path.join(CURRENT_DIR, '.device_id')

def get_device_fingerprint():
    if os.path.exists(DEVICE_FILE):
        with open(DEVICE_FILE, 'r') as f:
            return f.read().strip()
    raw = secrets.token_hex(16)
    device_id = hashlib.sha256(raw.encode()).hexdigest()[:32]
    with open(DEVICE_FILE, 'w') as f:
        f.write(device_id)
    return device_id

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_stuck_warning():
    global stuck_warning_shown
    if stuck_warning_shown:
        return
    stuck_warning_shown = True
    print()
    print(f"{C.BG_BRIGHT_RED}{C.BRIGHT_WHITE}{C.BOLD} PERINGATAN {C.RESET}")
    print(f"{C.YELLOW}[!] Tidak ada generate dalam 10 detik terakhir{C.RESET}")
    print(f"{C.YELLOW}[!] Kemungkinan terkena RATE LIMIT dari server Garena{C.RESET}")
    print(f"{C.CYAN}[!] Solusi: Aktifkan Airplane Mode atau Ganti IP menggunakan VPN{C.RESET}")
    stuck_warning_shown = False

# Kumpulan device pool yang disimulasikan
REGION_MAP = {
    1: {'code': 'ID', 'name': 'INDONESIA', 'lang': 'id'},
    2: {'code': 'ME', 'name': 'MIDDLE EAST', 'lang': 'ar'},
    3: {'code': 'IND', 'name': 'INDIA', 'lang': 'hi'},
    4: {'code': 'TH', 'name': 'THAILAND', 'lang': 'th'},
    5: {'code': 'VN', 'name': 'VIETNAM', 'lang': 'vi'},
    6: {'code': 'BD', 'name': 'BANGLADESH', 'lang': 'bn'},
    7: {'code': 'PK', 'name': 'PAKISTAN', 'lang': 'ur'},
    8: {'code': 'TW', 'name': 'TAIWAN', 'lang': 'zh'},
    9: {'code': 'CIS', 'name': 'RUSSIA', 'lang': 'ru'},
    10: {'code': 'SAC', 'name': 'SPAIN', 'lang': 'es'},
    11: {'code': 'BR', 'name': 'BRAZIL', 'lang': 'pt'}
}

SELECTED = REGION_MAP.get(REGION_CHOICE, REGION_MAP[1])
REGION = SELECTED['code']
REGION_NAME = SELECTED['name']
REGION_LANG = {REGION: SELECTED['lang']}

DEVICE_POOL = []
samsung = [f"SM-{c}{random.randint(100, 999)}" for _ in range(2000) for c in 'AGNFMSJE']
xiaomi = [f"{p} {random.randint(7, 14)}" for _ in range(1500) for p in ['Redmi Note', 'Redmi', 'Poco F', 'Poco X', 'Mi', 'Xiaomi', 'Redmi K', 'Poco M']]
oppo = [f"OPPO {m}{random.randint(2, 9999)}" for _ in range(1200) for m in ['CPH', 'Find X', 'Reno', 'A', 'F', 'R', 'K']]
vivo = [f"vivo {m}{random.randint(1, 9999)}" for _ in range(1200) for m in ['V', 'X', 'Y', 'T', 'S', 'U', 'Z']]
realme = [f"Realme {m}{random.randint(7, 70)}" for _ in range(1000) for m in ['', ' Pro', ' GT ', ' C', ' Narzo ', ' X', ' U']]
oneplus = [f"OnePlus {random.randint(8, 14)}" for _ in range(800)]
moto = [f"Moto {m}{random.randint(10, 100)}" for _ in range(800) for m in ['G', 'E', 'Edge ', 'Z', 'X']]
google = [f"Pixel {random.randint(3, 8)}" for _ in range(500)]
sony = [f"Xperia {random.randint(1, 5)} {chr(65 + random.randint(0, 2))}" for _ in range(400)]
nokia = [f"Nokia {random.randint(1, 9)}.{random.randint(1, 3)}" for _ in range(300)]
lg = [f"LG {chr(65 + random.randint(0, 15))}{random.randint(10, 99)}" for _ in range(300)]
honor = [f"Honor {random.randint(10, 70)}" for _ in range(300)]
asus = [f"ASUS Zenfone {random.randint(5, 10)}" for _ in range(300)]
other = list(('ASUS_I005DA', 'ASUS ROG Phone 5', 'Nothing Phone 1', 'Nothing Phone 2', 'SHARP AQUOS R8', 'Motorola Edge', 'Nubia RedMagic', 'Black Shark', 'Realme GT', 'Poco F4', 'iQOO 9', 'Oppo Find N', 'Vivo X Fold')) * 200

all_models = samsung + xiaomi + oppo + vivo + realme + oneplus + moto + google + sony + nokia + lg + honor + asus + other
brands = ['samsung', 'xiaomi', 'oppo', 'vivo', 'realme', 'oneplus', 'motorola', 'asus', 'google', 'sony', 'nokia', 'lg', 'honor', 'poco', 'iqoo', 'nubia', 'blackshark', 'nothing']
android_versions = ['9', '10', '11', '12', '13', '14', '15', '16']

for _ in range(50000):
    DEVICE_POOL.append({
        'model': random.choice(all_models),
        'brand': random.choice(brands),
        'android': random.choice(android_versions)
    })

HEX_KEY = bytes.fromhex('32656534343831396539623435393838343531343130363762323831363231383734643064356437616639643866376530306331653534373135623764316533')

def get_random_ip():
    return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}"

def get_headers():
    device = random.choice(DEVICE_POOL)
    return {
        'User-Agent': f"GarenaMSDK/4.0.39({device['model']};Android {device['android']};en;ID;)",
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip',
        'Connection': 'Keep-Alive',
        'X-Unity-Version': '2018.4.11f1',
        'X-GA': f"v1 {random.randint(100000, 999999)}",
        'X-Forwarded-For': get_random_ip(),
        'X-Real-IP': get_random_ip()
    }

def get_headers_form():
    h = get_headers()
    h['Content-Type'] = 'application/x-www-form-urlencoded'
    return h

def encode_varint(n):
    if n < 0:
        return b''
    result = []
    while True:
        byte = n & 127
        n >>= 7
        if n:
            byte |= 128
        result.append(byte)
        if not n:
            break
    return bytes(result)

def create_proto_field(field_num, value):
    if isinstance(value, dict):
        nested = b''
        for k, v in value.items():
            nested += create_proto_field(k, v)
        header = (field_num << 3) | 2
        return encode_varint(header) + encode_varint(len(nested)) + nested
    elif isinstance(value, int):
        header = (field_num << 3) | 0
        return encode_varint(header) + encode_varint(value)
    elif isinstance(value, (str, bytes)):
        encoded_val = value.encode() if isinstance(value, str) else value
        header = (field_num << 3) | 2
        return encode_varint(header) + encode_varint(len(encoded_val)) + encoded_val
    return b''

def build_proto(fields):
    return b''.join(create_proto_field(k, v) for k, v in fields.items())

def aes_encrypt(hex_data):
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad
    data = bytes.fromhex(hex_data)
    aes_key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(data, AES.block_size))

def encrypt_api(plain_hex):
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad
    plain = bytes.fromhex(plain_hex)
    aes_key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(plain, AES.block_size)).hex()

def major_login(uid, password, access_token, open_id, region):
    try:
        lang = REGION_LANG.get(region, 'en')
        payload_parts = [
            b'\x1a\x132025-08-30 05:19:21"\tfree fire(\x01:\x081.114.13B2Android OS 9 / API-28 (PI/rel.cjw.20220518.114133)J\x08HandheldR\nATM MobilsZ\x04WIFI`\xb6\nh\xee\x05r\x03300z\x1fARMv7 VFPv3 NEON VMH | 2400 | 2\x80\x01\xc9\x0f\x8a\x01\x0fAdreno (TM) 640\x92\x01\rOpenGL ES 3.2\x9a\x01+Google|dfa4ab4b-9dc4-454e-8065-e70c733fa53f\xa2\x01\x0e105.235.139.91\xaa\x01\x02',
            lang.encode('ascii'),
            b'\xb2\x01 1d8ec0240ede109973f3321b9354b44d\xba\x01\x014\xc2\x01\x08Handheld\xca\x01\x10Asus ASUS_I005DA\xea\x01@afcfbf13334be42036e4f742c80b956344bed760ac91b3aff9b607a610ab4390\xf0\x01\x01\xca\x02\nATM Mobils\xd2\x02\x04WIFI\xca\x03 7428b253defc164018c604a1ebbfebdf\xe0\x03\xa8\x81\x02\xe8\x03\xf6\xe5\x01\xf0\x03\xaf\x13\xf8\x03\x84\x07\x80\x04\xe7\xf0\x01\x88\x04\xa8\x81\x02\x90\x04\xe7\xf0\x01\x98\x04\xa8\x81\x02\xc8\x04\x01\xd2\x04=/data/app/com.dts.freefireth-PdeDnOilCSFn37p1AH_FLg==/lib/arm\xe0\x04\x01\xea\x04_2087f61c19f57f2af4e7feff0b24d9d9|/data/app/com.dts.freefireth-PdeDnOilCSFn37p1AH_FLg==/base.apk\xf0\x04\x03\xf8\x04\x01\x8a\x05\x0232\x9a\x05\n2019118692\xb2\x05\tOpenGLES2\xb8\x05\xff\x7f\xc0\x05\x04\xe0\x05\xf3F\xea\x05\x07android\xf2\x05pKqsHT5ZLWrYljNb5Vqh//yFRlaPHSO9NWSQsVvOmdhEEn7W+VHNUK+Q+fduA3ptNrGB0Ll0LRz3WW0jOwesLj6aiU7sZ40p8BfUE/FI/jzSTwRe2\xf8\x05\xfb\xe4\x06\x88\x06\x01\x90\x06\x01\x9a\x06\x014\xa2\x06\x014\xb2\x06"GQ@O\x00\x0e^\x00D\x06UA\x0ePM\r\x13hZ\x07T\x06\x0cm\\V\x0ejYV;\x0bU5'
        ]
        payload = b''.join(payload_parts)
        url = 'https://loginbp.common.ggbluefox.com/MajorLogin' if region in ('ME', 'TH') else 'https://loginbp.ggblueshark.com/MajorLogin'
        
        headers = {
            'Accept-Encoding': 'gzip',
            'Authorization': 'Bearer',
            'Connection': 'Keep-Alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Expect': '100-continue',
            'Host': 'loginbp.ggblueshark.com' if region in ('ME', 'TH') else 'loginbp.common.ggbluefox.com',
            'ReleaseVersion': 'OB54', # Sesuai permintaan: DIUBAH KE OB54
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 9; ASUS_I005DA Build/PI)',
            'X-GA': 'v1 1',
            'X-Unity-Version': '2018.4.11f1'
        }
        
        data = payload.replace(b'afcfbf13334be42036e4f742c80b956344bed760ac91b3aff9b607a610ab4390', access_token.encode())
        data = data.replace(b'1d8ec0240ede109973f3321b9354b44d', open_id.encode())
        d = encrypt_api(data.hex())
        
        session = requests.Session()
        session.verify = False
        response = session.post(url, headers=headers, data=bytes.fromhex(d), timeout=15)
        
        if response.status_code == 200 and len(response.text) > 10:
            jwt_start = response.text.find('eyJ')
            if jwt_start != -1:
                jwt_token = response.text[jwt_start:]
                second_dot = jwt_token.find('.', jwt_token.find('.') + 1)
                if second_dot != -1:
                    jwt_token = jwt_token[:second_dot + 44]
                
                parts = jwt_token.split('.')
                if len(parts) >= 2:
                    payload_part = parts[1]
                    padding = (4 - len(payload_part) % 4)
                    if padding != 4:
                        payload_part += '=' * padding
                    decoded = base64.urlsafe_b64decode(payload_part)
                    data = json.loads(decoded)
                    account_id = data.get('account_id') or data.get('external_id')
                    if account_id:
                        return {'account_id': str(account_id), 'jwt_token': jwt_token}
    except Exception:
        pass
    return {'account_id': 'N/A', 'jwt_token': ''}

session_pool = deque()
session_lock = threading.Lock()

def get_session():
    with session_lock:
        if session_pool:
            return session_pool.popleft()
    s = requests.Session()
    s.verify = False
    return s

def return_session(s):
    with session_lock:
        if len(session_pool) < THREAD_COUNT * 2:
            session_pool.append(s)
        else:
            s.close()

for _ in range(min(10, THREAD_COUNT)):
    s = requests.Session()
    s.verify = False
    session_pool.append(s)

running = True
stats = {
    'total': 0, 'same_4plus': 0, 'same_4': 0, 'same_5': 0, 'same_6': 0,
    'same_7': 0, 'same_8': 0, 'same_9': 0, 'same_10': 0, 'same_11plus': 0,
    'start_time': time.time()
}
stats_lock = threading.Lock()
stuck_monitor_active = True

def stuck_monitor():
    while stuck_monitor_active:
        time.sleep(10)
        if not running:
            return
        elapsed = time.time() - last_success_time
        if elapsed > 10 and stats['total'] > 0:
            show_stuck_warning()

def count_same_digits(account_id):
    aid = str(account_id)
    if not aid.isdigit() or len(aid) < 5:
        return 0
    analyzed = aid[1:]
    digit_counts = Counter(analyzed)
    return max(digit_counts.values()) if digit_counts else 0

def save_account_v3(account_data, user_hash):
    base_folder = 'Vitian'
    all_folder = os.path.join(base_folder, 'allaccount')
    os.makedirs(all_folder, exist_ok=True)
    accounts_json = os.path.join(all_folder, 'accounts.json')
    
    with json_lock:
        existing_accounts = []
        if os.path.exists(accounts_json):
            try:
                with open(accounts_json, 'r', encoding='utf-8') as f:
                    existing_accounts = json.load(f)
                    if not isinstance(existing_accounts, list):
                        existing_accounts = []
            except Exception:
                existing_accounts = []
        
        existing_accounts.append(account_data)
        with open(accounts_json, 'w', encoding='utf-8') as f:
            json.dump(existing_accounts, f, indent=2, ensure_ascii=False)
            
    same_count = account_data.get('same_digit_count', 0)
    if same_count >= 4:
        special_folder = os.path.join(base_folder, f"special_{user_hash}")
        os.makedirs(special_folder, exist_ok=True)
        
        id_file = os.path.join(special_folder, 'id.txt')
        with open(id_file, 'a', encoding='utf-8') as f:
            f.write(f"{account_data['account_id']}\n")
            
        cariid_file = os.path.join(special_folder, 'cariid.txt')
        if not os.path.exists(cariid_file):
            with open(cariid_file, 'w', encoding='utf-8') as f:
                f.write('# ===================================================\n')
                f.write('# CARI AKUN SAME DIGIT\n')
                f.write('# Tekan Ctrl+F lalu ketik [digit] misal [7] untuk same digit 7\n')
                f.write('# Format: [digit] uid | account_id | password\n')
                f.write('# ===================================================\n\n')
                
        with open(cariid_file, 'a', encoding='utf-8') as f:
            f.write(f"[{same_count}] {account_data['uid']} | {account_data['account_id']} | {account_data['password']}\n")

def print_output(no, account_id, same_count):
    color = get_color_for_digit(same_count)
    if same_count >= 4:
        print(f"{color}[{no}] {account_id} | {same_count}x{C.RESET}")
    else:
        print(f"{C.WHITE}[{no}] {account_id}{C.RESET}")

def generate_account():
    if not running:
        return None
    session = get_session()
    for retry in range(2):
        try:
            password = generate_password()
            name = generate_cool_name()
            
            resp = session.post(
                'https://100067.connect.garena.com/api/v2/oauth/guest:register',
                headers=get_headers(),
                json={'app_id': 100067, 'client_type': 2, 'password': password, 'source': 2},
                timeout=15
            )
            
            if resp.status_code == 200:
                data = resp.json()
                if 'data' in data and 'uid' in data['data']:
                    uid = data['data']['uid']
                    time.sleep(0.03)
                    
                    resp2 = session.post(
                        'https://100067.connect.garena.com/oauth/guest/token/grant',
                        headers=get_headers_form(),
                        data={'uid': uid, 'password': password, 'response_type': 'token', 'client_type': '2', 'client_secret': HEX_KEY, 'client_id': '100067'},
                        timeout=15
                    )
                    
                    if resp2.status_code == 200:
                        token_data = resp2.json()
                        open_id = token_data.get('open_id', '')
                        access_token = token_data.get('access_token', '')
                        
                        if open_id and access_token:
                            keystream = [48, 48, 48, 50, 48, 49, 55, 48, 48, 48, 48, 48, 50, 48, 49, 55, 48, 48, 48, 48, 48, 50, 48, 49, 55, 48, 48, 48, 48, 48, 50, 48]
                            encoded = ''
                            for i in range(len(open_id)):
                                encoded += chr(ord(open_id[i]) ^ keystream[i % len(keystream)])
                                
                            hex_str = ''.join(c if 32 <= ord(c) <= 126 else f"\\u{ord(c):04x}" for c in encoded)
                            field = codecs.decode(hex_str, 'unicode_escape').encode('latin1')
                            
                            url_major = 'https://loginbp.common.ggbluefox.com/MajorRegister' if REGION in ('ME', 'TH') else 'https://loginbp.ggblueshark.com/MajorRegister'
                            lang_code = REGION_LANG.get(REGION, 'en')
                            
                            payload = {1: name, 2: access_token, 3: open_id, 5: 102000007, 6: 4, 7: 1, 13: 1, 14: field, 15: lang_code, 16: 1, 17: 1}
                            payload_bytes = build_proto(payload)
                            encrypted_payload = aes_encrypt(payload_bytes.hex())
                            
                            headers_major = {
                                'Accept-Encoding': 'gzip', 'Authorization': 'Bearer', 'Connection': 'Keep-Alive',
                                'Content-Type': 'application/x-www-form-urlencoded', 'Expect': '100-continue',
                                'Host': 'loginbp.ggblueshark.com' if REGION in ('ME', 'TH') else 'loginbp.common.ggbluefox.com',
                                'ReleaseVersion': 'OB54', # Sesuai permintaan: DIUBAH KE OB54
                                'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 9; ASUS_I005DA Build/PI)',
                                'X-GA': 'v1 1', 'X-Unity-Version': '2018.4.11f1'
                            }
                            
                            session.post(url_major, headers=headers_major, data=encrypted_payload, timeout=15)
                            time.sleep(0.03)
                            
                            login_result = major_login(uid, password, access_token, open_id, REGION)
                            account_id = login_result.get('account_id', 'N/A')
                            
                            if account_id != 'N/A':
                                return_session(session)
                                global last_success_time
                                last_success_time = time.time()
                                return {'uid': uid, 'password': password, 'name': name, 'account_id': account_id, 'success': True}
        except Exception:
            pass
        time.sleep(0.5)
        
    return_session(session)
    return None

def worker():
    user_hash = hashlib.md5(get_device_fingerprint().encode()).hexdigest()[:8]
    while running:
        account = generate_account()
        if account and account.get('success'):
            uid = account['uid']
            aid = account['account_id']
            if aid == 'N/A':
                aid = str(uid)
            password = account['password']
            name = account['name']
            
            same_count = count_same_digits(aid)
            with stats_lock:
                stats['total'] += 1
                if same_count >= 4:
                    stats['same_4plus'] += 1
                    if same_count == 4:
                        stats['same_4'] += 1
                    elif same_count == 5:
                        stats['same_5'] += 1
                    elif same_count == 6:
                        stats['same_6'] += 1
                    elif same_count == 7:
                        stats['same_7'] += 1
                    elif same_count == 8:
                        stats['same_8'] += 1
                    elif same_count == 9:
                        stats['same_9'] += 1
                    elif same_count == 10:
                        stats['same_10'] += 1
                    else:
                        stats['same_11plus'] += 1
                current_no = stats['total']
                
            print_output(current_no, aid, same_count)
            account_info = {
                'uid': uid, 'password': password, 'account_id': aid, 'name': name,
                'region': REGION_NAME, 'same_digit_count': same_count,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'watermark': WATERMARK
            }
            save_account_v3(account_info, user_hash)
        else:
            time.sleep(FAIL_SLEEP)
        time.sleep(REQUEST_DELAY)

def main():
    # Deklarasi global ditaruh di paling atas fungsi utama
    global running, stuck_monitor_active
    
    clear_screen()
    print(f"{C.BG_BLUE}{C.BRIGHT_WHITE}{C.BOLD} VITIAN GENERATOR {VERSION} - RUNNING {C.RESET}\n")
    print(f"{C.CYAN}[MODE] BYPASS VERSION{C.RESET}")
    print(f"{C.CYAN}[REGION] {REGION_NAME}{C.RESET}\n")
    print(f"{C.YELLOW}[OUTPUT] VITIANGEN/{C.RESET}\n")
    
    try:
        with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
            futures = [executor.submit(worker) for _ in range(THREAD_COUNT)]
            for future in as_completed(futures):
                if not running:
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
                future.result()
    except KeyboardInterrupt:
        print(f"\n{C.RED}[STOP]{C.RESET}")
        running = False
        stuck_monitor_active = False
    except Exception as e:
        print(f"\n{C.RED}[ERR] {e}{C.RESET}")
        
    time.sleep(1)
    elapsed = time.time() - stats['start_time']
    print()
    print(f"{C.CYAN}VITIAN V12 - DONE{C.RESET}")
    print(f"{C.GREEN}[TOTAL] {stats['total']}{C.RESET}")
    print(f"{C.YELLOW}[SAME4+] {stats['same_4plus']}{C.RESET}")
    print(f"{C.CYAN}[TIME] {elapsed:.1f}s{C.RESET}")
    if elapsed > 0:
        print(f"{C.CYAN}[SPEED] {stats['total']/elapsed:.2f} acc/s{C.RESET}")

if __name__ == '__main__':
    try:
        from Crypto.Cipher import AES
        from Crypto.Util.Padding import pad
        
        monitor_thread = threading.Thread(target=stuck_monitor, daemon=True)
        monitor_thread.start()
        
        main()
    except ImportError:
        print(f"{C.RED}[ERR] pip install pycryptodome{C.RESET}")
        sys.exit(0)
