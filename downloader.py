import os
import time
import wget
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool
from bs4 import BeautifulSoup as bs
url = "https://oceans11.lanl.gov/deepwaterimpact/yC31_300x300x300-FourScalars_resolution.html"
path = os.path.join(os.getcwd(), 'yC31')


def download(link):
  filepath = os.path.join(path, link[1])
  if not os.path.isfile(filepath):
    while True:
      try:
        wget.download(link[0], filepath)
        break
      except ConnectionResetError:
        print('Timeout sleep')
        time.sleep(5)


def get_vti(src):
  links = []
  html = urllib.request.urlopen(src).read()
  #print(html)
  page = bs(html, features="lxml")
  target = page.find_all("a", download="")
  for link in target:
    curlink = link.get('href')
    curname = link.contents[0]
    if curlink.endswith('vti'):
      links.append([curlink, curname])

  executor = ThreadPoolExecutor(max_workers=8)
  for link in links:
    executor.submit(download, link)


get_vti(url)
