The details of the python files is as below.

1). games_list.py – This file captures the list of the games from the steam platform and downloads them as html files on the path project/page_list/game_list.
2). games_extract.py – This file creates a csv file games.csv on the path project/game_list.csv with the fields id, title and free and not free.
3). review_list.py – This file downloads the reviews as html pages on the path project/page_list/reviews_list for all the games that are present in the game_list.csv file.
4). review_extract.py – This file creates a final reviews file on the path project/reviews_data.csv with all the reviews data in it. It is a very large file and we have manually updated it every time we did something.
5). summary.py - This files gives the total summary of the dataset. Total games, total reviews, etc...

As the dataset was very large we were not able to attach it here but we have mentioned all the fields that are included in the final dataset file.
