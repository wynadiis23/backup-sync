import os
import zipfile
import time
from datetime import datetime
import glob
import configparser
import shutil # copy file
import logging # logging

"""
 TODO:
 1. Make a log file | in progress
 2. Move compressed file to the sync folder | completed
 3. (optional) create a notification 
"""


def finish():
    input("you can press any key to close this window!")

def log_insert(file, message, level):
    # basic configuration
    format_log = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    log_ = logging.FileHandler(file)
    log_.setFormatter(format_log)

    logger = logging.getLogger(file)
    logger.setLevel(level)

    if not logger.handlers:
        logger.addHandler(log_)
        # check logging type
        if (level == logging.INFO):
            logger.info(message)
        if (level == logging.ERROR):
            logger.error(message)
        if (level == logging.WARNING):
            logger.warning(message)

    log_.close()
    logger.removeHandler(log_)

    return


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
    i = 1
    with zipfile.ZipFile(zipName, 'w') as zipF:
        for file in files:
            print(f'[{i}/{len(files)}]')
            log_txt = f'compressing {file}' 
            print(log_txt)
            log_insert('./files.log', log_txt, logging.INFO)
            zipF.write(file, compress_type=zipfile.ZIP_LZMA)
            i += 1
        zipF.close()
    # update two last files txt
    replace_tlf_log(files)

    # move final backup to sync folder
    move_final_to_sync(zipName)

    print('compress and archiving complete')

    finish()

# def move_file_to_sync(file_name):
#     # get sync path from config file
#     sync_path = read_config_file('sync')

#     if ()

# def check_compressed_file(file):
#     comp_file = 

def read_tlf_old():
    tlf_old = []
    with open('./two_latest_files.txt') as file:
        tlf_old = [line.strip() for line in file]
    return tlf_old

def tlf_logs(tlf_new):
    # check if files are already compressed before, if files have been compressed, there is no need to compress again.
    print(tlf_new)
    if (os.path.isfile('./two_latest_files.txt')):
        print('replace tlf txt')
        # there is a file. check it first. if yes go replace the current content
        tlf_old = read_tlf_old()
        # compare the list, if not same, then continue, else do not archive and compress
        # tlf_new.sort()
        # tlf_old.sort()

        # if 1 are not same, then it is not identical
        # if we do it like this, there is a chance for a file to compressed multiple times.
        # if tlf_old == tlf_new:
        #     print('the list are same, do not archiving and compress')
        # else:
        #     print('the list are not same, continue archiving and compressing')

        # instead of matching all the list, let's find a matching string
        # so if there is a matching string between the list, do not do the archiving and compressing.
        # if there is no matching string, do the archiving and compressing
        # like this, a file will not compressed multiple times
        if (bool(set(tlf_new).intersection(tlf_old))):
            # there is a same string
            print('one of the file is already compressed, please check it')

            return 0 # return false, or finish the program
        else:
            # no same string

            return 1 # return true
            print('losog')

    else:
        print('create new tlf txt')
        # no exact file, create it
        # and do archiving and compressing
        tlf_cr = open('./two_latest_files.txt', 'w+')
        for i in tlf_new:
            tlf_cr.write(i)
            tlf_cr.write('\n')
        tlf_cr.close()

        return 1 # return true

def replace_tlf_log(tlf_new):
    # this section is buggy as hell. for now
    print('replacing two latest files txt')
    tlf_old = read_tlf_old()
    # Read in the file
    with open('./two_latest_files.txt', 'r') as file :
        filedata = file.read()

    # Replace the target string
    x = 0
    for i in tlf_new:
        print(tlf_old[x])
        print(i)
        filedata = filedata.replace(tlf_old[x], tlf_new[x])
        x += 1

    # Write the file out again
    print(filedata)
    with open('./two_latest_files.txt', 'w') as file:
        file.write(filedata)

    print('replacing complete')
    return 1 # no validation :)))))

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
        if (bool(bool_latest_files)):
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

def move_final_to_sync(zipName):
    # check zip files if there a
    if (os.path.isfile(f'./{zipName}')):
        # copy zip file to sync folder
        sync_folder = read_config_file('sync_dir')
        b = shutil.copy2(f'./{zipName}', sync_folder)
        # check if the file was successfully copied
        if (bool(os.path.isfile(b))):
            # if file was successfully moved, delete the compressed on the datastore directory
            print('SUCCESS, the file was successfully copied!')
            
            print('deleting compressed file in working dir')
            os.remove(f'./{zipName}')
        else:
            print('ERROR, compressed file not found!')
    else:
        print('ERROR, zipfile not found!')


def main():
    check_config_file()



if __name__=="__main__":
    main()
