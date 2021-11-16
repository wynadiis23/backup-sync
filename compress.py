import os
import zipfile
import time
from datetime import datetime, timedelta
import glob
import configparser

"""
 TODO:
 1. Make a log file 
 2. Move compressed file to the sync folder | in progress
 3. (optional) create a notification 
"""


def finish():
    input("you can press any key to close this window!")

#backup-20210603
def get_time():
    now = datetime.now()
    # current_time = now.strftime("%H:%M:%S")
    current_date = now.strftime("%Y%m%d")
    initial = 'backup-'+current_date
    # print("Current Time =", current_time)
    # print("Current Date =", current_date)
    print("initial =", initial)
    return initial


def compress(files):
    now = datetime.now()
    current_time = now.strftime("%H%M%S")
    curr_date = get_time()

    # foo_zip = zipfile.ZipFile('hasil_backup_1.zip', 'w')
    # foo_zip.write('backup-20210607-020733', compress_type = zipfile.ZIP_LZMA)
    # foo_zip.close()

    #multiple file

    print('start compressing')
    zipName = 'final-'+curr_date+'-'+current_time+'.zip'
    with zipfile.ZipFile(zipName, 'w') as zipF:
        for file in files:
            print('compressing ' + file)
            zipF.write(file, compress_type=zipfile.ZIP_LZMA)
        zipF.close()
        print('compress and archiving complete')

    finish()

# def move_file_to_sync(file_name):
#     # get sync path from config file
#     sync_path = read_config_file('sync')

#     if ()

def check_compressed_file(file):
    comp_file = 

def tlf_logs(tlf_content):
    # check if files are already compressed before, if files have been compressed, there is no need to compress again.
    if (os.path.isfile('./two_latest_files.txt')):
        # there is a file. check it first. if yes go replace the current content
        

    else:
        # no exact file, create it
        tlf_cr = open('./two_latest_files.txt', 'w+')
        tlf_cr.close()


def check_latest_files():
    # files = os.listdir(rootDir)
    # print(files)
    db_dir = read_config_file('dir')
    curr_date = get_time()
    #testing
    curr_date = "backup-20211116"
    print('\ncari file latest:')
    files =  sorted(glob.glob(db_dir + '/' + curr_date + '-*'), key=os.path.getmtime)

    if not files:
        print('there is no backup file today!')

        finish()
    else:
        #append two last elemets
        two_latest_files = []
        two_latest_files.append(files[-1])
        two_latest_files.append(files[-2])

        # check if the tlf log has been created, if not, create it. 
        # if yes then compare it with the latest ltf, if same do not do the archive and compress, if not replace the current content and continue the program
        bool_latest_files = tlf_logs(two_latest_files)
        if (bool_latest_files):
            # continue to archive and compress
            print('\ntwo latest files are:')
            for i in two_latest_files:
                print(i)
            # print(two_latest_files)
            # print(files)
            # print('mamang')
            compress(two_latest_files)
        else:
            # end. the compressed file with same backup file already created
            finish()

def check_config_file():
    # This will check if there is a config file or not. If there is no config file, it will generate it.
    if (os.path.isfile('./config.ini')):
        print('config file already exist! continue')

        # continue to check latest file
        check_latest_files()
    else:
        # generate a config file
        print('config file not found. Program will generate needed files')
        print('generate config file')
        # initialize config parser
        config = configparser.ConfigParser()

        # get input from user
        input_db_dir = input('Plese input path to Datastore folder : \n')
        input_sync_dir = input('Plese input path to Sync folder : \n')

        # setup config file
        config.add_section('user_info')
        config.set('user_info', 'dir', input_db_dir)
        config.set('user_info', 'sync_dir', input_sync_dir)

        # Write the new structure to the new file
        with open(r"./config.ini", 'w') as configfile:
            config.write(configfile)

        if (os.path.isfile('./config.ini')):
            print('config file successfully generated!\n')

            # continue to check latest file
            check_latest_files()
        else:
            print('error when generate config file!\n')

def read_config_file(query):
    # this line is for read configuration file. Please set your db toko root dir on the config.ini file.
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
    user_info = config['user_info']
    user_config = user_info[query]

    return user_config

def main():
    check_config_file()



if __name__="__main__":
    main()
