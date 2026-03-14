# -*- coding: utf-8 -*-
"""
天气监控与邮件告警系统 (Weather Monitor & Email Alert System)
功能: 定时获取天气数据，当温度低于阈值时自动发送邮件提醒
作者: 智能脚本架构师
版本: 1.0
"""

import os
import time
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from datetime import datetime

import requests
import schedule

# ============================================================================
# 日志配置
# ============================================================================
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_FILE = 'weather_monitor.log'

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# 配置管理 - 从环境变量读取敏感信息
# ============================================================================
"""
【重要】使用前请设置以下环境变量：

Windows PowerShell:
    $env:WEATHER_API_KEY="your_api_key"
    $env:WEATHER_CITY="Beijing"
    $env:TEMP_THRESHOLD="5"
    $env:SMTP_SERVER="smtp.qq.com"
    $env:SMTP_PORT="587"
    $env:SMTP_USER="your_email@qq.com"
    $env:SMTP_PASSWORD="your_authorization_code"
    $env:ALERT_RECIPIENT="recipient@example.com"

Linux/Mac:
    export WEATHER_API_KEY="your_api_key"
    export WEATHER_CITY="Beijing"
    export TEMP_THRESHOLD="5"
    export SMTP_SERVER="smtp.qq.com"
    export SMTP_PORT="587"
    export SMTP_USER="your_email@qq.com"
    export SMTP_PASSWORD="your_authorization_code"
    export ALERT_RECIPIENT="recipient@example.com"

API密钥获取:
    - 和风天气: https://dev.qweather.com/
    - OpenWeatherMap: https://openweathermap.org/api
"""


def get_config() -> Dict[str, Any]:
    """
    从环境变量获取配置信息
    
    返回:
        Dict[str, Any]: 包含所有配置项的字典
        
    异常:
        ValueError: 当必需的环境变量未设置时抛出
    """
    required_vars = [
        'WEATHER_API_KEY',
        'WEATHER_CITY',
        'TEMP_THRESHOLD',
        'SMTP_SERVER',
        'SMTP_PORT',
        'SMTP_USER',
        'SMTP_PASSWORD',
        'ALERT_RECIPIENT'
    ]
    
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    if missing_vars:
        error_msg = f"缺少必需的环境变量: {', '.join(missing_vars)}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    config = {
        'api_key': os.environ.get('WEATHER_API_KEY'),
        'city': os.environ.get('WEATHER_CITY'),
        'temp_threshold': float(os.environ.get('TEMP_THRESHOLD', '5')),
        'smtp_server': os.environ.get('SMTP_SERVER'),
        'smtp_port': int(os.environ.get('SMTP_PORT', '587')),
        'smtp_user': os.environ.get('SMTP_USER'),
        'smtp_password': os.environ.get('SMTP_PASSWORD'),
        'alert_recipient': os.environ.get('ALERT_RECIPIENT')
    }
    
    logger.info("配置加载成功")
    return config


# ============================================================================
# 天气数据获取
# ============================================================================
def fetch_weather(api_key: str, city: str) -> Optional[Dict[str, Any]]:
    """
    从和风天气API获取天气数据
    
    参数:
        api_key: 和风天气API密钥
        city: 城市名称或城市ID
        
    返回:
        Optional[Dict[str, Any]]: 天气数据字典，包含温度、天气状况等；
                                  请求失败时返回None
    """
    url = "https://devapi.qweather.com/v7/weather/now"
    params = {
        'location': city,
        'key': api_key
    }
    
    try:
        logger.info(f"正在获取 {city} 的天气数据...")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('code') != '200':
            logger.error(f"API返回错误: {data.get('message', '未知错误')}")
            return None
        
        now = data.get('now', {})
        weather_info = {
            'temp': float(now.get('temp', 0)),
            'feels_like': float(now.get('feelsLike', 0)),
            'text': now.get('text', '未知'),
            'humidity': now.get('humidity', '未知'),
            'wind_dir': now.get('windDir', '未知'),
            'wind_scale': now.get('windScale', '未知'),
            'update_time': data.get('updateTime', datetime.now().isoformat())
        }
        
        logger.info(f"天气数据获取成功: 温度 {weather_info['temp']}°C, {weather_info['text']}")
        return weather_info
        
    except requests.exceptions.Timeout:
        logger.error("请求超时，请检查网络连接")
        return None
    except requests.exceptions.ConnectionError:
        logger.error("网络连接失败，请检查网络设置")
        return None
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP错误: {e}")
        return None
    except (KeyError, ValueError, TypeError) as e:
        logger.error(f"数据解析错误: {e}")
        return None
    except Exception as e:
        logger.error(f"获取天气数据时发生未知错误: {e}")
        return None


# ============================================================================
# 邮件发送功能
# ============================================================================
def send_email_alert(weather_info: Dict[str, Any], config: Dict[str, Any]) -> bool:
    """
    发送低温预警邮件
    
    参数:
        weather_info: 天气信息字典
        config: 配置字典
        
    返回:
        bool: 发送成功返回True，失败返回False
    """
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = config['smtp_user']
        msg['To'] = config['alert_recipient']
        msg['Subject'] = f"【低温预警】{config['city']} 当前温度 {weather_info['temp']}°C"
        
        text_content = f"""
您好！

【低温预警通知】

城市: {config['city']}
当前温度: {weather_info['temp']}°C
体感温度: {weather_info['feels_like']}°C
天气状况: {weather_info['text']}
相对湿度: {weather_info['humidity']}%
风向风力: {weather_info['wind_dir']} {weather_info['wind_scale']}级
数据更新时间: {weather_info['update_time']}

当前温度已低于预设阈值 {config['temp_threshold']}°C，请注意保暖！

---
此邮件由天气监控系统自动发送
时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        html_content = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #ff6b6b; color: white; padding: 15px; border-radius: 5px; }}
        .content {{ background-color: #f9f9f9; padding: 20px; border-radius: 5px; margin-top: 10px; }}
        .info-row {{ margin: 10px 0; }}
        .label {{ font-weight: bold; color: #333; }}
        .footer {{ margin-top: 20px; padding-top: 10px; border-top: 1px solid #ddd; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>🌡️ 低温预警通知</h2>
        </div>
        <div class="content">
            <div class="info-row"><span class="label">城市:</span> {config['city']}</div>
            <div class="info-row"><span class="label">当前温度:</span> {weather_info['temp']}°C</div>
            <div class="info-row"><span class="label">体感温度:</span> {weather_info['feels_like']}°C</div>
            <div class="info-row"><span class="label">天气状况:</span> {weather_info['text']}</div>
            <div class="info-row"><span class="label">相对湿度:</span> {weather_info['humidity']}%</div>
            <div class="info-row"><span class="label">风向风力:</span> {weather_info['wind_dir']} {weather_info['wind_scale']}级</div>
            <div class="info-row"><span class="label">数据更新时间:</span> {weather_info['update_time']}</div>
            <hr>
            <p style="color: #ff6b6b; font-weight: bold;">
                ⚠️ 当前温度已低于预设阈值 {config['temp_threshold']}°C，请注意保暖！
            </p>
        </div>
        <div class="footer">
            此邮件由天气监控系统自动发送<br>
            时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
"""
        
        part1 = MIMEText(text_content, 'plain', 'utf-8')
        part2 = MIMEText(html_content, 'html', 'utf-8')
        
        msg.attach(part1)
        msg.attach(part2)
        
        logger.info(f"正在连接邮件服务器 {config['smtp_server']}...")
        
        with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
            server.starttls()
            server.login(config['smtp_user'], config['smtp_password'])
            server.sendmail(
                config['smtp_user'],
                config['alert_recipient'],
                msg.as_string()
            )
        
        logger.info(f"预警邮件发送成功 -> {config['alert_recipient']}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP认证失败，请检查邮箱地址和授权码")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP错误: {e}")
        return False
    except Exception as e:
        logger.error(f"发送邮件时发生未知错误: {e}")
        return False


# ============================================================================
# 主逻辑函数
# ============================================================================
def check_weather_and_alert() -> None:
    """
    主检查函数：获取天气数据、判断阈值、触发告警
    """
    logger.info("=" * 50)
    logger.info("开始执行天气检查任务")
    
    try:
        config = get_config()
    except ValueError:
        logger.error("配置加载失败，跳过本次检查")
        return
    
    weather_info = fetch_weather(config['api_key'], config['city'])
    
    if weather_info is None:
        logger.warning("无法获取天气数据，跳过本次检查")
        return
    
    current_temp = weather_info['temp']
    threshold = config['temp_threshold']
    
    logger.info(f"当前温度: {current_temp}°C, 阈值: {threshold}°C")
    
    if current_temp < threshold:
        logger.warning(f"温度 {current_temp}°C 低于阈值 {threshold}°C，触发告警！")
        send_email_alert(weather_info, config)
    else:
        logger.info(f"温度正常，无需告警")
    
    logger.info("天气检查任务完成")
    logger.info("=" * 50)


# ============================================================================
# 程序入口
# ============================================================================
def main() -> None:
    """
    主函数：初始化配置并启动定时任务调度
    """
    logger.info("=" * 60)
    logger.info("天气监控与邮件告警系统启动")
    logger.info("=" * 60)
    
    try:
        config = get_config()
        logger.info(f"监控城市: {config['city']}")
        logger.info(f"温度阈值: {config['temp_threshold']}°C")
        logger.info(f"告警接收邮箱: {config['alert_recipient']}")
    except ValueError:
        logger.error("配置初始化失败，程序退出")
        return
    
    schedule.every().hour.do(check_weather_and_alert)
    
    logger.info("定时任务已设置: 每小时检查一次天气")
    logger.info("按 Ctrl+C 停止程序")
    
    check_weather_and_alert()
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except KeyboardInterrupt:
            logger.info("收到停止信号，程序退出")
            break
        except Exception as e:
            logger.error(f"主循环发生错误: {e}")
            time.sleep(60)


if __name__ == "__main__":
    main()
