import csv
import os
import re
import argparse
import socket
import string
import urllib
import urllib.request
import urllib.parse


import json
from contextlib import closing
from time import sleep


def down_page(url, maxretries, timeout, pause):
    tries = 0
    htmlpage = None
    while tries < maxretries and htmlpage is None:
        try:
            with closing(urllib.request.urlopen(url, timeout=timeout)) as f:
                htmlpage = f.read()
                sleep(pause)
        except (urllib.error.URLError, socket.timeout, socket.error):
            tries += 1
    return htmlpage


def getgameids(filename):
    ids = set()
    with open(filename, encoding='utf8') as f:
        reader = csv.reader(f)
        for row in reader:
            dir = row[0]
            id_ = row[1]
            name = row[2]
            ids.add((dir, id_, name))
    return ids


def getreviews(ids, timeout, maxretries, pause, out):
    urltemplate = string.Template(
        'http://store.steampowered.com//appreviews/$id?cursor=$cursor&filter=recent&language=english')
    endre = re.compile(r'({"success":2})|(no_more_reviews)')

    for (dir, id_, name) in ids:
        if dir == 'sub':
            print('skipping sub %s %s' % (id_, name))
            continue

        gamedir = os.path.join(out, 'review_pages', 'reviews_details', '-'.join((dir, id_)))

        donefilename = os.path.join(gamedir, 'reviews-done.txt')
        if not os.path.exists(gamedir):
            os.makedirs(gamedir)
        elif os.path.exists(donefilename):
            print('skipping app %s %s' % (id_, name))
            continue

        print(dir, id_, name)

        cursor = '*'
        offset = 0
        page = 1
        maxError = 10
        errorCount = 0
        while True:
            url = urltemplate.substitute({'id': id_, 'cursor': cursor})
            print(offset, url)
            htmlpage = down_page(url, maxretries, timeout, pause)

            if htmlpage is None:
                print('Error downloading the URL: ' + url)
                sleep(pause * 3)
                errorCount += 1
                if errorCount >= maxError:
                    print('Max error!')
                    break
            else:
                with open(os.path.join(gamedir, 'reviews_list-%s.html' % page), 'w', encoding='utf-8') as f:
                    htmlpage = htmlpage.decode()
                    if endre.search(htmlpage):
                        break
                    f.write(htmlpage)
                    page = page + 1
                    parsed_json = (json.loads(htmlpage))
                    cursor = urllib.parse.quote(parsed_json['cursor'])

        with open(donefilename, 'w', encoding='utf-8') as f:
            pass


def main():
    parser = argparse.ArgumentParser(description='Crawler of Steam reviews')
    parser.add_argument('-f', '--force', required=False,
                        action='store_true')
    parser.add_argument(
        '-t', '--timeout',required=False, type=int, default=180)
    parser.add_argument(
        '-r', '--maxretries',required=False, type=int, default=3)
    parser.add_argument(
        '-p', '--pause',required=False, default=0.5,
        type=float)
    parser.add_argument(
        '-m', '--maxreviews',required=False,
        type=int, default=-1)
    parser.add_argument(
        '-o', '--out',required=False, default='project')
    parser.add_argument(
        '-i', '--ids', required=False, default='./project/games_list.csv')
    args = parser.parse_args()

    if not os.path.exists(args.out):
        os.makedirs(args.out)

    ids = getgameids(args.ids)

    print('%s games_list' % len(ids))

    getreviews(ids, args.timeout, args.maxretries, args.pause, args.out)


if __name__ == '__main__':
    main()
