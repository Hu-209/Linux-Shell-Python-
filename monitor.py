import psutil
import json
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.header import Header
import paramiko
import os

# 加载配置文件
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

# 获取单服务器系统信息
def get_system_info():
    cpu_usage = psutil.cpu_percent(interval=1)
    cpu_core = psutil.cpu_count(logical=True)
    mem = psutil.virtual_memory()
    mem_usage = mem.percent
    mem_total = round(mem.total / 1024 / 1024 / 1024, 2)
    mem_used = round(mem.used / 1024 / 1024 / 1024, 2)
    disk = psutil.disk_usage('/')
    disk_usage = disk.percent
    disk_total = round(disk.total / 1024 / 1024 / 1024, 2)
    disk_used = round(disk.used / 1024 / 1024 / 1024, 2)
    net = psutil.net_io_counters()
    net_send = round(net.bytes_sent / 1024 / 1024, 2)
    net_recv = round(net.bytes_recv / 1024 / 1024, 2)

    top_processes = []
    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            proc_info = proc.info
            if proc_info["cpu_percent"] > 0 or proc_info["memory_percent"] > 0:
                top_processes.append(proc_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    top_processes.sort(key=lambda x: x["cpu_percent"], reverse=True)[:5]

    return {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "hostname": os.uname().nodename,
        "cpu": {"core": cpu_core, "usage": cpu_usage},
        "memory": {"total_gb": mem_total, "used_gb": mem_used, "usage": mem_usage},
        "disk": {"total_gb": disk_total, "used_gb": disk_used, "usage": disk_usage},
        "network": {"send_mb": net_send, "recv_mb": net_recv},
        "top_processes": top_processes
    }

# 发送邮件告警
def send_alert_email(info, config):
    email_conf = config["email"]
    threshold = config["threshold"]
    alert_content = f"""
    <h3>Linux 服务器告警通知</h3>
    <p>告警时间：{info['time']}</p>
    <p>服务器：{info['hostname']}</p>
    <p>============ 异常指标 ============</p>
    """
    if info["cpu"]["usage"] > threshold["cpu_usage"]:
        alert_content += f"<p>CPU 使用率：{info['cpu']['usage']}%（阈值：{threshold['cpu_usage']}%）</p>"
    if info["memory"]["usage"] > threshold["mem_usage"]:
        alert_content += f"<p>内存使用率：{info['memory']['usage']}%（阈值：{threshold['mem_usage']}%）</p>"
    if info["disk"]["usage"] > threshold["disk_usage"]:
        alert_content += f"<p>磁盘使用率：{info['disk']['usage']}%（阈值：{threshold['disk_usage']}%）</p>"
    alert_content += "<p>============ TOP5 进程 ============</p>"
    for proc in info["top_processes"]:
        alert_content += f"<p>PID：{proc['pid']} | 名称：{proc['name']} | CPU：{proc['cpu_percent']}% | 内存：{proc['memory_percent']}%</p>"

    msg = MIMEText(alert_content, "html", "utf-8")
    msg["From"] = Header("Linux 监控脚本", "utf-8")
    msg["To"] = Header(email_conf["receiver"], "utf-8")
    msg["Subject"] = Header(f"【告警】{info['hostname']} 服务器指标异常", "utf-8")

    try:
        server = smtplib.SMTP(email_conf["smtp_server"], email_conf["smtp_port"])
        server.starttls()
        server.login(email_conf["sender"], email_conf["password"])
        server.sendmail(email_conf["sender"], email_conf["receiver"], msg.as_string())
        server.quit()
        print(f"✅ 告警邮件已发送至 {email_conf['receiver']}")
    except Exception as e:
        print(f"❌ 邮件发送失败：{str(e)}")

# 检查阈值
def check_threshold(info, config):
    threshold = config["threshold"]
    return (info["cpu"]["usage"] > threshold["cpu_usage"] or
            info["memory"]["usage"] > threshold["mem_usage"] or
            info["disk"]["usage"] > threshold["disk_usage"])

# 格式化输出
def print_report(info, output_format="json"):
    if output_format == "json":
        print(json.dumps(info, indent=2, ensure_ascii=False))
    else:
        print("="*60)
        print(f"������ 监控时间：{info['time']}")
        print(f"������️  服务器：{info['hostname']}")
        print("="*60)
        print(f"CPU 信息：{info['cpu']['core']} 核 | 使用率：{info['cpu']['usage']}%")
        print(f"内存信息：总 {info['memory']['total_gb']}GB | 已用 {info['memory']['used_gb']}GB | 使用率：{info['memory']['usage']}%")
        print(f"磁盘信息：总 {info['disk']['total_gb']}GB | 已用 {info['disk']['used_gb']}GB | 使用率：{info['disk']['usage']}%")
        print(f"网络信息：发送 {info['network']['send_mb']}MB | 接收 {info['network']['recv_mb']}MB")
        print("="*60)
        print("TOP5 进程（按 CPU 排序）：")
        for i, proc in enumerate(info["top_processes"], 1):
            print(f"{i}. PID：{proc['pid']} | 名称：{proc['name']} | CPU：{proc['cpu_percent']}% | 内存：{proc['memory_percent']}%")
        print("="*60)

# 批量监控多服务器
def batch_monitor(config):
    servers = config["servers"]
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    for server in servers:
        print(f"\n������ 正在监控服务器：{server['hostname']}（{server['ip']}）")
        try:
            ssh_client.connect(hostname=server["ip"], username=server["username"], timeout=10)
            script_path = os.path.join(os.path.dirname(__file__), "monitor.py")
            sftp = ssh_client.open_sftp()
            sftp.put(script_path, "/tmp/monitor.py")
            sftp.close()
            stdin, stdout, stderr = ssh_client.exec_command(f"python3 /tmp/monitor.py --format text")
            print(stdout.read().decode("utf-8"))
            stderr_output = stderr.read().decode("utf-8")
            if stderr_output:
                print(f"❌ 远程执行错误：{stderr_output}")
            ssh_client.close()
        except Exception as e:
            print(f"❌ 连接服务器 {server['ip']} 失败：{str(e)}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Linux 系统信息监控脚本")
    parser.add_argument("--format", choices=["json", "text"], default="json", help="输出格式（json/text）")
    parser.add_argument("--batch", action="store_true", help="批量监控多服务器")
    parser.add_argument("--alert", action="store_true", help="开启告警")
    args = parser.parse_args()

    config = load_config()
    if args.batch:
        batch_monitor(config)
    else:
        system_info = get_system_info()
        print_report(system_info, args.format)
        if args.alert and check_threshold(system_info, config):
            send_alert_email(system_info, config)
