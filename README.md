# Linux 系统信息监控脚本

![Python Version](https://img.shields.io/badge/Python-3.7%2B-blue)
![Shell Version](https://img.shields.io/badge/Shell-Bash-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

一款轻量级 Linux 服务器监控工具，支持 **单服务器实时监控**、**多服务器批量监控**、**阈值告警**、**多格式输出**，解决运维日常手动查机器状态的痛点。

## ������ 核心功能

### 1. 全面的指标采集
- **CPU**：核心数、使用率、TOP5 占用进程
- **内存**：总内存、已用内存、使用率
- **磁盘**：根目录总容量、已用容量、使用率
- **网络**：实时收发流量（MB/KB）
- **进程**：按 CPU 排序的 TOP5 进程（PID、名称、资源占用）

### 2. 灵活的输出格式
- ������ JSON 格式：便于程序解析（默认）
- ������ 文本格式：直观阅读，适合人工查看

### 3. 实用的扩展功能
- ⏱️ 定时执行：通过 crontab 实现周期性监控
- ������ 邮件告警：指标超过阈值自动发送告警邮件
- ������ 批量监控：基于 SSH 免密登录，支持多服务器统一监控

### 4. 双版本支持
- **Python 进阶版**：功能完整（批量监控、邮件告警），依赖 psutil 库
- **Shell 基础版**：轻量无依赖，适合极简环境

## ������️ 技术栈
- 核心语言：Python 3.7+ / Shell（Bash）
- Python 依赖：psutil（系统指标采集）、paramiko（SSH 批量执行）、smtplib（邮件发送）
- 自动化工具：crontab（定时任务）、SSH（免密登录）
- 其他：JSON（配置文件）、HTML（邮件内容）

## ������ 安装步骤

### 1. 环境准备
#### （1）基础依赖安装
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install -y python3 python3-pip ifstat ssh

# CentOS/RHEL
sudo yum install -y python3 python3-pip ifstat openssh-clients
