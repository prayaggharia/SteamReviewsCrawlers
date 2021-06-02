import argparse
import re
import socket
import os
from contextlib import closing
from time import sleep
import urllib
import urllib.request



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


def getgames(timeout, maxretries, pause, out):
    baseurl = 'http://store.steampowered.com/search/results?sort_by=_ASC&snr=1_7_7_230_7&page='
    page = 0
    gameidre = re.compile(r'/(app|sub)/([0-9]+)/')

    pagedir = os.path.join(out, 'page_list', 'games_list')
    if not os.path.exists(pagedir):
        os.makedirs(pagedir)

    retries = 0
    while True:
        url = '%s%s' % (baseurl, page)
        print(page, url)
        htmlpage = down_page(url, maxretries, timeout, pause)

        if htmlpage is None:
            print('Error downloading: ' + url)
            sleep(pause * 10)
        else:
            htmlpage = htmlpage.decode()
            with open(os.path.join(pagedir, 'page-%s.html' % page), mode='w', encoding='utf-8') as f:
                f.write(htmlpage)

            pageids = set(gameidre.findall(htmlpage))
            if len(pageids) == 0:

                if retries < maxretries:
                    print('empty', retries)
                    sleep(5)
                    retries += 1
                    continue
                else:
                    break
            print(len(pageids), pageids)
            retries = 0
            page += 1


def main():
    parser = argparse.ArgumentParser(description='Crawler of Steam game ids and names')
    parser.add_argument('-f', '--force',required=False,
                        action='store_true')
    parser.add_argument(
        '-t', '--timeout',required=False, type=int, default=180)
    parser.add_argument(
        '-r', '--maxretries', required=False, type=int, default=5)
    parser.add_argument(
        '-p', '--pause',required=False, default=0.5,
        type=float)
    parser.add_argument(
        '-m', '--maxreviews',required=False,
        type=int, default=-1)
    parser.add_argument(
        '-o', '--out',required=False, default='project')
    args = parser.parse_args()

    if not os.path.exists(args.out):
        os.makedirs(args.out)

    getgames(args.timeout, args.maxretries, args.pause, args.out)


if __name__ == '__main__':
    main()
