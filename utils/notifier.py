"""
模块名称：notifier
主要功能：Windows系统通知推送工具模块

@File: notifier.py
@Desc: 实现Windows系统通知和日志记录功能
"""

import logging
import platform
from typing import List, Dict
from plyer import notification
from config import NOTIFICATION_CONFIG


class MessageNotifier:
    """消息通知推送类。
    
    专注于Windows系统通知和日志记录。
    
    Attributes:
        logger (logging.Logger): 日志记录器
        config (dict): 通知配置信息
    """
    
    def __init__(self):
        """初始化通知器。"""
        self.logger = logging.getLogger(__name__)
        self.config = NOTIFICATION_CONFIG
            
    def send_windows_notification(self, title: str, message: str) -> bool:
        """发送Windows系统通知。
        
        Args:
            title: 通知标题
            message: 通知内容
            
        Returns:
            bool: 发送是否成功
        """
        if not self.config.get("windows_notification_enabled", True):
            return False
            
        if platform.system() != "Windows":
            self.logger.warning("当前系统不是Windows，无法发送系统通知")
            return False
            
        try:
            # 使用plyer库发送Windows系统通知
            notification.notify(
                title=title,
                message=message,
                app_name="通知监控",
                timeout=10,  # 通知显示时间（秒）
                toast=True   # 启用Windows 10/11 Toast通知
            )
            
            self.logger.info("✅ Windows系统通知发送成功")
            return True
                
        except Exception as e:
            self.logger.error(f"❌ Windows通知发送失败: {e}")
            return False
            
    def send_notification(self, announcements: List[Dict]) -> bool:
        """发送新通知公告提醒。
        
        Args:
            announcements: 新通知公告列表
            
        Returns:
            bool: 是否发送成功
        """
        if not announcements:
            return False
            
        # 生成通知内容
        title = f"青岛人社局新通知 ({len(announcements)}条)"
        
        if len(announcements) == 1:
            # 单条通知显示完整标题
            message = announcements[0]['title'][:100]  # 限制长度
        else:
            # 多条通知显示摘要
            message = f"发现{len(announcements)}条新通知，请查看日志获取详情"
            
        # 发送Windows系统通知
        success = self.send_windows_notification(title, message)
        
        # 记录详细日志
        self.logger.info("📋 新通知详情:")
        for i, announcement in enumerate(announcements, 1):
            self.logger.info(f"  {i}. {announcement['title']}")
            self.logger.info(f"     🔗 {announcement['url']}")
            
        return success