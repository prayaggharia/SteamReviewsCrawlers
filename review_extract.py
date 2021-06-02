import csv
import datetime
import json
import argparse
import sys
import os
import re

from bs4 import BeautifulSoup


def reviews(basepath, outputfile_name):
    helpfulre = re.compile(r'([0-9]+) [a-z]+? found this review helpful')
    funnyre = re.compile(r'([0-9]+) [a-z]+? found this review funny')
    ownedre = re.compile(r'([0-9]+) product')
    revre = re.compile(r'([0-9]+) review')
    timere = re.compile(r'([0-9.]+) hrs on record')
    postedre = re.compile(r'Posted: (.+)')
    idre = re.compile(r'app-([0-9]+)$')
    yearre = re.compile(r'.* [0-9][0-9][0-9][0-9]$')
    userre = re.compile(r'/(profiles|id)/(.+?)/')
    with open(outputfile_name, mode="w", encoding="utf-8", newline="") as outputfile:
        writer = csv.writer(outputfile)
        for root, _, files in os.walk(basepath):
            m = idre.search(root)
            if m:
                id_ = m.group(1)
            else:
                print('skipping non-game path ', root, file=sys.stderr)
                continue
            for file in files:
                fullpath = os.path.join(root, file)
                print('process', fullpath)
                with open(fullpath, encoding='utf8') as f:
                    try:
                        soup = BeautifulSoup(json.loads(f.read())['html'], "html.parser")
                    except ValueError:
                        print('error on ', fullpath, file=sys.stderr)
                    for reviewdiv in soup.findAll('div', attrs={'class': 'review_box'}):
                        helpful = 0
                        funny = 0
                        elem = reviewdiv.find('div', attrs={'class': 'vote_info'})
                        if elem:
                            m = helpfulre.search(elem.text)
                            if m:
                                helpful = m.group(1)
                            m = funnyre.search(elem.text)
                            if m:
                                funny = m.group(1)
                        username = '__anon__'
                        elem = reviewdiv.find('div', attrs={'class': 'persona_name'})
                        if elem:
                            m = userre.search(str(elem.contents))
                            if m:
                                username = m.group(2)
                        owned = 0
                        elem = reviewdiv.find('div', attrs={'class': 'num_owned_games'})
                        if elem:
                            m = ownedre.search(elem.text)
                            if m:
                                owned = m.group(1)
                        numrev = 0
                        elem = reviewdiv.find('div', attrs={'class': 'num_reviews'})
                        if elem:
                            m = revre.search(elem.text)
                            if m:
                                numrev = m.group(1)
                        recco = 0
                        elem = reviewdiv.find('div', attrs={'class': 'title ellipsis'})
                        if elem:
                            if elem.text == 'Recommended':
                                recco = 1
                            else:
                                recco = -1
                        time = 0
                        elem = reviewdiv.find('div', attrs={'class': 'hours ellipsis'})
                        if elem:
                            m = timere.search(elem.text)
                            if m:
                                time = m.group(1)
                        posted = 0
                        elem = reviewdiv.find('div', attrs={'class': 'postedDate'})
                        if elem:
                            m = postedre.search(elem.text)
                            if m:
                                posted = m.group(1).strip()
                                if not yearre.match(posted):
                                    posted = posted + ", %s" % datetime.date.today().year
                        content = ''
                        elem = reviewdiv.find('div', attrs={'class': 'content'})
                        if elem:
                            content = elem.text.strip()
                        writer.writerow(
                            (id_, helpful, funny, username, owned, numrev, recco, time, posted, content))


def main():
    parser = argparse.ArgumentParser(description='Extractor Steam reviews')
    parser.add_argument(
        '-i', '--input',default="./project/page_list/reviews_list",
        required=False)
    parser.add_argument(
        '-o', '--output', help='Output file', default='./project/reviews_data.csv', required=False)
    args = parser.parse_args()
    reviews(args.input, args.output)


if __name__ == '__main__':
    main()
