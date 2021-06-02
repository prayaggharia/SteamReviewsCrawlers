import csv
import os
import argparse
import re
import socket
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


def extract(basepath, outputfile_name):
    gameidre = re.compile(r'/(app|sub)/([0-9]+)/')
    gamenamere = re.compile(r'<span class="title">(.*?)</span>')
    gamepricere = re.compile(r'data-price-final="\d+"')
    gamepriceextractre = re.compile(r'\d+')
    games = dict()
    for root, _, files in os.walk(basepath):
        for file in files:
            fullpath = os.path.join(root, file)
            with open(fullpath, encoding='utf8') as f:
                htmlpage = f.read()

                gameids = list(gameidre.findall(htmlpage))
                gamenames = list(gamenamere.findall(htmlpage))
                gameprices = list(gamepricere.findall(htmlpage))
                for app, id_, name, price in zip([app for (app, _) in gameids], [id_ for (_, id_) in gameids], gamenames, gameprices):
                    games[(app, id_, gamepriceextractre.findall(price)[0])] = name
    with open(outputfile_name, mode='w', encoding='utf-8', newline='') as outputfile:
        writer = csv.writer(outputfile)
        for app, id_, price in games:
            writer.writerow([app, id_, games[(app, id_, price)], getFreeLabel(price)])


def getFreeLabel(price):
    if price == "0":
        return "FREE TO PLAY"
    else:
        return "NOT FREE"

def main():
    parser = argparse.ArgumentParser(description='Crawler of Steam game ids and names')
    parser.add_argument(
        '-i', '--input', help='Input file or path (all files in subpath are processed)', default='./project/page_list/games_list',
        required=False)
    parser.add_argument(
        '-o', '--output', help='Output file', default='./data/games_list.csv', required=False)
    args = parser.parse_args()

    extract(args.input, args.output)


if __name__ == '__main__':
    main()
