#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块名称：scraper
@Time: 2025-01-20 16:06:00
@Author: Yang208115
@File: scraper.py
@Desc: 通知公告的自动爬取、解析和新通知检测功能
"""

import requests
import json
import os
import sys
import time
import logging
from datetime import datetime
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from config import TARGET_URL, REQUEST_CONFIG, STORAGE_CONFIG, SCRAPE_CONFIG, LOGGING_CONFIG
from utils.notifier import MessageNotifier


class QingdaoHRSScraper:
    """
    Attributes:
        target_url (str): 目标网站URL
        session (requests.Session): HTTP会话对象
        data_file (str): 数据存储文件路径
        logger (logging.Logger): 日志记录器
    """
    
    def __init__(self):
        """初始化爬虫。"""
        self.target_url = TARGET_URL
        self.session = requests.Session()
        self.session.headers.update(REQUEST_CONFIG["headers"])
        self.data_file = STORAGE_CONFIG["data_file"]
        self.notifier = MessageNotifier()
        self.setup_logging()
        
    def setup_logging(self):
        """设置日志配置"""
        logging.basicConfig(
            level=getattr(logging, LOGGING_CONFIG["level"]),
            format=LOGGING_CONFIG["format"],
            handlers=[
                logging.FileHandler(STORAGE_CONFIG["log_file"], encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def fetch_page_content(self) -> Optional[str]:
        """获取网页内容"""
        try:
            self.logger.info(f"正在访问: {self.target_url}")
            
            response = self.session.get(
                self.target_url,
                timeout=REQUEST_CONFIG["timeout"]
            )
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            self.logger.info(f"成功获取网页内容，状态码: {response.status_code}")
            return response.text
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"获取网页内容失败: {e}")
            return None
            
    def parse_announcements(self, html_content: str) -> List[Dict]:
        """解析通知公告信息"""
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            announcements = []
            
            # 根据网页结构查找通知公告链接
            # 需要分析具体的HTML结构来确定选择器
            self.logger.info("开始解析通知公告信息...")
            
            # 暂时使用通用的链接查找方法
            # 实际使用时需要根据页面结构调整选择器
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href')
                text = link.get_text(strip=True)
                
                # 过滤出通知公告相关链接
                if self.is_announcement_link(text, href):
                    announcement = {
                        'id': self.generate_id(text, href),
                        'title': text,
                        'url': self.get_full_url(href),
                        'scraped_at': datetime.now().strftime(SCRAPE_CONFIG["date_format"]),
                        'is_new': True
                    }
                    announcements.append(announcement)
                    
            self.logger.info(f"解析完成，找到 {len(announcements)} 条通知")
            return announcements
            
        except Exception as e:
            self.logger.error(f"解析通知公告失败: {e}")
            return []
            
    def is_announcement_link(self, text: str, href: str) -> bool:
        """判断是否为通知公告链接"""
        if not text or not href:
            return False
            
        # 通知公告的关键词
        keywords = ['通知', '公告', '关于', '职称', '评审', '报送']
        
        # 检查链接文本是否包含关键词
        return any(keyword in text for keyword in keywords)
        
    def generate_id(self, title: str, url: str) -> str:
        """生成通知的唯一ID"""
        import hashlib
        content = f"{title}_{url}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()[:16]
        
    def get_full_url(self, href: str) -> str:
        """获取完整URL"""
        if href.startswith('http'):
            return href
        elif href.startswith('/'):
            return f"https://hrss.qingdao.gov.cn{href}"
        else:
            return f"https://hrss.qingdao.gov.cn/ztzl_47/zcpd_47/tzgg_47/{href}"
            
    def load_existing_data(self) -> Dict:
        """加载已存在的数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"加载数据文件失败: {e}")
        
        # 返回默认结构
        return {
            "announcements": [],
            "last_check": "",
            "total_count": 0
        }
        
    def save_data(self, data: Dict):
        """保存数据到文件"""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.logger.info(f"数据已保存到: {self.data_file}")
        except Exception as e:
            self.logger.error(f"保存数据失败: {e}")
            
    def detect_new_announcements(self, current_announcements: List[Dict], existing_data: Dict) -> List[Dict]:
        """检测新通知"""
        existing_ids = {ann['id'] for ann in existing_data.get('announcements', [])}
        new_announcements = []
        
        for announcement in current_announcements:
            if announcement['id'] not in existing_ids:
                new_announcements.append(announcement)
                
        return new_announcements
        
    def notify_new_announcements(self, new_announcements: List[Dict]):
        """通知新的公告。
        
        Args:
            new_announcements: 新通知公告列表
        """
        if not new_announcements:
            self.logger.info("没有发现新的通知公告")
            return
            
        self.logger.info(f"🔔 发现 {len(new_announcements)} 条新通知:")
        for announcement in new_announcements:
            self.logger.info(f"- {announcement['title']}")
            self.logger.info(f"  链接: {announcement['url']}")
            
        # 发送推送通知
        try:
            if self.notifier.send_notification(new_announcements):
                self.logger.info("📱 推送通知发送成功")
            else:
                self.logger.warning("⚠️ 推送通知发送失败，请检查通知配置")
        except Exception as e:
            self.logger.error(f"❌ 推送通知出错: {e}")
        
    def run_once(self):
        """执行一次爬取任务"""
        self.logger.info("开始执行爬取任务...")
        
        # 获取网页内容
        html_content = self.fetch_page_content()
        if not html_content:
            self.logger.error("无法获取网页内容，跳过本次检查")
            return
            
        # 解析通知公告
        current_announcements = self.parse_announcements(html_content)
        if not current_announcements:
            self.logger.warning("未解析到任何通知公告")
            
        # 加载现有数据
        existing_data = self.load_existing_data()
        
        # 检测新通知
        new_announcements = self.detect_new_announcements(current_announcements, existing_data)
        
        # 通知新公告
        self.notify_new_announcements(new_announcements)
        
        # 更新数据
        all_announcements = existing_data.get('announcements', [])
        
        # 添加新通知
        for new_ann in new_announcements:
            all_announcements.append(new_ann)
            
        # 限制存储数量
        max_count = SCRAPE_CONFIG["max_announcements"]
        if len(all_announcements) > max_count:
            all_announcements = all_announcements[-max_count:]
            
        # 保存更新后的数据
        updated_data = {
            "announcements": all_announcements,
            "last_check": datetime.now().strftime(SCRAPE_CONFIG["date_format"]),
            "total_count": len(all_announcements)
        }
        self.save_data(updated_data)
        
        self.logger.info("爬取任务完成")
        
    def run_daemon(self):
        """以守护进程模式运行。
        
        长期运行监控程序，定期检查新通知并推送消息。
        """
        self.logger.info("🚀 启动守护进程模式...")
        self.logger.info(f"⏰ 检查间隔: {SCRAPE_CONFIG['check_interval']} 秒 ({SCRAPE_CONFIG['check_interval']//60} 分钟)")
        self.logger.info("� Windows系统通知: 已启用")
        self.logger.info("💡 按 Ctrl+C 停止监控")
        
        # 发送启动通知
        try:
            self.notifier.send_windows_notification(
                "青岛人社局通知监控", 
                "监控系统已启动，将定期检查新通知"
            )
        except Exception:
            pass  # 忽略通知失败
        
        error_count = 0
        max_errors = 5  # 最大连续错误次数
        
        while True:
            try:
                self.run_once()
                error_count = 0  # 重置错误计数
                
                # 等待下一次检查
                self.logger.info(f"😴 等待 {SCRAPE_CONFIG['check_interval']} 秒后进行下次检查...")
                time.sleep(SCRAPE_CONFIG["check_interval"])
                
            except KeyboardInterrupt:
                self.logger.info("👋 收到停止信号，正在优雅退出...")
                # 发送停止通知
                try:
                    self.notifier.send_windows_notification(
                        "青岛人社局通知监控", 
                        "监控系统已停止"
                    )
                except Exception:
                    pass
                break
            except requests.exceptions.RequestException as e:
                error_count += 1
                self.logger.error(f"🌐 网络请求错误 ({error_count}/{max_errors}): {e}")
                
                if error_count >= max_errors:
                    self.logger.error("❌ 连续网络错误过多，程序退出")
                    break
                    
                # 网络错误时等待更长时间
                time.sleep(min(300, 60 * error_count))  # 最多等待5分钟
                
            except Exception as e:
                error_count += 1
                self.logger.error(f"⚠️ 运行时错误 ({error_count}/{max_errors}): {e}")
                
                if error_count >= max_errors:
                    self.logger.error("❌ 连续错误过多，程序退出")
                    break
                    
                time.sleep(60)  # 其他错误等待1分钟


def main():
    """主函数"""
    import argparse
    
    # 先运行开机自检（静默模式）
    print("🔧 正在进行系统自检...")
    try:
        from startup_check import run_startup_check
        if not run_startup_check(silent=True):
            print("❌ 系统自检失败，程序退出")
            print("💡 运行 'python startup_check.py' 查看详细信息")
            return
    except Exception as e:
        print(f"❌ 自检过程出错: {e}")
        return
    
    print("✅ 系统自检通过，启动爬虫程序...")
    print("-" * 50)
    
    parser = argparse.ArgumentParser(description='通知公告爬虫')
    parser.add_argument('--daemon', action='store_true', help='以守护进程模式运行')
    parser.add_argument('--once', action='store_true', help='只执行一次爬取')
    
    args = parser.parse_args()
    
    scraper = QingdaoHRSScraper()
    
    if args.daemon:
        scraper.run_daemon()
    else:
        scraper.run_once()


if __name__ == "__main__":
    main()