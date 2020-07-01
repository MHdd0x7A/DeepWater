import os

path_iso = './yA31_v02/iso/'
path_vol = './yA31_v02/vol/'

def createFolder(directory):
        try:
            if os.path.exists(directory):
                print('Error' + directory + 'already exit')

            if not os.path.exists(directory):
                os.makedirs(directory)
                print('Successful create' + directory )
        except OSError:
            print("fail os error")

createFolder(path_iso)
createFolder(path_vol)
