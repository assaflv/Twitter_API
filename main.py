import requests
import os
import pandas as pd
from datetime import timedelta

def auth():
    return os.environ.get("BEARER_TOKEN")


def create_url():
    # Replace with user ID below
    user_id = 44196397
    return "https://api.twitter.com/2/users/{}/tweets".format(user_id)


def get_params(start_time):
    # If the first time of the script take the min date

    return {
        "max_results": 100,
        "start_time": start_time,
        "tweet.fields": "created_at,public_metrics"
    }

def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def connect_to_endpoint(url, headers, params):
    response = requests.request("GET", url, headers=headers, params=params)
    #print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()

def run_API(start_time):
    bearer_token = auth()
    url = create_url()
    headers = create_headers(bearer_token)
    params = get_params(start_time)
    json_response = connect_to_endpoint(url, headers, params)
    return json_response

def get_tweets(start_time):
    json_response = run_API(start_time)
    if json_response['meta']['result_count'] == 0: return False # If there is no new tweets

    data = json_response['data']
    tweet_df = pd.DataFrame(data)

    tweet_df['likes'] = tweet_df['public_metrics'].apply(lambda x: x.get('like_count')) # Extract likes from 'public_metrics' data
    tweet_df['Above100'] = tweet_df['likes'].apply(lambda x: "Hot" if x > 100 else False) # Check if more then 100 likes and mark as HOT
    tweet_df.drop(['public_metrics'], axis=1, inplace=True) # Drop the public metrics column
    tweet_df['created_at'] = pd.to_datetime(tweet_df['created_at'])  # Convert to date format (ISO 8601)

    return tweet_df

def main():
    #The for loop is to simulate mulipale running. 
    #The start time is the first date that the API can get - use if it's the first running.
   
    start_time = None
    for i in range(0,4):
        if start_time == None:
            start_time = "2010-11-06T00:00:01Z"
            tweet_df = get_tweets(start_time)
        else:
            start_time = tweet_df['created_at'].max()
            start_time = start_time + timedelta(seconds=1)
            new_tweet_df = get_tweets(start_time.isoformat())
            if new_tweet_df == False: break #No new tweets
            else:
                tweet_df = pd.concat([tweet_df, new_tweet_df],ignore_index=True)

    tweet_df.to_csv('tweets.csv')
if __name__ == "__main__":
    main()



