from external.scihub import SciHub
from scholarly import scholarly
from datetime import datetime
import logging

from tools.sheets import get_articles_from_sheet, insert_article_in_sheet, upload_file
from models.article import Article, list_has_article
from tools.utils import setup_proxy

def main(argv):
  logging.warning("Starting scholar parser...")
  scholarly.use_proxy(setup_proxy('scraperapi'))
  scholarly.set_timeout(1200)
  logging.info("Proxy set")

  logging.info("Getting saved articles...")
  sheet_articles = get_articles_from_sheet()
  logging.info("Saved articles received.")

  logging.info("Defining search query...")

  try:
    argc = len(argv)

    if argc >= 3:
      query = argv[1]
      offset = int(argv[2])
      start_offset = len(sheet_articles) + offset
    elif argc == 2:
      query = argv[1]
      start_offset = len(sheet_articles)
    else:
      logging.info("Query argument not filled.")

    logging.info("Offset value defined. Start="+str(start_offset))
  except:
    query = argv[1]
    start_offset = len(sheet_articles)
    logging.info("Offset value undefined or invalid. Start="+str(start_offset))

  search_query = scholarly.search_pubs(query, start_index=start_offset, citations=False)

  sh = SciHub()

  loop_count = 0
  articles_found = 0
  not_done = True
  logging.info('Starting article loop')
  while not_done:
    loop_count += 1
    logging.info('Getting next result...')

    try:
      q = next(search_query)
    except StopIteration:
      logging.info('Query ended. All results parsed.')
      not_done = False
      break

    logging.info('Article \"' + q["bib"]["title"] + '\".')

    if list_has_article(sheet_articles, q["bib"]["title"]):
      logging.info('\tArticle already on list. Skipping...')
    else:
      logging.info('\tNew article! Getting more information...')
      articles_found += 1

      result = scholarly.fill(q)
      logging.info(result)

      try:
        pub_type = result["bib"]["pub_type"]
      except:
        pub_type = 'UNKNOWN'
      logging.info("Item is {}.".format(pub_type))

      pub_location = 'UNKNOWN'
      try:
        if result["bib"]["pub_type"] in set(['inproceedings', 'incollection']):
          pub_location = result["bib"]["booktitle"]
        elif result["bib"]["pub_type"] == 'article':
          pub_location = result["bib"]["journal"]
      except:
        pub_location = 'UNKNOWN'

      try:
        abstract = result["bib"]["abstract"]
      except:
        abstract = ''

      try:
        url = result['pub_url']
      except:
        try:
          url = result['eprint_url']
        except:
          url = ''

      try:
        gsrank = result['gsrank']
      except:
        gsrank = ''

      try:
        bibtex = scholarly.bibtex(result)
      except:
        bibtex = ''

      entry = Article(
        title=result["bib"]["title"],
        abstract=abstract,
        keywords='',
        citations=result["num_citations"],
        pub_location=pub_location,
        pub_year=result["bib"]["pub_year"],
        pub_type=pub_type,
        pub_url=url,
        drive_url="",
        created_at=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        bibtex=bibtex,
        gsrank=gsrank
      )

      logging.info("Found new article!")
      print('New article. Articles found: '+str(articles_found))
      downloaded = False

      if len(entry.pub_url) > 0:
        try:
          logging.info('\tDownloading Article PDF')
          result = sh.download(entry.pub_url, destination='temp')
          downloaded = True
        except:
          logging.error('\tFailed downloading file.')
      else:
        logging.info('\tNo URL to query file.')

      if downloaded == True:
        logging.info('\tFinished Downloading Article PDF')
        try:
          logging.info('\tFilename: ' + result['name'])
          logging.info('\tUploading...')
          upload = upload_file(result['name'], 'temp/' + result['name'])
          entry.drive_url = 'https://drive.google.com/file/d/' + upload['id'] + '/view?usp=sharing'
          logging.info('\tUploaded file with id ' + upload['id'])
        except:
          logging.info('Error uploading file.')

      logging.info('\tInserting article in spreadsheet')
      insert_article_in_sheet(article=entry)
      sheet_articles.append(entry)
      logging.info('\tArticle inserted.')

  logging.info("Parser closing.")

  logging.info("\tArticles found: " + str(articles_found))
  logging.info("\tSheet articles: " + str(len(sheet_articles)))
  logging.info("\tLoop count: " + str(loop_count))
