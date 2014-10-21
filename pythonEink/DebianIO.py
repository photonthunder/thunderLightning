#!/usr/bin/env python3

import os.path
from time import sleep

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

class Port():
	def __init__(self, pin, digitalMode="in", arduino=False):
		if arduino:
			self.kernel_id=pin2kid[arduinoDigitalPins[pin]]
		else:
			self.kernel_id=pin2kid[pin]
		# print("kernel ID = {}".format(self.kernel_id))
		self.portPath="/sys/class/gpio/"
		self.ioPath="/sys/class/gpio/pio{}".format(kid2pin[self.kernel_id])
		self.export()
		self.direction(digitalMode.lower())

	def __enter__(self):
		return self

	def export(self):
		if not os.path.exists(self.ioPath):
			with open(self.portPath+'/export','w') as f:
				f.write(str(self.kernel_id))

	def unexport(self):
		if os.path.exists(self.ioPath):
			with open(self.portPath+'/unexport','w') as f:
				f.write(str(self.kernel_id))

	def direction(self, direct):
		if os.path.exists(self.ioPath):
			with open(self.ioPath + '/direction','w') as f:
				f.write(direct)

	def setValue(self, value):
		if os.path.exists(self.ioPath):
			with open(self.ioPath + '/value','w') as f:
				f.write(str(value))

	def high(self):
		self.setValue(1)
		
	def low(self):
		self.setValue(0)

	def getValue(self):
		if os.path.exists(self.ioPath):
			with open(self.ioPath + '/value','r') as f:
				a=f.read()
				return int(a)

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.unexport()



# period and dutyCycle in nanoseconds
class PWM():
	def __init__(self, period, dutyCycle, pwmNum = 0):
		self.pwmNum = pwmNum
		self.portPath="/sys/class/pwm/pwmchip" + str(pwmNum)
		self.ioPath=self.portPath+"/pwm"+str(pwmNum)
		self.export()
		self.period(period)
		self.dutyCycle(dutyCycle)

	def __enter__(self):
		self.enable()

	def export(self):
		if not os.path.exists(self.ioPath):
			with open(self.portPath+"/export",'w') as f:
				f.write(str(self.pwmNum))

	def unexport(self):
		if os.path.exists(self.ioPath):
			with open(self.portPath+"/unexport",'w') as f:
				f.write(str(self.pwmNum))

	def period(self, value):
		if os.path.exists(self.ioPath):
			with open(self.ioPath + '/period','w') as f:
				f.write(str(value))

	def dutyCycle(self, value):
		if os.path.exists(self.ioPath):
			with open(self.ioPath + '/duty_cycle','w') as f:
				f.write(str(value))

	def enable(self):
		if os.path.exists(self.ioPath):
			with open(self.ioPath + '/enable','w') as f:
				f.write(str(1))

	def disable(self):
		if os.path.exists(self.ioPath):
			with open(self.ioPath + '/enable','w') as f:
				f.write(str(0))

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.disable()
		self.unexport()




if __name__ == '__main__':
	with Port('8', digitalMode="out", arduino=True) as EPD_CS, PWM(5000, 2500) as PWM0:
		while(1):
			EPD_CS.high()
			sleep(0.01)
			EPD_CS.low()
			sleep(0.01)


