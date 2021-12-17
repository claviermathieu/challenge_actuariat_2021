import numpy as np
import pandas as pd
import glob


def ind_file_start(my_list, substring = str, start_pos = None, end_pos = None):
    bool_list = []
    for e in my_list:
        bool_list.append(e.startswith(substring, start_pos, end_pos))
    if sum(bool_list) == 0:
        print('Aucun fichier commence par le nom spécifié.')
    elif sum(bool_list) != 1:
        print('Plusieurs fichiers commencent par le nom spécifié.')
    else:
        return(np.where(bool_list)[0][0])



def folders_available(path_r):
    """
    Get root data folder
    * Parameters:
        - path_r : path of the data root folder
    * Return:
        - List of folder_available (one folder per date) in the data root folder.
    """

    folders = glob.glob(path_r + "/*")
    folders = list(map(lambda x : x[len(path_r) + 1:], folders))
    
    return(np.sort(folders))



def file_path(path_r, date_ind = int, file_name = str):
    """
    Get file folder available from specific folder (folders names from folders_available function)
    * Parameters:
        - path_r : path of the data root folder
        - num_folder : index of the selected file from folders list.
    * Return:
        - List of files' path use directly with pd.read_csv() function.
    """
    folders = folders_available(path_r)
    folder_path = path_r + '/' + folders[date_ind] + "/*"
    files = glob.glob(folder_path)
    ind_file = ind_file_start(files, substring = file_name, start_pos = len(folder_path) - 1)
    
    return(files[ind_file])


def read_csv(path = str, decimal = ','):
    print(path)
    return(pd.read_csv(path, sep = ';', decimal = decimal, encoding = 'latin-1'))


