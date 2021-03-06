import os, sys
import zipfile
import time
from datetime import datetime
import glob
import configparser
import shutil # copy file
import logging # logging
import t_notif as tn

"""
 TODO:
 1. Make a log file | in progress > move log file to sync folder, check the old one, if it is there, then delete it, copy the new one
 2. Move compressed file to the sync folder | completed
 3. (optional) create a notification 
 4. compress latest file only
"""

if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app 
    # path into variable _MEIPASS'.
    # application_path = sys._MEIPASS
    application_path = os.path.dirname(sys.executable)
    print('run as exe')
else:
    print('run as py script')
    application_path = os.path.dirname(os.path.abspath(__file__))


def finish():
    return
    # input("you can press any key to close this window!")

def t_messages(back_file, final_zip):
    id = read_config_file('t_notif','s_id')
    t_token = read_config_file('t_notif','t_token')
    t_ch_id = read_config_file('t_notif','t_ch_id')
    message = f"Message from {id}\nThe backup was completed.\nHere is the detail.\nBackup file {back_file} compressed as {final_zip}.\n\nPlease check at your storage!"

    tn.notify_ending(application_path, message, t_token, t_ch_id)

    finish()

def validate_config():
    config = configparser.ConfigParser()
    path_config = os.path.join(application_path, 'config.ini')
    print(path_config)
    config.read(path_config)

    # print(config.items('user_info'))
    # max err_conf rn is 2, it is depend on items in config file, hardcoded anyway :(
    err_conf = 0
    sync_folder_exist = 0
    print(config.items())
    for (each_key, each_val) in config.items("user_info"):
        # print(each_val)
        if (each_key == 'sync_dir'):
            if bool(os.path.isdir(each_val)):
                log_txt = f'directory {each_val} is present' 
                # print(log_txt)
                log_insert('.//files.log', log_txt, logging.INFO)
                sync_folder_exist = 1
            else:
                log_txt = f'no such file or directory: {each_val}' 
                # print(log_txt)
                log_insert('.//files.log', log_txt, logging.ERROR)
                err_conf += 1
        else:
            if bool(os.path.isdir(each_val)):
                log_txt = f'directory {each_val} is present' 
                # print(log_txt)
                log_insert('.//files.log', log_txt, logging.INFO)
            else:
                log_txt = f'no such file or directory: {each_val}' 
                # print(log_txt)
                log_insert('.//files.log', log_txt, logging.ERROR)
                err_conf += 1

    # check folder sync. i doing this if the error dir is not the sync dir, log file will be copied anyway.
    # if the sync dir is not persist/error exit will be the way, please check your config file

    if err_conf != 0:
        # sync folder doest not exist, write error log and exit
        if sync_folder_exist == 0:
            log_txt = 'config file error, please check config file. make sure the directory exist!'
            # print(log_txt)
            log_insert('.//files.log', log_txt, logging.ERROR)
            exit()
        # sync folder exist, write the error log and copy to the sync dir
        else:
            log_txt = 'config file error, please check config file. make sure the directory exist!'
            # print(log_txt)
            log_insert('.//files.log', log_txt, logging.ERROR)
            copy_log_file('.//files.log')
            exit()

    return

def log_insert(file, message, level):
    print(message)
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

def copy_log_file(file):
    # copy log file to sync folder
    # first check if existing log file is there, if exist then delete it, copy the new one. if not exist, copy the new one
    sync_folder = read_config_file('user_info','sync_dir')
    log_path_sync = sync_folder + '/' + file
    if (bool(os.path.isfile(log_path_sync))):
        # remove the old log
        os.remove(log_path_sync)

        # copy the new one
        b = shutil.copy2(file, sync_folder)
        if (bool(os.path.isfile(b))):
            log_txt = 'files log was successfully copied'
            log_insert('.//files.log', log_txt, logging.INFO)
        else:
            log_txt = 'can not copy the files log!'
            log_insert('.//files.log', log_txt, logging.ERROR)
    else:
        b = shutil.copy2(file, sync_folder)
        if (bool(os.path.isfile(b))):
            log_txt = 'files log was successfully copied'
            log_insert('.//files.log', log_txt, logging.INFO)
        else:
            log_txt = 'can not copy the files log!'
            log_insert('.//files.log', log_txt, logging.ERROR)

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
            log_txt = f'compressing {file}' 
            # print(log_txt)
            log_insert('.//files.log', log_txt, logging.INFO)
            zipF.write(file, compress_type=zipfile.ZIP_LZMA)
            i += 1
        zipF.close()
    # update two last files txt
    replace_tlf_log(files)

    # move final backup to sync folder
    move_final_to_sync(zipName)

    log_txt = 'compress and archiving complete!'
    log_insert('.//files.log', log_txt, logging.INFO)

    log_txt = 'copy files log to sync folder'
    log_insert('.//files.log', log_txt, logging.INFO)

    copy_log_file('.//files.log')

    # get value of t notif
    val = read_config_file('t_notif','v')
    if (val == 'True'):
        t_messages(files, zipName)

    finish()

# def move_file_to_sync(file_name):
#     # get sync path from config file
#     sync_path = read_config_file('sync')

#     if ()

# def check_compressed_file(file):
#     comp_file = 

def read_tlf_old():
    tlf_old = []
    with open('.//two_latest_files.txt') as file:
        tlf_old = [line.strip() for line in file]
    return tlf_old

def tlf_logs(tlf_new):
    # check if files are already compressed before, if files have been compressed, there is no need to compress again.
    log_txt = f'new tlf are: {tlf_new}'
    log_insert('.//files.log', log_txt, logging.INFO)
    if (os.path.isfile('.//two_latest_files.txt')):
        log_txt = 'replace tlf txt'
        log_insert('.//files.log', log_txt, logging.INFO)
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
            log_txt = 'one of the file is already compressed, please check it'
            log_insert('.//files.log', log_txt, logging.WARNING)
            copy_log_file('.//files.log')

            return 0 # return false, or finish the program
        else:
            # no same string

            return 1 # return true

    else:
        log_txt = 'create new tlf txt'
        log_insert('.//files.log', log_txt, logging.INFO)
        # no exact file, create it
        # and do archiving and compressing
        tlf_cr = open('.//two_latest_files.txt', 'w+')
        for i in tlf_new:
            tlf_cr.write(i)
            tlf_cr.write('\n')
        tlf_cr.close()

        return 1 # return true

def replace_tlf_log(tlf_new):
    log_txt = 'replacing two latest files txt'
    log_insert('.//files.log', log_txt, logging.INFO)
    tlf_old = read_tlf_old()
    # Read in the file
    with open('.//two_latest_files.txt', 'r') as file :
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
    with open('.//two_latest_files.txt', 'w') as file:
        file.write(filedata)

    log_txt = 'replacing complete'
    log_insert('.//files.log', log_txt, logging.INFO)
    return 1 # no validation :)))))

def check_latest_files():
    # files = os.listdir(rootDir)
    # print(files)
    db_dir = read_config_file('user_info','dir')
    curr_date = get_time()
    #testing
    # curr_date = "backup-20211116"
    log_txt = curr_date
    log_insert('.//files.log', log_txt, logging.INFO)
    print('\ncari file latest:')
    files =  sorted(glob.glob(db_dir + '/' + curr_date + '-*'), key=os.path.getmtime)

    if not files:
        log_txt = 'there is no backup file today!'
        log_insert('.//files.log', log_txt, logging.WARNING)
        copy_log_file('.//files.log')

        finish()
    else:
        #append two last elemets
        two_latest_files = []
        two_latest_files.append(files[-1])
        # two_latest_files.append(files[-2])

        # check if the tlf log has been created, if not, create it. 
        # if yes then compare it with the latest ltf, if same do not do the archive and compress, if not replace the current content and continue the program
        bool_latest_files = tlf_logs(two_latest_files)
        if (bool(bool_latest_files)):
            # continue to archive and compress
            log_txt = '\ntwo latest files are:'
            log_insert('.//files.log', log_txt, logging.INFO)
            for i in two_latest_files:
                print(i)
                log_insert('.//files.log', i, logging.INFO)
            # print(two_latest_files)
            # print(files)
            # print('mamang')
            compress(two_latest_files)
        else:
            # end. the compressed file with same backup file already created
            finish()

def check_config_file():
    # This will check if there is a config file or not. If there is no config file, it will generate it.
    if (os.path.isfile('.//config.ini')):
        log_txt = 'config file already exist! continue'
        log_insert('.//files.log', log_txt, logging.INFO)

        # continue to check latest file
        validate_config()
        check_latest_files()
    else:
        # generate a config file
        log_txt = 'config file not found. Program will generate needed files'
        log_insert('.//files.log', log_txt, logging.INFO)
        log_txt = 'generate config file'
        log_insert('.//files.log', log_txt, logging.INFO)
        # initialize config parser
        config = configparser.ConfigParser()

        # get input from user
        input_db_dir = input('Plese input path to Datastore folder : \n')
        input_sync_dir = input('Plese input path to Sync folder : \n')

        # setup config file
        config.add_section('user_info')
        config.set('user_info', 'dir', input_db_dir)
        config.set('user_info', 'sync_dir', input_sync_dir)

        # setup for telegram notification too
        config.add_section('t_notif')
        config.set('t_notif', 'v', '0')
        config.set('t_notif', 't_token', '')
        config.set('t_notif', 't_ch_id', '')

        # Write the new structure to the new file
        with open(r".//config.ini", 'w') as configfile:
            config.write(configfile)

        if (os.path.isfile('.//config.ini')):
            log_txt = 'config file successfully generated!\n'
            log_insert('.//files.log', log_txt, logging.INFO)

            # continue to check latest file
            check_latest_files()
        else:
            log_txt = 'error when generate config file!\n'
            log_insert('.//files.log', log_txt, logging.ERROR)
            copy_log_file('.//files.log')
            exit()

def read_config_file(section, item):
    # this line is for read configuration file. Please set your db toko root dir on the config.ini file.
    config = configparser.ConfigParser()
    path_config = os.path.join(application_path, 'config.ini')
    # print(repr(path_config))
    config.read(path_config)
    if (section == 'user_info'):
        user_info = config[section]
        user_config = user_info[item]
        return user_config
    elif (section == 't_notif'):
        t_info = config[section]
        t_info_conf = t_info[item]
        return t_info_conf
    else:
        log_txt = "no such section and item on config file"
        log_insert('.//files.log', log_txt, logging.ERROR)
        exit()

def move_final_to_sync(zipName):
    # check zip files if there a
    if (os.path.isfile(f'.//{zipName}')):
        # copy zip file to sync folder
        sync_folder = read_config_file('user_info','sync_dir')
        b = shutil.copy2(f'.//{zipName}', sync_folder)
        # check if the file was successfully copied
        if (bool(os.path.isfile(b))):
            # if file was successfully moved, delete the compressed on the datastore directory
            log_txt = 'the file was successfully copied!'
            log_insert('.//files.log', log_txt, logging.INFO)
            
            log_txt = 'deleting compressed file in working dir'
            log_insert('.//files.log', log_txt, logging.INFO)
            os.remove(f'.//{zipName}')
        else:
            log_txt = 'compressed file not copied!'
            log_insert('.//files.log', log_txt, logging.ERROR)
            copy_log_file('.//files.log')
            exit()
    else:
        log_txt = 'zipfile not found!'
        log_insert('.//files.log', log_txt, logging.ERROR)
        copy_log_file('.//files.log')
        exit()


def main():
    # validate_config()
    check_config_file()



if __name__=="__main__":
    main()
# try:
#     main()
# except Exception as e:
#     logging.exception("Unexpected exception! %s",e)