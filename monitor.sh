#!/bin/bash
CPU_THRESHOLD=80
MEM_THRESHOLD=85
DISK_THRESHOLD=90

TIME=$(date +"%Y-%m-%d %H:%M:%S")
HOSTNAME=$(hostname)
CPU_CORE=$(nproc)
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}' | cut -d. -f1)
MEM_TOTAL=$(free -g | grep Mem | awk '{print $2}')
MEM_USED=$(free -g | grep Mem | awk '{print $3}')
MEM_USAGE=$(free | grep Mem | awk '{print $3/$2 * 100.0}' | cut -d. -f1)
DISK_TOTAL=$(df -h / | grep / | awk '{print $2}' | sed 's/G//')
DISK_USED=$(df -h / | grep / | awk '{print $3}' | sed 's/G//')
DISK_USAGE=$(df -h / | grep / | awk '{print $5}' | sed 's/%//')
NET_SEND=$(ifstat -i eth0 1 1 | tail -n1 | awk '{print $6}' | sed 's/K//')
NET_RECV=$(ifstat -i eth0 1 1 | tail -n1 | awk '{print $8}' | sed 's/K//')
TOP_PROCESSES=$(ps -eo pid,ppid,pcpu,pmem,comm --sort=-pcpu | head -n6)

echo "=================================================="
echo "������ 监控时间：$TIME"
echo "������️  服务器：$HOSTNAME"
echo "=================================================="
echo "CPU 信息：$CPU_CORE 核 | 使用率：$CPU_USAGE%"
echo "内存信息：总 ${MEM_TOTAL}GB | 已用 ${MEM_USED}GB | 使用率：$MEM_USAGE%"
echo "磁盘信息：总 ${DISK_TOTAL}GB | 已用 ${DISK_USED}GB | 使用率：$DISK_USAGE%"
echo "网络信息：发送 ${NET_SEND}KB/s | 接收 ${NET_RECV}KB/s"
echo "=================================================="
echo "TOP5 进程（按 CPU 排序）："
echo "$TOP_PROCESSES"
echo "=================================================="

ALERT_LOG="/var/log/linux_monitor_alert.log"
alert_flag=0
alert_content="[$TIME] 服务器 $HOSTNAME 指标异常：\n"
if [ $CPU_USAGE -gt $CPU_THRESHOLD ]; then
    alert_content+="CPU 使用率 $CPU_USAGE%（阈值 $CPU_THRESHOLD%）\n"
    alert_flag=1
fi
if [ $MEM_USAGE -gt $MEM_THRESHOLD ]; then
    alert_content+="内存使用率 $MEM_USAGE%（阈值 $MEM_THRESHOLD%）\n"
    alert_flag=1
fi
if [ $DISK_USAGE -gt $DISK_THRESHOLD ]; then
    alert_content+="磁盘使用率 $DISK_USAGE%（阈值 $DISK_THRESHOLD%）\n"
    alert_flag=1
fi

if [ $alert_flag -eq 1 ]; then
    echo -e "$alert_content" >> $ALERT_LOG
    echo "⚠️  发现异常指标，已记录到告警日志：$ALERT_LOG"
fi
