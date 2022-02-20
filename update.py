# -*- coding: utf-8 -*-

import os
import nfc
import time
import requests
import RPi.GPIO as GPIO
from multiprocessing import Process

API_URL = os.environ['API_URL']
PROXY = os.environ['PROXY_URL']
PROXIES = {
  "http": PROXY,
  "https": PROXY,
}
PIN = 21

service_code = 0x100b

def try_post(student_id):
  print(student_id)
  for _ in range(10):
    try:
      requests.post(API_URL, json={"student_id": student_id}, proxies=PROXIES, verify = False)
      break
    except Exception as e:
      print('ignore error:', e)
    time.sleep(1)

def connected(tag):
  global prev, p
  idm, pmm = tag.polling(system_code=0x809e)
  tag.idm, tag.pmm, tag.sys = idm, pmm, 0x809e

  if isinstance(tag, nfc.tag.tt3.Type3Tag):
    try:
      # 学籍番号を読み取る
      sc = nfc.tag.tt3.ServiceCode(service_code >> 6, service_code & 0x3f)
      bc = nfc.tag.tt3.BlockCode(0, service=0)
      data = tag.read_without_encryption([sc], [bc])
      student_id = int(data[2:9])

      # LEDを点滅させる
      p.start(50)
      p.ChangeFrequency(220)
      time.sleep(1.1)
      p.stop()

      # APIサーバにリクエストを送る
      Process(target=try_post, args=(student_id,)).start()
    except Exception as e:
      print(e)
  else:
    print("tag isn't Type3Tag")


clf = nfc.ContactlessFrontend('usb')
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.OUT, initial=GPIO.LOW)
p = GPIO.PWM(PIN, 1)

while True:
  try:
    clf.connect(rdwr={'on-connect': connected})
  except Exception as e:
    pass