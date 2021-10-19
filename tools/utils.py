from scholarly import ProxyGenerator

from os import listdir
from os.path import isfile, join
import logging

from tools.variables import SCRAPER_API_KEY

def setup_logging():
  files = [f for f in listdir('logs') if isfile(join('logs', f))]

  index = 0
  if (len(files) > 0):
    file_indexes = [int(filename.split('.')[0].split('-')[1]) for filename in files]
    index = max(file_indexes) + 1

  for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

  log_filename = 'logs/app-' + str(index) + '.log'
  logging.basicConfig(filename=log_filename, filemode='w', format='%(asctime)s %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
  logging.debug("Logging started.")

def setup_proxy(type):
  if (type == 'tor'):
    pg = ProxyGenerator()
    pg.Tor_Internal(tor_cmd="tor")
  elif (type == 'scraperapi'):
    pg = ProxyGenerator()
    pg.ScraperAPI(SCRAPER_API_KEY)
  elif (type == 'luminati'):
    pg = ProxyGenerator()
    pg.Luminati(
      usr="lum-customer-hl_37551f3f-zone-static",
      passwd="z3t508x58vm6",
      proxy_port=80
    )

  return pg
