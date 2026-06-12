#!/usr/bin/env python3
import os,time,select,termios,sys

COMMANDS = """
AT+CPIN?
AT+CGDCONT?
AT+COPS?
AT+CPSI?
AT+CGREG?
AT+CSQ
AT+CNMP?
AT+CFUN?
AT+SIMCOMATI
AT+CUSBPIDSWITCH?
"""

baud=termios.B115200

def op(p):
    fd=os.open(p,os.O_RDWR|os.O_NOCTTY|os.O_NONBLOCK)
    old=termios.tcgetattr(fd); a=old[:]
    a[0]=a[1]=a[3]=0
    a[2]=baud|termios.CS8|termios.CREAD|termios.CLOCAL
    a[4]=a[5]=baud
    a[6][termios.VMIN]=a[6][termios.VTIME]=0
    termios.tcsetattr(fd,termios.TCSANOW,a)
    termios.tcflush(fd,termios.TCIOFLUSH)
    return fd,old

def rd(fd,t=2):
    end=time.time()+t; r=b""
    while time.time()<end:
        a,_,_=select.select([fd],[],[],.2)
        if a:
            d=os.read(fd,4096)
            if d:
                r+=d
                print(d.decode(errors="replace"),end="")
                if b"OK" in r or b"ERROR" in r: break
    return r

def wr(fd,c):
    print(">>>",c)
    os.write(fd,(c+"\r\n").encode())
    if not rd(fd): print("超时")
    print("---")

for n in "234":
    p="/dev/ttyUSB"+n
    if not os.path.exists(p): continue
    try:
        fd,old=op(p)
        os.write(fd,b"AT\r\n")
        if b"OK" in rd(fd,2): break
        termios.tcsetattr(fd,termios.TCSANOW,old); os.close(fd)
    except: pass
else:
    print("ttyUSB2 3 4 都无响应"); sys.exit(1)

print("使用",p)

try:
    for c in COMMANDS.strip().splitlines():
        wr(fd,c.strip())
finally:
    termios.tcsetattr(fd,termios.TCSANOW,old)
    os.close(fd)