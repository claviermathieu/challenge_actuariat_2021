
## NE PAS OUBLIER DE CHANGER LA LIBRAIRIE LIB.DATA:

import pandas as pd
import glob

PATH_R = "../data/daily_data"


def folders_available(path_r=PATH_R):
    """
    Get root data folder
    * Parameters:
        - path_r : path of the data root folder
    * Return:
        - List of folder_available (one folder per date) in the data root folder.
    """

    folders = glob.glob(path_r + "/*")
    folders = list(map(lambda x: x[len(path_r) + 1:], folders))

    return (folders)


def files_available(path_r=PATH_R, folder_ind=0):
    """
    Get file folder available from specific folder (folders names from folders_available function)
    * Parameters:
        - path_r : path of the data root folder
        - num_folder : index of the selected file from folders list.
    * Return:
        - List of files' path use directly with pd.read_csv() function.
    """
    folders = folders_available(path_r)
    folder_path = path_r + '/' + folders[folder_ind] + "/*"
    files = glob.glob(folder_path)

    return (files)


def read_csv(files, ind_file=0):
    return (pd.read_csv(files[ind_file], sep=';', decimal=',', encoding='latin-1'))