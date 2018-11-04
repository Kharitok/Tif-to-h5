pip install  numpy --update
from matplotlib.colors import LogNorm
import h5py
from tifffile import imread
import re
im = imread('av100_seq5_8p8mm_-2299.tif32')

def tiffread(file_):
	return imread('av100_seq5_8p8mm_-2299.tif32')


class Data_description():


	def __init__(self,filename):
		self.Init_array(filename +'.tif32')
		self.Init_meta(filename +'.txt')
		self.filename = filename

	def Init_array(self,file_):
		self.array = imread(file_)
	
	def Init_meta(self,file_):
		self.Zern,self.Ext = dicter(file_)
	
	def save(self):
		with h5py.File(self.filename+'.h5', 'w') as f:
			dset = f.create_dataset(self.filename,data = self.array)
			for i in self.Zern:
				dset.attrs[i] = self.Zern[i]
			for i in self.Ext:
				dset.attrs[i] = self.Ext[i]

def dicter(file_):
	with open(file_) as f:
		data = f.readlines()
		
		strings_1 = [data[i] for i in range (data.index('Zernike-Aberrations [mm]:\n')+1,
		data.index('Extended Coefficients [mm]:\n'))]
		strings_1 = list(filter(lambda x:x!='\n',strings_1))
		strings_2 = [data[i] for i in range (data.index('Coefficient Value\n')+1,
		len(data))]

		strings_1 = list(filter(lambda x:x!='\n',strings_1))
		strings_2 = list(filter(lambda x:x!='\n',strings_2))


		ext_l_1 = [re.search(r'\S(\S|\s)+?\s\s',st).group() for st in strings_1]
		ext_l_2 = [float(re.search(r'-?\d+\.\d+',st).group()) for st in strings_1]
		Zern_l_1 = [re.search(r'\[.+\]',st).group() for st in strings_2]
		Zern_l_2 = [float(re.search(r'-?\d+\.\d+',st).group()) for st in strings_2]
		Ext = dict(zip(ext_l_1,ext_l_2))
		Zern = dict(zip(Zern_l_1,Zern_l_2))
		return((Zern,ext))

		



