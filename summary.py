import argparse
import csv
import json
import sys
from collections import defaultdict


def process_reviews(inputfile_name, output_dir):
    with open(inputfile_name, mode="r", encoding="utf-8") as inputfile:
        totalreviews = 0
        totalhours = 0
        users = defaultdict(lambda: defaultdict(float))
        games = defaultdict(lambda: defaultdict(float))
        reader = csv.reader(inputfile)
        for (id_, helpful, funny, username, owned, numrev, recco, time, posted, content) in reader:
            time = float(time)
            totalreviews += 1
            totalhours += time
            users[username]['games'] += 1
            users[username]['time'] += time
            games[id_]['reviews'] += 1
            games[id_]['time'] += time
            if totalreviews % 1000 == 0:
                print('\r%i' % totalreviews, end='', flush=True, file=sys.stderr)

        summary = {'reviews': totalreviews,
                   'hours': totalhours,
                   'users': len(users),
                   'games': len(games)}
        with open(output_dir + '/summary.json', mode='w', encoding="utf-8") as f:
            json.dump(summary, f)
        with open(output_dir + '/users.json', mode='w', encoding="utf-8") as f:
            json.dump(users, f)
        with open(output_dir + '/games.json', mode='w', encoding="utf-8") as f:
            json.dump(games, f)


def main():
    parser = argparse.ArgumentParser(description='Stats from Steam reviews')
    parser.add_argument(
        '-i', '--input', help='Input file of reviews', required=False, default="./project/reviews_data.csv")
    parser.add_argument(
        '-o', '--output', help='Output dir for stats', required=False, default="./project/")
    args = parser.parse_args()

    process_reviews(args.input, args.output)


if __name__ == '__main__':
    main()
