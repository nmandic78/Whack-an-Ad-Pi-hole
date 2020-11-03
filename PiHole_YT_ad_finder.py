import paramiko
import pandas as pd
import sqlite3
import datetime


def download_database():    # Download query database from Pi-hole

    localpath = r'D:\RASPBERRY PI\DATA\pihole-FTL.db'   # local address to save the database
    remotepath = '/etc/pihole/pihole-FTL.db'    # location of databes on Raspberry

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # put right IP and new password if changed from default;'raspberry' (should be changed!)
        ssh.connect('192.168.0.22', username="pi", password="mane77peru22")
        print('Connected')
        sftp = ssh.open_sftp()
        print('SFTP opened')
        sftp.get(remotepath, localpath)
        print('Got it')
        sftp.close()
        ssh.close()
        print('SFTP, SSH closed')
        return True
    except Exception as e:
        print(e)
        return False


print(download_database())    # Download or update (it will overwrite old file) database from Pi-hole

# Read dataframe from database
conn = sqlite3.connect(r'D:\RASPBERRY PI\DATA\pihole-FTL.db')
df_pihole = pd.read_sql_query('SELECT * FROM queries', conn)
conn.close()

# Convert UNIX serial to datetime, then convert default output of to_datetime from UTC to CET,
# and than to tz_naive by tz_localize(None)
df_pihole['timestamp'] = pd.to_datetime(df_pihole['timestamp'], unit='s').dt.tz_localize('UTC').dt.tz_convert('CET').dt.tz_localize(None)
print(df_pihole.index)

df_pihole.set_index(['timestamp', 'id'], inplace=True)  # Must set multiindex as there are records with same time
# df_pihole.index.get_level_values('timestamp').tz_localize('CET')


df_pihole['Ad'] = ''   # add column Ad

print()
print('Database shape: ', df_pihole.shape)
print()

time_log = pd.read_csv(r'D:\RASPBERRY PI\DATA\logged_ads.csv', header=None)

time_log.columns = ['timestamp']    # should be only one column in logged Ads (logged_ads.csv) and we'll name it 'timestamp'

# set to estimated max time from begining of commerical and recording the timestamp to catch potential ad servers
d = datetime.timedelta(seconds=30)

for ind in time_log.index:
    click_time = str(time_log['timestamp'][ind])
    # print(click_time)
    date_time_to = datetime.datetime.strptime(click_time, '%Y-%m-%d %H:%M:%S')
    # print('DT: ', date_time_to)

    date_time_from = date_time_to - d

    # get subset of dataframe by time and address containing 'googlevideo'
    found_indices = df_pihole.loc[date_time_from:date_time_to].query('domain.str.contains("googlevideo")', engine='python').index

    df_pihole.loc[found_indices, 'Ad'] = 'Suspicious'   # mark as suspicious in column Ad


df_pihole.to_csv(r'D:\RASPBERRY PI\DATA\marked_queries1.csv', index=True, header=True)     # save results to CSV


# transformation to get logged domains occurences share in whole list of those domains (to filter false positives)

df_tmp = df_pihole.loc[df_pihole['Ad'] == 'Suspicious']['domain'].value_counts().to_frame(name='susp_count')
df_tmp.index.name = 'domain'

df_tmp_all = df_pihole['domain'].value_counts().to_frame(name='all_count')
df_tmp_all.index.name = 'domain'


df_tmp = pd.merge(df_tmp, df_tmp_all, left_index=True, right_index=True, how='left')

df_tmp['susp_share'] = df_tmp['susp_count'] / df_tmp['all_count']

df_tmp.sort_values(by=['susp_share'], ascending=False, inplace=True)

print(df_tmp)
print()

df_tmp.to_csv(r'D:\RASPBERRY PI\DATA\suspicious_domains_1.csv', index=True, header=True)     # save results to CSV

print('Finished')
