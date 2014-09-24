#!/usr/bin/env python3

import os.path
from time import sleep


serialPorts = {
	'S1' :  '/dev/ttyS1',
	'S2' :  '/dev/ttyS2',
	'S5' :  '/dev/ttyS5',
}

#Pin to Kernel ID table
def toPorts(reg):
	return chr(ord('A') + (reg // 32)) + str(reg % 32)

pin2kid = {toPorts(n) : n for n in range(160)}

kid2pin = {n : toPorts(n) for n in range(160)}

arduinoDigitalPins = {
	'13' :  'C24',
	'12' :  'C22',
	'11' :  'C23',
	'10' :  'C25',
	'9'  :  'C3',
	'8'  :  'C4',
	'7'  :  'C5',
	'6'  :  'C6',
	'5'  :  'C7',
	'4'  :  'C28',
	'3'  :  'C8',
	'2'  :  'C9',
	'1'  :  'C30',
	'0'  :  'C29',
}

arduinoAnalogPins = {
	'A11' :  'D31',
	'A10' :  'C19',
	'A9'  :  'C21',
	'A8'  :  'C20',
	'A7'  :  'D27',
	'A6'  :  'D26',
	'A5'  :  'D25',
	'A4'  :  'D24',
	'A3'  :  'D23',
	'A2'  :  'D22',
	'A1'  :  'D21',
	'A0'  :  'C18',
}

def getPath(kernel_id):
	iopath="/sys/class/gpio/pio{}".format(kid2pin[kernel_id])
	return iopath

def export(kernel_id):
	iopath=getPath(kernel_id)
	if not os.path.exists(iopath): 
		f = open('/sys/class/gpio/export','w')
		f.write(str(kernel_id))
		f.close()

def unexport(kernel_id):
	iopath=getPath(kernel_id)
	if os.path.exists(iopath): 
		f = open('/sys/class/gpio/unexport','w')
		f.write(str(kernel_id))
		f.close()

# out or in
def direction(kernel_id,direct):
	iopath=getPath(kernel_id)
	if os.path.exists(iopath): 
		f = open(iopath + '/direction','w')
		f.write(direct)
		f.close()

# 0 or 1
def set_value(kernel_id,value):
	iopath=getPath(kernel_id)
	if os.path.exists(iopath): 
		f = open(iopath + '/value','w')
		f.write(str(value))
		f.close()

def get_value(kernel_id):
	if kernel_id != -1:
		iopath=getPath(kernel_id)
		if os.path.exists(iopath): 
			f = open(iopath + '/value','r')
			a=f.read()
			f.close()
			return int(a)

class Port():
	def __init__(self, pin, mode):
		self.kernel_id=pin2kid[pin]
		export(self.kernel_id)
		direction(self.kernel_id,mode.lower())

	def high(self):
		set_value(self.kernel_id,1)
		
	def low(self):
		set_value(self.kernel_id,0)

	def get_value(self):
		return get_value(self.kernel_id)

	def unexport(self):
		return unexport(self.kernel_id)


if __name__ == '__main__':
	PA16 = Port('A16', "out")
	while(1):
		PA16.high()
		sleep(1)
		PA16.low()
		sleep(1)


