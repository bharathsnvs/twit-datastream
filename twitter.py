from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API
from tweepy import Cursor
import numpy as np
import pandas as pd

import credentials
import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

### AUTHENTICATE ###
class TwitterAuthenticator():
    def authenticate_twitter_app(self):
        auth = OAuthHandler(credentials.CONSUMER_KEY, credentials.CONSUMER_SECRET)
        auth.set_access_token(credentials.ACCESS_TOKEN, credentials.ACCESS_TOKEN_SECRET)
        return auth

### TWITTER CLIENT ###
class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)

        self.twitter_user = twitter_user
    
    def get_twitter_client_api(self):
        return self.twitter_client
    
    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets
    
    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list
    
    def get_home_timeline_tweets(self, num_tweets):
        home_timeline_tweets = []
        for tweets in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweets)
        return home_timeline_tweets
    

class TwitterStreamer():
    """
    Class for streaming and processing live tweets
    """
    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()
    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        # Handle twitter authentication and connection to the streaming api
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_authenticator.authenticate_twitter_app()

        stream = Stream(auth, listener)
        #Filter stream based on keyword
        stream.filter(track=hash_tag_list)


class TwitterListener(StreamListener):
    """
    Basic class that prints received tweets to standard output
    """
    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self, data):
        try:
            print(data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(data)
            return True
        except BaseException as e:
            print("Error on_data: %s" % str(e))
        return True

    def on_error(self, status):
        if status == 420:
            ### 420 error = twitter saying you are accessing the tweets too fast too soon ###
            return False
        print(status)

class TweetAnalyzer():
    """
    Functionality for analyzing and analyzing content from tweets
    """
    def tweets_to_df(self, tweets):
        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=["tweets"])

        
        #df['id'] = np.array([tweet.id for tweet in tweets])
        #df['len'] = np.array([len(tweet.text) for tweet in tweets])
        
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['source'] = np.array([tweet.source for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])

        return df 
    
#### EMAIL SETUP ####



#####


if __name__ == "__main__":

    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()
    api = twitter_client.get_twitter_client_api()

    # # # WAY TO SCNA THROUGH MULTIPLE USERS # # #

    tweets_array = []
    name_list = ["naval", "paulg", "elonmusk"]
    for i in name_list:
        tweets = api.user_timeline(screen_name=i, count=10)
        tweets_array = tweets_array + tweets
        # for tweet in tweets:
        #     if tweet.retweet_count > 100:
        #         tweets_array = tweets_array + tweet
        #     else:
        #         None
    
    # # #
    print(tweets_array)
    # Below line prints out what features of a tweet we can extract
    #print(dir(tweets[0]))
    
    #print(tweets[0].retweet_count)

    #tweets = api.user_timeline(screen_name='paulg', count=10)

    #######

    df = tweet_analyzer.tweets_to_df(tweets_array)

    msg = EmailMessage()

    recipients = ['bharathsnvs@gmail.com', 'anand.waghmare_asp21@ashoka.edu.in']
    sender = "usalresearchteam@gmail.com"

    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Handpicked automated twitter stream'
    msg['From'] = "usalresearchteam@gmail.com"
    msg['To'] = ", ".join(recipients)
    html = df.to_html()
    HTML_BODY = MIMEText(html, 'html')
    msg.attach(HTML_BODY)

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login("usalresearchteam@gmail.com", "vkbs1818")
    server.sendmail(sender, recipients, msg.as_string())

    server.quit()

    print(df)

    #df.to_csv(r'output.csv', header=True)
    #######

    # Apt output for API
    # print(df.to_json(orient='records'))

    #twitter_client = TwitterClient('naval')
    #print(twitter_client.get_user_timeline_tweets(5))

    #print(twitter_client.get_home_timeline_tweets(1))

    ####  STREAM TWEETS  ######
    # hash_tag_list = ['cricket']
    # fetched_tweets_filename = "tweets.txt"
    # twitter_streamer = TwitterStreamer()
    # twitter_streamer.stream_tweets(fetched_tweets_filename, hash_tag_list)
    ##########