# -*- coding: utf-8 -*-
import re
import json
import math
from datetime import datetime, timezone, timedelta
from collections import Counter

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        return json.load(f)

def extract_emojis(text):
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002702-\U000027B0"
        "\U0001F900-\U0001F9FF"
        "\U0001FA00-\U0001FA6F"
        "\U0001FA70-\U0001FAFF"
        "\U00002600-\U000026FF"
        "\U00002300-\U000023FF"
        "]",
        flags=re.UNICODE
    )
    return emoji_pattern.findall(text)

def is_emoji(char):
    if len(char) != 1:
        return False
    code = ord(char)
    emoji_ranges = [
        (0x1F600, 0x1F64F), (0x1F300, 0x1F5FF), (0x1F680, 0x1F6FF),
        (0x1F1E0, 0x1F1FF), (0x2702, 0x27B0), (0x1F900, 0x1F9FF),
        (0x1FA00, 0x1FA6F), (0x1FA70, 0x1FAFF), (0x2600, 0x26FF), (0x2300, 0x23FF),
    ]
    return any(start <= code <= end for start, end in emoji_ranges)

def parse_timestamp(ts):
    try:
        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        local_dt = dt.astimezone(timezone(timedelta(hours=8)))
        return local_dt.hour
    except:
        return None

def clean_text(text):
    """清理文本，去除表情、@、回复等干扰内容"""
    if not text:
        return ""
    
    # 1. 去除回复标记 [回复 xxx: yyy]
    text = re.sub(r'\[回复\s+[^\]]*\]', '', text)
    
    # 2. 去除@某人（包括中文、emoji昵称）
    text = re.sub(r'@[^\s\[\]@]+\s*', '', text)
    
    # 3. 循环去除所有方括号内容（如[图片][表情]等）
    prev = None
    while prev != text:
        prev = text
        text = re.sub(r'\[[^\[\]]*\]', '', text)
    
    # 4. 去除链接
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'www\.\S+', '', text)
    
    # 5. 去除多余空白
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def calculate_pmi(word, word_freq, total_words, char_freq):
    if len(word) < 2:
        return 0
    p_word = word_freq / total_words
    p_chars = 1.0
    for char in word:
        p_char = char_freq.get(char, 1) / total_words
        p_chars *= p_char
    if p_chars == 0:
        return 0
    return math.log2(p_word / p_chars) if p_word > 0 else 0

def calculate_entropy(neighbor_freq):
    total = sum(neighbor_freq.values())
    if total == 0:
        return 0
    entropy = 0
    for freq in neighbor_freq.values():
        p = freq / total
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy

def generate_time_bar(hour_counts, width=20):
    max_count = max(hour_counts.values()) if hour_counts else 1
    lines = []
    for hour in range(24):
        count = hour_counts.get(hour, 0)
        bar_len = int(count / max_count * width) if max_count > 0 else 0
        bar = '█' * bar_len + '░' * (width - bar_len)
        percentage = count * 100 / sum(hour_counts.values()) if sum(hour_counts.values()) > 0 else 0
        lines.append(f"  {hour:02d}:00 {bar} {count:>5} ({percentage:>4.1f}%)")
    return lines

def analyze_single_chars(texts):
    """分析单字的独立出现情况 - 来自旧版"""
    total_count = Counter()
    solo_count = Counter()
    boundary_count = Counter()
    punctuation = set('，。！？、；：""''（）,.!?;:\'"()[]【】《》<>…—～·')
    
    for text in texts:
        # 统计每个字的总出现次数
        for char in text:
            if re.match(r'^[\u4e00-\u9fffa-zA-Z]$', char):
                total_count[char] += 1
        
        # 统计单字消息
        clean_chars = [c for c in text if re.match(r'^[\u4e00-\u9fffa-zA-Z]$', c)]
        if len(clean_chars) == 1:
            solo_count[clean_chars[0]] += 1
        
        # 统计在边界位置的出现
        for i, char in enumerate(text):
            if not re.match(r'^[\u4e00-\u9fffa-zA-Z]$', char):
                continue
            left_ok = (i == 0) or (text[i-1] in punctuation) or (text[i-1].isspace())
            right_ok = (i == len(text)-1) or (text[i+1] in punctuation) or (text[i+1].isspace())
            if left_ok and right_ok:
                boundary_count[char] += 1
    
    result = {}
    for char in total_count:
        total = total_count[char]
        solo = solo_count[char]
        boundary = boundary_count[char]
        independent = solo + boundary * 0.5
        ratio = independent / total if total > 0 else 0
        result[char] = (total, independent, ratio)
    
    return result
