# 示例数据生成脚本
# 用于演示系统功能，无需上传真实数据

import json
import random
from datetime import datetime, timedelta

def generate_demo_chat():
    """
    生成一个演示用的 QQ 群聊 JSON 文件
    包含虚构的消息数据，用于展示系统功能
    """
    
    # 虚构的群成员 (uin, name)
    members = [
        {"uin": 10001, "name": "张三"},
        {"uin": 10002, "name": "李四"},
        {"uin": 10003, "name": "王五"},
        {"uin": 10004, "name": "赵六"},
        {"uin": 10005, "name": "钱七"},
        {"uin": 10006, "name": "孙八"},
        {"uin": 10007, "name": "周九"},
        {"uin": 10008, "name": "吴十"},
        {"uin": 10009, "name": "郑十一"},
        {"uin": 10010, "name": "小明"},
    ]
    
    # 虚构的热词
    hot_words = [
        "好的", "哈哈哈", "确实", "太厉害了", "666",
        "牛", "加油", "没问题", "可以", "厉害",
        "真的吗", "哇", "不错", "棒", "支持"
    ]
    
    # 虚构的话题
    topics = [
        "今天天气真好", "周末去哪玩", "工作进展怎么样",
        "最近在看什么书", "有什么好吃的推荐", "游戏打的怎么样",
        "这个问题怎么解决", "明天见面吗", "收到了吗", "在吗"
    ]
    
    # 生成消息
    messages = []
    # 使用当前年份的数据更真实
    current_year = datetime.now().year
    start_date = datetime(current_year, 1, 1)
    
    for i in range(5000):  # 生成 5000 条消息
        # 随机时间
        days = random.randint(0, 364)
        hours = random.randint(0, 23)
        minutes = random.randint(0, 59)
        seconds = random.randint(0, 59)
        msg_time = start_date + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        
        # 随机发送者
        sender_info = random.choice(members)
        
        # 随机消息内容
        msg_type = random.choices(['text', 'image', 'voice'], weights=[0.8, 0.15, 0.05])[0]
        
        if msg_type == 'text':
            # 生成文本消息 - 增加热词出现频率
            parts = []
            # 70% 概率添加热词
            if random.random() < 0.7:
                parts.append(random.choice(hot_words))
            # 添加话题
            parts.append(random.choice(topics))
            # 30% 概率再添加一个热词
            if random.random() < 0.3:
                parts.append(random.choice(hot_words))
            text_content = " ".join(parts)
            
            message = {
                "time": int(msg_time.timestamp()),
                "sender": sender_info,
                "content": {"text": text_content}
            }
        elif msg_type == 'image':
            message = {
                "time": int(msg_time.timestamp()),
                "sender": sender_info,
                "content": {"text": "[图片]"}
            }
        else:  # voice
            message = {
                "time": int(msg_time.timestamp()),
                "sender": sender_info,
                "content": {"text": "[语音]"}
            }
        
        messages.append(message)
    
    # 按时间排序
    messages.sort(key=lambda x: x['time'])
    
    # 构建完整的 JSON 结构
    chat_data = {
        "chatName": "示例群聊（演示数据）",
        "messages": messages
    }
    
    return chat_data


if __name__ == "__main__":
    print("🎨 正在生成演示数据...")
    demo_data = generate_demo_chat()
    
    output_file = "demo_chat.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(demo_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 演示数据已生成: {output_file}")
    print(f"📊 包含 {len(demo_data['messages'])} 条消息")
    print(f"👥 涉及 10 位虚构成员")
    print(f"💡 可以使用此文件测试系统功能")
