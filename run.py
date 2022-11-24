#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import os
import ddddocr
import requests


PORTABLEAPPK_USER = os.getenv('PORTABLEAPPK_USER')
PORTABLEAPPK_PASSWD = os.getenv('PORTABLEAPPK_PASSWD')
DINGTALK_TOKEN = os.getenv('DINGTALK_TOKEN')

ocr = ddddocr.DdddOcr(show_ad=False)

# 获取初始身份
session = requests.session()
wp_login_url = "https://portableappk.com/wp-login.php"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.5195.54 Safari/537.36", 
    "Referer": "https://portableappk.com/", 
    }
session.get(wp_login_url, headers=headers)

# 尝试登录
retry = 0
while True:
    # 获取验证码
    gen_captcha_img_url = "https://portableappk.com/wp-content/plugins/wordpress-hack-bundle/addons/gen-captcha-img.php"
    r1 = session.get(gen_captcha_img_url, headers=headers)
    code = ocr.classification(r1.content)
    # 登录
    login_data = {
        "log": PORTABLEAPPK_USER, 
        "pwd": PORTABLEAPPK_PASSWD, 
        "phrase": code, 
        "wp-submit": "登录",
        "redirect_to": "https://portableappk.com/wp-admin/", 
        "testcookie": "1"
        }
    r2 = session.post(wp_login_url, headers=headers,data=login_data, allow_redirects=False)
    if r2.status_code == 302:
        break
    else:
        retry += 1
    if retry > 15:
        text = "portableappk: 多次尝试登录失败"
        data = {"msgtype": "text", "text": {"content": text},"at": {"atMobiles": [], "isAtAll": False},}
        url = "https://oapi.dingtalk.com/robot/send?access_token={}".format(DINGTALK_TOKEN)
        requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        exit()

# 尝试签到
retry = 0
while True:
    # 获取验证码
    r3 = session.get(gen_captcha_img_url, headers=headers)
    code = ocr.classification(r3.content)
    # 签到
    verify_checkin_url = "https://portableappk.com/wp-content/plugins/wordpress-hack-bundle/addons/verify-checkin.php"
    r4 = session.post(verify_checkin_url,headers=headers, data={"phrase": code})
    if r4.json()['success'] == 1:
        text = "portableappk: 签到成功\n"+r4.text
        data = {"msgtype": "text", "text": {"content": text},"at": {"atMobiles": [], "isAtAll": False}, }
        url = "https://oapi.dingtalk.com/robot/send?access_token={}".format(DINGTALK_TOKEN)
        requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        break
    else:
        retry += 1
    if retry > 15:
        text = "portableappk: 签到失败"
        data = {"msgtype": "text", "text": {"content": text},"at": {"atMobiles": [], "isAtAll": False}, }
        url = "https://oapi.dingtalk.com/robot/send?access_token={}".format(DINGTALK_TOKEN)
        requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        break

