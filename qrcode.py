import requests
import json
from PIL import Image 
from io import BytesIO

r = requests.get('https://login.web.wechat.com/jslogin?appid=wx782c26e4c19acffb&redirect_uri=https%3A%2F%2Fweb.wechat.com%2Fcgi-bin%2Fmmwebwx-bin%2Fwebwxnewloginpage&fun=new&lang=en_US&_=1674452492274')
code = r.text.split('"')[-2]
qr_r = requests.get(f'https://login.weixin.qq.com/qrcode/{code}')
img = Image.open(BytesIO(qr_r.content))
img.show()

