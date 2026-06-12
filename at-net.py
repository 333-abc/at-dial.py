#!/usr/bin/env python3
import os,termios,time,select,sys

PORTS=["/dev/ttyUSB2","/dev/ttyUSB3","/dev/ttyUSB4"]
BAUD=termios.B115200

COMMANDS = """
AT
ATE1
AT+CSQ
AT+CUSBCFG=USBID,1E0E,9001
AT+CUSBCFG=USBID,1E0E,9011
AT+CUSBCFG=USBID,1E0E,9018
AT+QCFG="usbnet",0
AT+QCFG="usbnet",1
AT+QCFG="usbnet",2
AT+QCFG="usbnet",3
AT+GTUSBMODE=38
AT+CFUN=1,1
"""
# =======================

def openp(p):
    fd=os.open(p,os.O_RDWR|os.O_NOCTTY|os.O_NONBLOCK)
    old=termios.tcgetattr(fd)
    a=termios.tcgetattr(fd)
    a[0]=a[1]=a[3]=0
    a[2]=BAUD|termios.CS8|termios.CREAD|termios.CLOCAL
    a[4]=a[5]=BAUD
    a[6][termios.VMIN]=0
    a[6][termios.VTIME]=0
    termios.tcsetattr(fd,termios.TCSANOW,a)
    termios.tcflush(fd,termios.TCIOFLUSH)
    return fd,old

def wr(fd,s):
    os.write(fd,(s+"\r\n").encode())

def rd(fd,t=1.8,show=1):
    end=time.time()+t
    r=b""
    while time.time()<end:
        a,_,_=select.select([fd],[],[],0.2)
        if a:
            d=os.read(fd,4096)
            if d:
                r+=d
                if show: print(d.decode(errors="replace"),end="")
                end=time.time()+0.3
    return r

def closep(fd,old):
    termios.tcsetattr(fd,termios.TCSANOW,old)
    os.close(fd)

fd=old=None
PORT=None

for p in PORTS:
    if not os.path.exists(p): continue
    try:
        fd,old=openp(p)
        wr(fd,"AT")
        if "OK" in rd(fd,2,0).decode(errors="ignore"):
            PORT=p
            break
        closep(fd,old)
        fd=old=None
    except:
        pass

if not PORT:
    print("ttyUSB2 ttyUSB3 ttyUSB4 都无响应")
    sys.exit(1)

cmds=[]
for x in COMMANDS.splitlines():
    x=x.strip()
    if x and not x.startswith("#"):
        cmds.append(x)

print("使用",PORT,"115200")
print("选择编号发送  a 全部发送  m 手动输入  q 退出")

try:
    while True:
        print("\n指令列表")
        for i,c in enumerate(cmds,1):
            print(f"{i}. {c}")

        s=input("\n选择: ").strip().lower()

        if s in ("q","quit","exit"):
            break

        if s=="m":
            s=input("AT> ").strip()
            todo=[x.strip() for x in s.replace(";","\n").splitlines() if x.strip()]
        elif s=="a":
            todo=cmds
        else:
            try:
                todo=[cmds[int(s)-1]]
            except:
                print("选择无效")
                continue

        for c in todo:
            print("\n>>>",c)
            wr(fd,c)
            if not rd(fd,2,1):
                print("超时")
            print("---")
            time.sleep(1)

finally:
    if fd:
        closep(fd,old)
        print("\n串口已关闭")