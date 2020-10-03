import paramiko
import pandas as pd
import sqlite3
import datetime


def download_database():    # Download query database from Pi-hole

    localpath = r'D:\RASPBERRY PI\DATA\pihole-FTL.db'   # local address to save the database
    remotepath = '/etc/pihole/pihole-FTL.db'    # location of databes on Raspberry

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try :
        ssh.connect('192.168.0.22', username="pi", password="raspberry")     # put right IP and new password if changed from default;'raspberry' (should be changed!)
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

download_database()    # Download or update (it will overwrite old file) database from Pi-hole - Comment it if there is no need for update

# Read dataframe from database
conn = sqlite3.connect(r'D:\RASPBERRY PI\DATA\pihole-FTL.db')
df_pihole = pd.read_sql_query('SELECT * FROM queries', conn)
conn.close()

# Convert UNIX serial to datetime
df_pihole['timestamp'] = pd.to_datetime(df_pihole['timestamp'], unit='s')
df_pihole.set_index(['timestamp', 'id'], inplace=True)  # Must set multiindex as there are records with same time

df_pihole['Ad'] = ''   # add column Ad

print()
print('Database shape: ', df_pihole.shape)
print()

time_log = pd.read_csv(r'D:\RASPBERRY PI\DATA\logged_ads.csv', header = None)   # set the right path for recorded timestamps of ads start time

time_log.columns = ['timestamp']    # should be only one column in logged Ads (logged_ads.csv) and we'll name it 'timestamp'

d = datetime.timedelta(seconds=30)  # set to estimated max time from begining of commerical and recording the timestamp to catch potential ad servers

for ind in time_log.index:
    click_time = str(time_log['timestamp'][ind])
    print(click_time)
    date_time_to = datetime.datetime.strptime(click_time, '%Y-%m-%d %H:%M:%S')
    date_time_from = date_time_to - d
    
    found_indices = df_pihole.loc[date_time_from:date_time_to].query('domain.str.contains("googlevideo")', engine='python').index   # get subset of dataframe by time and address containing 'googlevideo'

    df_pihole.loc[found_indices, 'Ad'] = 'Suspicious'   # mark as suspicious in column Ad

df_pihole.to_csv (r'D:\RASPBERRY PI\DATA\marked_queries1.csv', index=True, header=True)     # save results to CSV

print('Finished')
