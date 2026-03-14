# 天气监控与邮件告警系统

生产级Python自动化脚本，定时获取天气数据并在温度低于阈值时自动发送邮件提醒。

## 项目结构

```
weather_monitor/
├── weather_monitor.py    # 主程序脚本
├── requirements.txt      # Python依赖
├── .env.example          # 环境变量配置示例
├── README.md             # 说明文档
└── weather_monitor.log   # 运行日志（运行后自动生成）
```

---

## 第一部分：安装依赖

### 1. 创建虚拟环境（推荐）

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

**Windows PowerShell:**
```powershell
$env:WEATHER_API_KEY="your_api_key"
$env:WEATHER_CITY="Beijing"
$env:TEMP_THRESHOLD="5"
$env:SMTP_SERVER="smtp.qq.com"
$env:SMTP_PORT="587"
$env:SMTP_USER="your_email@qq.com"
$env:SMTP_PASSWORD="your_authorization_code"
$env:ALERT_RECIPIENT="recipient@example.com"
```

**Linux/Mac:**
```bash
export WEATHER_API_KEY="your_api_key"
export WEATHER_CITY="Beijing"
export TEMP_THRESHOLD="5"
export SMTP_SERVER="smtp.qq.com"
export SMTP_PORT="587"
export SMTP_USER="your_email@qq.com"
export SMTP_PASSWORD="your_authorization_code"
export ALERT_RECIPIENT="recipient@example.com"
```

### 4. 运行程序

```bash
python weather_monitor.py
```

---

## 第二部分：后台运行建议

### Windows 系统

#### 方案一：使用 nohup（需安装Git Bash或Cygwin）

```bash
nohup python weather_monitor.py > output.log 2>&1 &
```

#### 方案二：使用 Windows 任务计划程序

1. 打开 **任务计划程序**（搜索 "Task Scheduler"）
2. 点击 **创建基本任务**
3. 配置如下：
   - **名称**: WeatherMonitor
   - **触发器**: 计算机启动时
   - **操作**: 启动程序
   - **程序**: `python.exe` 完整路径
   - **参数**: `weather_monitor.py` 完整路径
   - **起始于**: 脚本所在目录

4. 完成后，右键任务 → **属性** → 勾选 **不管用户是否登录都要运行**

#### 方案三：使用 NSSM 安装为Windows服务

```powershell
# 下载 NSSM: https://nssm.cc/download
nssm install WeatherMonitor "C:\Python\python.exe" "C:\path\to\weather_monitor.py"
nssm start WeatherMonitor
```

---

### Linux 系统

#### 方案一：使用 nohup

```bash
nohup python3 weather_monitor.py > output.log 2>&1 &

# 查看进程
ps aux | grep weather_monitor

# 停止进程
kill <PID>
```

#### 方案二：使用 systemd 服务（推荐）

1. 创建服务文件：

```bash
sudo nano /etc/systemd/system/weather-monitor.service
```

2. 写入以下内容：

```ini
[Unit]
Description=Weather Monitor Service
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/weather_monitor
Environment="WEATHER_API_KEY=your_api_key"
Environment="WEATHER_CITY=Beijing"
Environment="TEMP_THRESHOLD=5"
Environment="SMTP_SERVER=smtp.qq.com"
Environment="SMTP_PORT=587"
Environment="SMTP_USER=your_email@qq.com"
Environment="SMTP_PASSWORD=your_authorization_code"
Environment="ALERT_RECIPIENT=recipient@example.com"
ExecStart=/usr/bin/python3 /path/to/weather_monitor/weather_monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. 启用并启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable weather-monitor
sudo systemctl start weather-monitor

# 查看状态
sudo systemctl status weather-monitor

# 查看日志
sudo journalctl -u weather-monitor -f
```

#### 方案三：使用 crontab

```bash
# 编辑定时任务
crontab -e

# 添加以下行（每小时执行一次）
0 * * * * cd /path/to/weather_monitor && /usr/bin/python3 weather_monitor.py >> /var/log/weather_monitor.log 2>&1
```

---

## API密钥获取

### 和风天气（推荐，国内访问稳定）

1. 访问 https://dev.qweather.com/
2. 注册账号并登录
3. 创建应用，选择 **Web API**
4. 复制 **KEY** 即为 `WEATHER_API_KEY`

### OpenWeatherMap（备选）

1. 访问 https://openweathermap.org/api
2. 注册账号
3. 在 API Keys 页面获取密钥

---

## 邮箱授权码获取（QQ邮箱示例）

1. 登录 QQ邮箱 网页版
2. 点击 **设置** → **账户**
3. 找到 **POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务**
4. 开启 **POP3/SMTP服务**
5. 点击 **生成授权码**，按提示发送短信
6. 获得的16位授权码即为 `SMTP_PASSWORD`

---

## 日志查看

程序运行后会生成 `weather_monitor.log` 日志文件：

```bash
# 实时查看日志
tail -f weather_monitor.log

# Windows PowerShell
Get-Content weather_monitor.log -Wait
```

---

## 故障排查

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 配置加载失败 | 环境变量未设置 | 检查所有必需变量是否正确设置 |
| API返回错误 | API密钥无效或过期 | 重新获取API密钥 |
| SMTP认证失败 | 授权码错误 | 确认使用授权码而非登录密码 |
| 网络连接失败 | 网络问题 | 检查网络连接和防火墙设置 |
