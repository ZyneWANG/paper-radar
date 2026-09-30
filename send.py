# -*- coding: utf-8 -*-
"""
第 4 关 · 自动发信
用 SMTP 把 email.html 作为 HTML 邮件发到你的邮箱。
只用标准库（smtplib / email）。
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import settings


def smtp_host(email):
    domain = email.split('@')[-1].lower().strip()
    table = {
        'qq.com': 'smtp.qq.com',
        '163.com': 'smtp.163.com',
        '126.com': 'smtp.126.com',
        'gmail.com': 'smtp.gmail.com',
        'outlook.com': 'smtp.office365.com',
        'hotmail.com': 'smtp.office365.com',
    }
    return table.get(domain, 'smtp.' + domain)


def main():
    sender = (settings.SENDER_EMAIL or '').strip()
    code = (settings.SENDER_AUTH_CODE or '').strip()
    receiver = (settings.RECEIVER_EMAIL or '').strip()
    if (not sender) or (not code) or (not receiver) \
            or ('你的' in sender) or ('你的' in code) or ('收件邮箱' in receiver):
        raise SystemExit('邮箱还没填好：打开 config.py，填好发件邮箱、授权码、收件邮箱并保存。')

    with open('email.html', encoding='utf-8') as f:
        html_body = f.read()

    msg = MIMEMultipart('alternative')
    msg['Subject'] = Header('论文雷达 · HCI 周报', 'utf-8')
    msg['From'] = sender
    msg['To'] = receiver
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    host = smtp_host(sender)
    print('正在通过 %s 发送……' % host)
    with smtplib.SMTP_SSL(host, 465, timeout=40) as s:
        s.login(sender, code)
        s.sendmail(sender, [receiver], msg.as_string())
    print('发送成功！去 %s 的收件箱查收（若没看到，看一下“订阅邮件/推广/垃圾邮件”分类）。' % receiver)


if __name__ == '__main__':
    main()
