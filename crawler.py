#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import requests
import random
import threading
from bs4 import BeautifulSoup
import _mysql as mysql



user_agent_strings = [
'Mozilla/5.0 (X11; CrOS x86_64 10452.85.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.158 Safari/537.36',
'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.158 Mobile Safari/537.36'
]

urls = ['lektorat-tecklenburg.de']

headers = {
    'User-Agent': random.choice(user_agent_strings)
}
for url in urls:
    response = requests.get('https://' + url, headers=headers)

#print(response.text)

#get all links
links = []
soup = BeautifulSoup(response.text, 'html.parser')

for link in soup.findAll('a'):
    for url in urls:
        if url in link.get('href'):
            links.append(link.get('href'))

print(set(links))
def reset_db(flag):
    if flag:
        return
    query = 'DROP TABLE IF EXISTS links, unarsedpages, authors, articles, tags, revisions2tags;'
    db.query(query)

def init_db():
    queries = ['''

CREATE TABLE IF NOT EXISTS `zork`.`Link` (
  `id` INT NOT NULL,
  `text` TEXT NULL,
  `due` DATETIME NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_bin;

''','''

CREATE TABLE IF NOT EXISTS `zork`.`Unprocessed` (
  `id` INT NOT NULL,
  `text` LONGTEXT NULL,
  `fetched` DATETIME NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_bin;

''','''

CREATE TABLE IF NOT EXISTS `zork`.`Article` (
  `id` INT NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

''','''

CREATE TABLE IF NOT EXISTS `zork`.`Author` (
  `id` INT NOT NULL,
  `name` VARCHAR(255) NULL,
  `abbriviation` VARCHAR(45) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

''','''

CREATE TABLE IF NOT EXISTS `zork`.`Revision` (
  `id` INT NOT NULL,
  `text` LONGTEXT NOT NULL,
  `fetched` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
  `published` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  CONSTRAINT `article_id`
    FOREIGN KEY (`id`)
    REFERENCES `zork`.`Article` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

''','''

CREATE TABLE IF NOT EXISTS `zork`.`Article_has_Author` (
  `Article_id` INT NOT NULL,
  `Author_id` INT NOT NULL,
  PRIMARY KEY (`Article_id`, `Author_id`),
  INDEX `fk_Article_has_Author_Author1_idx` (`Author_id` ASC),
  INDEX `fk_Article_has_Author_Article1_idx` (`Article_id` ASC),
  CONSTRAINT `fk_Article_has_Author_Article1`
    FOREIGN KEY (`Article_id`)
    REFERENCES `zork`.`Article` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Article_has_Author_Author1`
    FOREIGN KEY (`Author_id`)
    REFERENCES `zork`.`Author` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

''','''

CREATE TABLE IF NOT EXISTS `zork`.`Tag` (
  `id` INT NOT NULL,
  `text` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

''','''

CREATE TABLE IF NOT EXISTS `zork`.`Revision_has_Tag` (
  `Revision_id` INT NOT NULL,
  `Tag_id` INT NOT NULL,
  PRIMARY KEY (`Revision_id`, `Tag_id`),
  INDEX `fk_Revision_has_Tag_Tag1_idx` (`Tag_id` ASC),
  INDEX `fk_Revision_has_Tag_Revision1_idx` (`Revision_id` ASC),
  CONSTRAINT `fk_Revision_has_Tag_Revision1`
    FOREIGN KEY (`Revision_id`)
    REFERENCES `zork`.`Revision` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Revision_has_Tag_Tag1`
    FOREIGN KEY (`Tag_id`)
    REFERENCES `zork`.`Tag` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

    ''']
    for query in queries:
        print(query)
        db.query(query)

def make_request():
    query = 'SELECT link FROM links WHERE due > NOW() ORDER BY due DESC LIMIT 1;' 
    db.query(query)


def main():
    threading.Thread(target=lambda: every(args.requestinterval, make_request)).start()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dbhost', type=str, help='DB host', default='localhost')
    parser.add_argument('--dbname', type=str, help='DB name')
    parser.add_argument('--dbuser', type=str, help='DB user name')
    parser.add_argument('--dbpassword', type=str, help='password for DB user')
    parser.add_argument('--hostlist', type=str, help='path to a textfile containing the the host addresses. Each Line one host address. No http(s)://', default='hosts.txt')
    parser.add_argument('--requestinterval', type=int, help='time to wait between requests in seconds', default=10)
    parser.add_argument('--refreshinterval', type=int, help='time to wait before revisit a link in hours', default=24)
    parser.add_argument('--resetdb', action='store_true')
    args = parser.parse_args()

    db=mysql.connect(host=args.dbhost,user=args.dbuser,passwd=args.dbpassword,db=args.dbname)
    reset_db(args.resetdb)
    init_db()

    with open(args.hostlist, 'r') as hostlist:
        urls=hostlist.read().split('\n')

    main()
