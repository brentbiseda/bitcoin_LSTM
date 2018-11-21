#!/usr/bin/python
import csv
import os
import re
import string
import praw
import datetime
import pandas as pd

punctuation = string.punctuation + "\n"
now = datetime.datetime.now()
coin_name=[]
coin_ticker=[]
pos_words=[]
neg_words=[]

with open("Coin List.csv", "r") as f:
    reader = csv.reader(f, delimiter=",")
    for row in reader:
        coin_name.append(str(row[0]).translate(str.maketrans('','',punctuation)).lower())
        coin_ticker.append(str(row[1]).translate(str.maketrans('','',punctuation)).lower())
for line in open("positive_words.csv", "r"):
    pos_words.append(str(line).translate(str.maketrans('','',punctuation)).lower())
for line in open("negative_words.csv", "r"):
    neg_words.append(str(line).translate(str.maketrans('','',punctuation)).lower())

score_list = [0] * len(coin_name)

# Create the Reddit instance
reddit = praw.Reddit('bb1')

# Have we run this code before? If not, create an empty list
if not os.path.isfile("posts_replied_to.txt"):
    comments_analyzed = []
else:
    # Read the file into a list and remove any empty values
    with open("comments_analyzed.txt", "r") as f:
        comments_analyzed = f.read()
        comments_analyzed = comments_analyzed.split("\n")
        comments_analyzed = list(filter(None, comments_analyzed))

users_analyzed = []

# Get the top 5 posts from subreddit
subreddit = reddit.subreddit('Aeon+Ardor+Augur+Best_of_Crypto+BitMarket+BitShares+Bitcoin+BitcoinAll+BitcoinBeginners+BitcoinMarkets+BitcoinMining+BitcoinSerious+BlockChain+CryptoCurrencies+CryptoCurrency+CryptoMarkets+DRKCoin+DashCoin+DashTrader+Digibyte+DoItForTheCoin+EmerCoin+EtherMining+EthereumClassic+GolemProject+ICONOMI+Jobs4Crypto+Liberland+Lisk+LitecoinMarkets+LivingOnBitcoin+MintCoin+Monero+NXT+Namecoin+NiceHash+NobleCoin+NuBits+QuarkCoin+Ripple+SafeMarket+Shadowcash+Stealthcoin+TaCoCoin+Terracoin+ZcashMiners+altcoin+bitcoin_devlist+bitcoin_uncensored+bitcoin_unlimited+bitcoinxt+blackcoin+btc+burstcoin+crypto+dashmarket+dashous+dashpay+decred+digix+dogecoin+ethdapps+ethdev+ethereum+ethinvestor+ethtrader+factom+gridcoin+komodoplatform+lbry+litecoin+litecoinmining+maidsafe+mastercoin+mazacoin+melonproject+myriadcoin+nem+nyancoins+peercoin+pivx+primecoin+reddCoin+reptrader+ripplers+shapeshiftio+siacoin+steemit+storj+stratisplatform+supernet+vertcoin+xmrtrader+zec')

for submission in subreddit.hot(limit=500):
    while True:
        try:
            submission.comments.replace_more()
            break
        except PossibleExceptions:
            print("Handling replace_more exception")
            sleep(1)
    for comment in submission.comments:
        score_counter = 0
        if comment.id not in comments_analyzed:
            comments_analyzed.append(comment.id)
            if comment.author not in users_analyzed:
                users_analyzed.append(comment.author)
                comment_vector = str(comment.body).split(". ")
                for sentence in comment_vector:
                    current_sentence = str(sentence).translate(str.maketrans('', '', punctuation)).lower()
                    for word in current_sentence.split(" "):
                        if word in coin_name:
                            score_counter += 1
                            if word in pos_words:
                                score_counter += 2
                            if word in neg_words:
                                score_counter += -5
                            score_list[coin_name.index(word)] += score_counter
                        elif word in coin_ticker:
                            score_counter += 1
                            if word in pos_words:
                                score_counter += 2
                            if word in neg_words:
                                score_counter += -5
                            score_list[coin_ticker.index(word)] += score_counter

csv_sentiment = pd.read_csv("Coin Sentiment.csv")
csv_sentiment[str(now)] = score_list
csv_sentiment.to_csv("Coin Sentiment.csv", index=False)

with open("comments_analyzed.txt", "w") as f:
    for comment_id in comments_analyzed:
        f.write(comment_id + "\n")