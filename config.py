"""模块名称：config

@Time: 2025-01-20 16:06:00
@Author: Yang208115
@File: config.py
@Desc: 存储爬虫运行所需的各种配置参数，包括目标URL、请求配置、存储配置等
"""

# 目标URL配置
TARGET_URL = "https://hrss.qingdao.gov.cn/ztzl_47/zcpd_47/tzgg_47/"

# 请求配置
REQUEST_CONFIG = {
    "timeout": 30,  # 请求超时时间（秒）
    "retries": 3,   # 重试次数
    "delay": 1,     # 请求间隔（秒）
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
}

# 数据存储配置
STORAGE_CONFIG = {
    "data_file": "data/announcements.json",
    "log_file": "logs/scraper.log",
    "backup_enabled": True,
    "backup_count": 7  # 保留最近7天的备份
}

# 爬取配置
SCRAPE_CONFIG = {
    "check_interval": 1200,  # 检查间隔（秒），默认5分钟
    "max_announcements": 50,  # 最多保存的通知数量
    "date_format": "%Y-%m-%d %H:%M:%S"
}

# 通知配置
NOTIFICATION_CONFIG = {
    "console_enabled": True,
    "file_enabled": True,
    "windows_notification_enabled": True,  # Windows系统通知，默认启用
    
    # 邮件通知配置
    "email_enabled": False,  # 设置为True启用邮件通知
    "email_config": {
        "smtp_server": "smtp.qq.com",  # QQ邮箱SMTP服务器
        "smtp_port": 587,
        "sender_email": "your_email@qq.com",  # 发送方邮箱
        "sender_password": "your_app_password",  # QQ邮箱授权码
        "recipient_email": "recipient@qq.com"  # 接收方邮箱
    },
    
    # 企业微信通知配置
    "wechat_enabled": False,  # 设置为True启用企业微信通知
    "wechat_webhook": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY",
    
    # 钉钉通知配置
    "dingtalk_enabled": False,  # 设置为True启用钉钉通知
    "dingtalk_webhook": "https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN",
    
    # Telegram通知配置
    "telegram_enabled": False,  # 设置为True启用Telegram通知
    "telegram_bot_token": "YOUR_BOT_TOKEN",
    "telegram_chat_id": "YOUR_CHAT_ID"
}

# 日志配置
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5
}