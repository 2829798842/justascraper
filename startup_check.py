#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块名称：startup_check
主要功能：开机自检和系统检查

@Time: 2025-08-05 09:35:00
@Author: Yang208115
@File: startup_check.py
@Desc: 开机自检，检查运行环境和依赖
"""

import sys
import os
import platform
import subprocess
import logging
from pathlib import Path

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def check_python_version(logger, silent=False):
    """检查Python版本"""
    if not silent:
        logger.info("🐍 检查Python版本...")
    version = sys.version_info
    if not silent:
        logger.info(f"   Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        logger.error("❌ Python版本过低，需要Python 3.8及以上版本")
        return False
    
    if not silent:
        logger.info("✅ Python版本检查通过")
    return True

def check_platform(logger, silent=False):
    """检查操作系统"""
    if not silent:
        logger.info("💻 检查操作系统...")
    system = platform.system()
    if not silent:
        logger.info(f"   操作系统: {system} {platform.release()}")
    
    if system != "Windows":
        if not silent:
            logger.warning("⚠️ 当前系统不是Windows，系统通知功能可能不可用")
    else:
        if not silent:
            logger.info("✅ Windows系统检查通过")
    
    return True

def check_dependencies(logger, silent=False):
    """检查依赖包"""
    if not silent:
        logger.info("📦 检查依赖包...")
    
    required_packages = [
        ("requests", "requests"),
        ("beautifulsoup4", "bs4"), 
        ("lxml", "lxml"),
        ("plyer", "plyer")
    ]
    
    missing_packages = []
    
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            if not silent:
                logger.info(f"   ✅ {package_name}")
        except ImportError:
            logger.warning(f"   ❌ {package_name} - 缺失")
            missing_packages.append(package_name)
    
    if missing_packages:
        logger.error(f"❌ 缺少依赖包: {', '.join(missing_packages)}")
        logger.info("💡 请运行以下命令安装依赖:")
        logger.info("   uv pip install " + " ".join(missing_packages))
        return False
    
    if not silent:
        logger.info("✅ 所有依赖包检查通过")
    return True

def check_directories(logger, silent=False):
    """检查目录结构"""
    if not silent:
        logger.info("📁 检查目录结构...")
    
    required_dirs = ["data", "logs", "utils"]
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            if not silent:
                logger.info(f"   📁 创建目录: {dir_name}")
            dir_path.mkdir(exist_ok=True)
        else:
            if not silent:
                logger.info(f"   ✅ {dir_name}")
    
    if not silent:
        logger.info("✅ 目录结构检查通过")
    return True

def check_config_files(logger, silent=False):
    """检查配置文件"""
    if not silent:
        logger.info("⚙️ 检查配置文件...")
    
    config_files = ["config.py", "scraper.py", "utils/notifier.py", "utils/__init__.py"]
    
    for file_name in config_files:
        file_path = Path(file_name)
        if not file_path.exists():
            logger.error(f"   ❌ {file_name} - 文件不存在")
            return False
        else:
            if not silent:
                logger.info(f"   ✅ {file_name}")
    
    if not silent:
        logger.info("✅ 配置文件检查通过")
    return True

def check_network_connectivity(logger, silent=False):
    """检查网络连接"""
    if not silent:
        logger.info("🌐 检查网络连接...")
    
    try:
        import requests
        response = requests.get("https://hrss.qingdao.gov.cn", timeout=10)
        if response.status_code == 200:
            if not silent:
                logger.info("✅ 目标网站连接正常")
            return True
        else:
            logger.warning(f"⚠️ 目标网站返回状态码: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ 网络连接失败: {e}")
        return False

def test_notification(logger, silent=False):
    """测试通知功能"""
    if not silent:
        logger.info("📢 测试通知功能...")
    
    try:
        from utils.notifier import MessageNotifier
        notifier = MessageNotifier()
        
        # 测试Windows通知
        success = notifier.send_windows_notification(
            "青岛人社局通知监控", 
            "系统自检完成，通知功能正常"
        )
        
        if success:
            if not silent:
                logger.info("✅ 系统通知测试成功")
        else:
            if not silent:
                logger.warning("⚠️ 系统通知测试失败，但不影响主要功能")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 通知功能测试失败: {e}")
        return False

def run_startup_check(silent=False):
    """运行完整的开机自检
    
    Args:
        silent: 是否静默模式（减少输出）
    """
    logger = setup_logging()
    
    if not silent:
        logger.info("🚀 青岛人社局通知监控系统 - 开机自检")
        logger.info("=" * 50)
    
    checks = [
        ("Python版本", lambda logger: check_python_version(logger, silent)),
        ("操作系统", lambda logger: check_platform(logger, silent)),
        ("依赖包", lambda logger: check_dependencies(logger, silent)),
        ("目录结构", lambda logger: check_directories(logger, silent)),
        ("配置文件", lambda logger: check_config_files(logger, silent)),
        ("网络连接", lambda logger: check_network_connectivity(logger, silent)),
        ("通知功能", lambda logger: test_notification(logger, silent))
    ]
    
    failed_checks = []
    
    for check_name, check_func in checks:
        try:
            if not check_func(logger):
                failed_checks.append(check_name)
        except Exception as e:
            logger.error(f"❌ {check_name}检查出错: {e}")
            failed_checks.append(check_name)
    
    if not silent:
        logger.info("=" * 50)
    
    if failed_checks:
        logger.error(f"❌ 自检失败，问题项目: {', '.join(failed_checks)}")
        logger.info("💡 请解决上述问题后再运行程序")
        return False
    else:
        if not silent:
            logger.info("🎉 所有检查项目通过，系统准备就绪！")
            logger.info("💡 可以运行以下命令启动监控:")
            logger.info("   python scraper.py --daemon")
        else:
            logger.info("✅ 系统自检通过")
        return True

if __name__ == "__main__":
    success = run_startup_check()
    sys.exit(0 if success else 1)
