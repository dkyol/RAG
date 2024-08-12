import pandas as pd
import os
import datetime as dt
from utils import empty


class UserDb:

    def __init__(self, data_folder):
        # TODO replace this with a real DB instead of csvs 
        self.user_filepath = os.path.join(data_folder, 'users.csv')
        self.query_filepath = os.path.join(data_folder, 'queries.csv')

        if not os.path.exists(self.user_filepath):
            df = pd.DataFrame(columns=['s_ecid', 'username', 'timestamp'])
            df.to_csv(self.user_filepath, index=False)

        if not os.path.exists(self.query_filepath):
            df = pd.DataFrame(
                columns=['s_ecid', 'query_type', 'query', 'timestamp'])
            df.to_csv(self.query_filepath, index=False)

    @staticmethod
    def _get_timestamp():
        return dt.datetime.utcnow().replace(microsecond=0)    

    def get_username(self, s_ecid):
        df = pd.read_csv(self.user_filepath)
        username = df.loc[df['s_ecid'] == s_ecid, 'username'].tolist()
        if len(username) > 0:
            return username[0]
        return None

    def associate_username(self, s_ecid, username):
        if not empty(s_ecid) and not empty(username):
            df = pd.read_csv(self.user_filepath)
            if len(df.loc[df['s_ecid'] == s_ecid, 'username'].tolist()) > 0:
                df.loc[df['s_ecid'] == s_ecid, 'username'] = username
            else:
                df = pd.concat([df, pd.DataFrame.from_records([{'s_ecid': s_ecid,
                                                                'username': username,
                                                                'timestamp': UserDb._get_timestamp()}])])
            df = df.drop_duplicates(subset='s_ecid', keep='last')
            df.to_csv(self.user_filepath, index=False)

    def log_query(self, s_ecid, query_type, query):
        if not empty(s_ecid) and not empty(query_type) and not empty(query):
            df = pd.read_csv(self.query_filepath)
            df = pd.concat([df, pd.DataFrame.from_records([{'s_ecid': s_ecid,
                                                            'query_type': query_type,
                                                            'query': query,
                                                            'timestamp': UserDb._get_timestamp()}])])
            df.to_csv(self.query_filepath, index=False)

    def get_users(self):
        users = pd.read_csv(self.user_filepath)
        users = users.sort_values(by='timestamp', ascending=False)
        return users

    def get_queries(self, n=50):
        users = self.get_users()
        users = users[['s_ecid', 'username']]
        queries = pd.read_csv(self.query_filepath)
        queries = queries.merge(users, on='s_ecid')
        queries = queries[['s_ecid', 'username', 'query_type', 'query', 'timestamp']]
        queries = queries.sort_values(by='timestamp', ascending=False)
        queries = queries.head(n)
        # queries = queries.iloc[::-1]
        return queries

