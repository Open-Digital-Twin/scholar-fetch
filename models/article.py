from tools.variables import RANGE_NAME

"""
Row columns:
  0: "title"
  1: "abstract"
  2: "keywords"
  3: "citations"
  4: "pub_location"
  5: "pub_year"
  6: "pub_type"
  7: "pub_url"
  8: "drive_url"
  9: "created_at"
  10: "bibtex"
  11: "gsrank"
  12: "exclude"
  13: "exclude_motive
"""
class Article:
  def __init__(self, title, abstract, keywords, citations, pub_location, pub_year, pub_type, pub_url, drive_url, created_at, bibtex, gsrank, exclude='', exclude_motive=''):
    self.title = title
    self.abstract = abstract
    self.keywords = keywords
    self.citations = citations
    self.pub_location = pub_location
    self.pub_year = pub_year
    self.pub_type = pub_type
    self.pub_url = pub_url
    self.drive_url = drive_url
    self.created_at = created_at
    self.bibtex = bibtex
    self.gsrank = gsrank
    self.exclude = exclude
    self.exclude_motive = exclude_motive

  def body(self):
    return {
      # "range": RANGE_NAME,
      "values": [self.to_row()]
    }
  
  def to_row(self, include_pad=True):
    row = [self.title, self.abstract, self.keywords, self.citations, self.pub_location, self.pub_year, self.pub_type, self.pub_url, self.drive_url, self.created_at, self.bibtex, self.gsrank, self.exclude, self.exclude_motive]

    if include_pad:
      row.insert(0, '')

    return row

def list_has_article(articles, title):
  found = False
  for article in articles:
    if article.title == title:
      found = True
      break
  
  return found
