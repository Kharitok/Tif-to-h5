"""

Convert  .tif32 files to .h5.
Can add adittional atributes from .txt files.

.tif32 and .txt should have corresponding and statdard format names :

av{averaging number}_seq{sequence number}_{aperture sizze}_-{id}.tif32

and 

av{averaging number}_seq{sequence number}Anytext.txt


for example:

av100_seq7_5mm_-2299.tif32
av100_seq7_Aberrations.txt

to use script 

type Python Converter.py path_to_folder_or_file

where path_to_folder_or_file can be path to folder containing files or certain file especially
"""



# pip install  numpy --upgrade


import argparse
import h5py
from tifffile import imread
import re
import os
import sys


class Data_description():

    def __init__(self, dat_file, meta_file):
        self.dat_file = dat_file
        self.meta_file = meta_file
        self.Init_array(self.dat_file.name+'.'+self.dat_file.ext)
        self.Init_meta(self.meta_file.name+'.'+self.meta_file.ext)
        self.filename = dat_file.name

    def Init_array(self, file_):
        # print(file_)
        self.array = imread(file_)

    def Init_meta(self, file_):
        # print('file_')
        self.Zern, self.Ext = dicter(file_)

    def save(self):
        with h5py.File(self.filename+'.h5', 'w') as f:
            dset = f.create_dataset(self.filename, data=self.array)

            f.attrs['id'] = self.dat_file.id
            f.attrs['averaging number'] = self.dat_file.av_number
            f.attrs['sequence number'] = self.dat_file.seq_number
            f.attrs['aperture size'] = self.dat_file.ap_size
            f.attrs['name'] = self.filename

            for i in self.Zern:
                dset.attrs[i] = self.Zern[i]
            for i in self.Ext:
                dset.attrs[i] = self.Ext[i]


def dicter(file_):
    with open(file_) as f:
        data = f.readlines()

        strings_1 = [data[i] for i in range(data.index('Zernike-Aberrations [mm]:\n')+1,
                                            data.index('Extended Coefficients [mm]:\n'))]
        strings_1 = list(filter(lambda x: x != '\n', strings_1))
        strings_2 = [data[i] for i in range(data.index('Coefficient Value\n')+1,
                                            len(data))]

        strings_1 = list(filter(lambda x: x != '\n', strings_1))
        strings_2 = list(filter(lambda x: x != '\n', strings_2))

        Zern_l_1 = [re.search(r'\S(\S|\s)+?\s\s', st).group()
                    for st in strings_1]
        Zern_l_2 = [float(re.search(r'-?\d+\.\d+', st).group())
                    for st in strings_1]
        ext_l_1 = [re.search(r'\[.+\]', st).group() for st in strings_2]
        ext_l_2 = [float(re.search(r'-?\d+\.\d+', st).group())
                   for st in strings_2]
        Ext = dict(zip(ext_l_1, ext_l_2))
        Zern = dict(zip(Zern_l_1, Zern_l_2))
        return(Zern, Ext)


class File_obj():
    def __init__(self, name):

        ret = NameParser(name)
        if ret[1] != 1:

            self.ext = ret[0]['ext']
            self.name = ret[0]['file_name']
            if self.ext == 'txt':
                self.av_number = ret[0]['av_number']
                self.seq_number = ret[0]['seq_number']
            elif self.ext == 'tif32':
                self.av_number = ret[0]['av_number']
                self.seq_number = ret[0]['seq_number']
                self.ap_size = ret[0]['ap_size']
                self.id = ret[0]['id']
            else:
                raise(ValueError('wrong type of file'))

        else:
            raise(ValueError(ret[2]))

    def __str__(self):
        return(self.name+'.'+self.ext)

    def __repr__(self):
        return(self.name+'.'+self.ext)


def NameParser(name):
    atr = dict()
    err_t = None
    is_error = 0
    try:
        atr['ext'] = re.search(r'\.[\S]+', name).group()[1:]
    except AttributeError:
        is_error = 1
        err_t = ("file extension  not found")
    atr['file_name'] = name[: -(len(atr['ext'])+1)]
    if atr['ext'] == 'tif32':
        try:
            atr['av_number'] = int(re.search(r'av\d+', name).group()[2:])
        except AttributeError:
            is_error = 1
            err_t = ("averafing number  not found")
        try:
            atr['seq_number'] = int(re.search(r'seq\d+', name).group()[3:])
        except AttributeError:
            is_error = 1
            err_t = ("sequence number not found")

        try:
            atr['ap_size'] = re.search(r'_\d+\S+_', name).group()[1:-1]
        except AttributeError:
            is_error = 1
            err_t = ("aperture size  not found")

        try:
            atr['id'] = int(re.search(r'\d+\.', name).group()[:-1])
        except AttributeError:
            is_error = 1
            err_t = ("id  not found")

    else:

        try:
            atr['av_number'] = int(re.search(r'av\d+', name).group()[2:])
        except AttributeError:
            is_error = 1
            err_t = ("averafing number  not found")
        try:
            atr['seq_number'] = int(re.search(r'seq\d+', name).group()[3:])
        except AttributeError:
            is_error = 1
            err_t = ("sequence number not found")

    return ((atr, is_error, err_t))


def Create_file_obj_list(full_path):

    if not os.path.isdir(full_path):

        name = os.path.split(full_path)[1]
        path = os.path.split(full_path)[0]
        all_files = [f for f in os.listdir(path) if os.path.isfile(f)]

        meta_objs = []
        data_objs = []
        pairs = []

        try:
            f_obj = File_obj(name)
        except ValueError:
            raise ValueError("Wrong type of file or name")
            return

        for file in all_files:
            try:
                f = File_obj(file)
                if f.ext == 'txt':
                    meta_objs.append(f)
                elif f.ext == 'tif32':
                    err = 0
                    data_objs.append(f)

            except ValueError:
                pass
        if err == 1:
            raise ValueError("folder don't containd data files")
            return

        if f_obj.ext == 'txt':
            data_exist = 0
            for data in data_objs:
                if ((data.av_number == f_obj.av_number)and
                        (data.seq_number == f_obj.seq_number)):
                    pairs.append((data, f_obj))
                    data_exist = 1
                    break
            if data_exist == 0:
                raise ValueError("coresponding datafile not found")
                return
        elif f_obj.ext == 'tif32':
            meta_exist = 0
            for meta in meta_objs:
                if ((f_obj.av_number == meta.av_number)and
                        (f_obj.seq_number == meta.seq_number)):
                    pairs.append((f_obj, meta))
                    meta_exist = 1
                    break
            if meta_exist != 1:
                pairs.append((f_obj, None))

        return pairs

    else:
        all_files = [f for f in os.listdir(full_path) if os.path.isfile(f)]
        meta_objs = []
        data_objs = []
        pairs = []
        err = 1

        for file in all_files:
            try:
                f = File_obj(file)
                if f.ext == 'txt':
                    meta_objs.append(f)
                elif f.ext == 'tif32':
                    err = 0
                    data_objs.append(f)

            except ValueError:
                pass
        if err == 1:
            raise ValueError("folder don't containd data files")
            return

        for data in data_objs:
            pair_exist = 0
            for meta in meta_objs:
                if ((data.av_number == meta.av_number)
                        and(data.seq_number == meta.seq_number)):
                    pairs.append((data, meta))

                    meta_objs.remove(meta)
                    pair_exist = 1
            if pair_exist != 1:
                pairs.append((data, None))
                data_objs.remove(data)

    return pairs


def conv(path):
    pairs = Create_file_obj_list(path)
    dat = []
    for pair in pairs:
        dat.append(Data_description(pair[0], pair[1]))
    for da in dat:
        da.save()
    print(f'{len(pairs)} files converted ')


if __name__ == "__main__":



    parser = argparse.ArgumentParser(description='Convert tiff32 to h5 and add metainformation from corresponding txt',
                                    #usage='Any text you want\n',
                                    formatter_class = argparse.RawTextHelpFormatter,
                                    epilog=""".tif32 and .txt should have corresponding and statdard format names:

    av{averaging number}_seq{sequence number}_{aperture sizze}_-{id}.tif32
and
    av{averaging number}_seq{sequence number}Anytext.txt

for example:
    av100_seq7_5mm_-2299.tif32
    av100_seq7_Aberrations.txt
""")

    parser.add_argument('Path', metavar='Path', type=str,help='Path to folder or file to  be converted')
    args = parser.parse_args()    
    conv(args.Path)
