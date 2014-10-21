#!/usr/bin/env python3

from SpiBus import SpiBus
from DebianIO import Port, PWM
from time import sleep
import sys
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

WHITE_ONE = 1
BLACK_ZERO = 0

OLD_IMAGE = 0
COMPENSATE_OLD_IMAGE = 1
WHITE_OLD_IMAGE = 2
INVERSE_NEW_IMAGE = 3
NEW_IMAGE = 4

# Four Basic Liberation Fonts, each having a Bold, Italic, and BoldItalic options
FontPath = "/usr/share/fonts/truetype/liberation/"
FontMono = FontPath + "LiberationMono-Regular.ttf"
FontSans = FontPath + "LiberationSans-Regular.ttf"
FontSansNarrow = FontPath + "LiberationSansNarrow-Regular.ttf"
FontSerif = FontPath + "LiberationSerif-Regular.ttf"

# Set for 2" Board only
# 200 x 96

class EinkDriver():
	def __init__(self):
		self.spi = SpiBus(device="/dev/spidev32765.0", mode='0')
		self.oldPixelImage = Image.new('1', (200, 96), WHITE_ONE).load()

	def spiOn(self):
		self.spi = SpiBus(device="/dev/spidev32765.0", mode='2')
		self.spi.sendByte(0x00)

	def spiOff(self):
		self.spi = SpiBus(device="/dev/spidev32765.0", mode='0')
		self.spi.sendByte(0x00)

	def startUp(self):
		self.spiOff()
		print("Starting up Eink Display")
		self.einkReset = Port('6', digitalMode="out", arduino=True)
		self.einkPanelOn = Port('2', digitalMode="out", arduino=True)
		self.einkDischarge = Port('4', digitalMode="out", arduino=True)
		self.einkBorder = Port('3', digitalMode="out", arduino=True)

		self.einkReset.low()
		self.einkPanelOn.low()
		self.einkDischarge.low()
		self.einkBorder.low()

		self.spiOn()

		# self.einkPWM = PWM(10000, 5000)
		self.einkPWM = PWM(3000, 1500)
		self.einkPWM.enable()
		sleep(0.025)
		self.einkPanelOn.high()
		sleep(0.010)
		self.einkReset.high()
		self.einkBorder.high()
		sleep(0.005)
		self.einkReset.low()
		sleep(0.005)
		self.einkReset.high()
		sleep(0.005)
		print("Waiting for Eink Busy to Clear...", end="")
		sys.stdout.flush()
		self.einkBusy = Port('7', digitalMode="in", arduino=True)
		while (self.einkBusy.getValue() == 1):
			sleep(10E-6)
		print("Done")

		self.spi.sendData(0x70, 0x01)
		self.spi.sendData(0x72, 0x00, 0x00, 0x00, 0x00, 0x01, 0xFF, 0xE0, 0x00)
		self.spi.sendData(0x70, 0x06)
		self.spi.sendData(0x72, 0xFF)
		self.spi.sendData(0x70, 0x07)
		self.spi.sendData(0x72, 0x9D)
		self.spi.sendData(0x70, 0x08)
		self.spi.sendData(0x72, 0x00)
		self.spi.sendData(0x70, 0x09)
		self.spi.sendData(0x72, 0xD0, 0x00)
		self.spi.sendData(0x70, 0x04)
		self.spi.sendData(0x72, 0x03)
		sleep(0.005)
		self.spi.sendData(0x70, 0x03)
		self.spi.sendData(0x72, 0x01)
		self.spi.sendData(0x70, 0x03)
		self.spi.sendData(0x72, 0x00)
		sleep(0.005)
		self.spi.sendData(0x70, 0x05)
		self.spi.sendData(0x72, 0x01)
		sleep(0.03)
		self.einkPWM.disable()
		self.spi.sendData(0x70, 0x05)
		self.spi.sendData(0x72, 0x03)
		sleep(0.03)
		self.spi.sendData(0x70, 0x05)
		self.spi.sendData(0x72, 0x0F)
		sleep(0.03)
		self.spi.sendData(0x70, 0x02)
		self.spi.sendData(0x72, 0x24)

		self.spiOff()
		print("Eink Started")

	def shutdown(self):
		print("Shutting Down Eink")
		self.sendAllNothing()
		self.sendAllDummy()
		sleep(0.025)
		self.einkBorder.low
		sleep(0.3)
		self.einkBorder.high
		self.spiOn()
		self.spi.sendData(0x70, 0x03)
		self.spi.sendData(0x72, 0x01)
		self.spi.sendData(0x70, 0x02)
		self.spi.sendData(0x72, 0x05)
		self.spi.sendData(0x70, 0x05)
		self.spi.sendData(0x72, 0x0E)
		self.spi.sendData(0x70, 0x05)
		self.spi.sendData(0x72, 0x02)
		self.spi.sendData(0x70, 0x04)
		self.spi.sendData(0x72, 0x0C)
		sleep(0.120)
		self.spi.sendData(0x70, 0x05)
		self.spi.sendData(0x72, 0x00)
		self.spi.sendData(0x70, 0x07)
		self.spi.sendData(0x72, 0x0D)
		self.spi.sendData(0x70, 0x04)
		self.spi.sendData(0x72, 0x50)
		sleep(0.04)
		self.spi.sendData(0x70, 0x04)
		self.spi.sendData(0x72, 0xA0)
		sleep(0.04)
		self.spi.sendData(0x70, 0x04)
		self.spi.sendData(0x72, 0x00)
		self.einkReset.low()
		self.einkPanelOn.low()
		self.einkBorder.low()
		self.spiOff()
		self.einkDischarge.high()
		sleep(0.150)
		self.einkDischarge.low()
		print("Eink Shutdown")

	def sendUniformLine(self, line, data, dummy=False):
		self.spi.sendData(0x70, 0x0A)
		count = 0
		self.spi.writeBuffer[count] = 0x72
		# Even row values
		for i in range(25):
			count += 1
			self.spi.writeBuffer[count] = data
		lineNumber = (line) // 4
		lineValue = (0xC0 >> (2 * ((line) % 4)))
		# Scan Lines to write
		for i in range(24):
			if ((dummy == False) and (lineNumber == i)):
				count += 1
				self.spi.writeBuffer[count] = lineValue
			else:
				count += 1
				self.spi.writeBuffer[count] = 0x00
		# Odd row values
		for i in range(25):
			count += 1
			self.spi.writeBuffer[count] = data
		count += 1
		self.spi.writeBuffer[count] = 0x00
		self.spi.send(count + 1)

	def sendAll(self, data, dummy=False):
		self.spiOn()
		for index in range(96):
			# print("Sending line {}".format(index))
			self.spi.sendData(0x70, 0x04)
			self.spi.sendData(0x72, 0x03)
			self.sendUniformLine(index, data)
			self.spi.sendData(0x70, 0x02)
			self.spi.sendData(0x72, 0x2F)
		self.spiOff()

	def sendAllWhite(self):
		# print("Sending All White")
		self.sendAll(0xAA)

	def sendAllBlack(self):
		# print("Sending All Black")
		self.sendAll(0xFF)

	def sendAllNothing(self):
		# print("Sending All Nothing")
		self.sendAll(0x00)

	def sendAllDummy(self):
		# print("Sending All Dummy")
		self.sendAll(0x55, dummy=True)

	def sendPixelImageLine(self, line, myList, stage=NEW_IMAGE):
		self.spi.sendData(0x70, 0x0A)
		count = 0
		self.spi.writeBuffer[count] = 0x72
		# Even row values from max to min
		for i in range(25):
			myValue = 0x00
			for bitIndex in range(4):
				if (myList[200-1-2*4*i-2*bitIndex] == WHITE_ONE):
					if (stage == COMPENSATE_OLD_IMAGE) or (stage == INVERSE_NEW_IMAGE):
						myValue |= 0xC0 >> (2*bitIndex)
					else:
						myValue |= 0x80 >> (2*bitIndex)
				else:
					if (stage == COMPENSATE_OLD_IMAGE):
						myValue |= 0x80 >> (2*bitIndex)
					elif (stage == WHITE_OLD_IMAGE) or (stage == INVERSE_NEW_IMAGE):
						myValue |= 0x00
					else:
						myValue |= 0xC0 >> (2*bitIndex)
			count += 1
			self.spi.writeBuffer[count] = myValue
		lineNumber = (line) // 4
		lineValue = (0xC0 >> (2 * ((line) % 4)))
		# Scan Lines to write
		for i in range(24):
			if (lineNumber == i):
				count += 1
				self.spi.writeBuffer[count] = lineValue
			else:
				count += 1
				self.spi.writeBuffer[count] = 0x00
		# Odd row values from min to max
		for i in range(25):
			myValue = 0
			for bitIndex in range(4):
				if (myList[0+2*4*i+2*bitIndex] == WHITE_ONE):
					if (stage == COMPENSATE_OLD_IMAGE) or (stage == INVERSE_NEW_IMAGE):
						myValue |= 0xC0 >> (2*bitIndex)
					else:
						myValue |= 0x80 >> (2*bitIndex)
				else:
					if (stage == COMPENSATE_OLD_IMAGE):
						myValue |= 0x80 >> (2*bitIndex)
					elif (stage == WHITE_OLD_IMAGE) or (stage == INVERSE_NEW_IMAGE):
						myValue |= 0x00
					else:
						myValue |= 0xC0 >> (2*bitIndex)
			count += 1
			self.spi.writeBuffer[count] = myValue
		count += 1
		self.spi.writeBuffer[count] = 0x00
		self.spi.send(count + 1)

	def sendPixelImage(self, pixelImage, imageStep):
		self.spiOn()
		for row in range(96):
			rowList = []
			self.spi.sendData(0x70, 0x04)
			self.spi.sendData(0x72, 0x03)
			for column in range(200):
				if imageStep <= WHITE_OLD_IMAGE:
					rowList.append(self.oldPixelImage[column, row])
				else:
					rowList.append(pixelImage[column, row])
			self.sendPixelImageLine(row, rowList, imageStep)
			self.spi.sendData(0x70, 0x02)
			self.spi.sendData(0x72, 0x2F)
		self.spiOff()

	def clearImage(self):
		self.oldPixelImage = Image.new('1', (200, 96), WHITE_ONE).load()
		self.sendAllBlack()
		self.sendAllBlack()
		self.sendAllWhite()
		self.sendAllWhite()

	def sendImage(self, newImage):
		self.newPixelImage = newImage.load()
		self.sendPixelImage(self.newPixelImage, COMPENSATE_OLD_IMAGE)
		self.sendPixelImage(self.newPixelImage, WHITE_OLD_IMAGE)
		self.sendPixelImage(self.newPixelImage, INVERSE_NEW_IMAGE)
		self.sendPixelImage(self.newPixelImage, NEW_IMAGE)
		self.oldPixelImage = self.newPixelImage

	def rawImage(self, newImage):
		self.newPixelImage = newImage.load()
		self.sendPixelImage(self.newPixelImage, NEW_IMAGE)
		self.oldPixelImage = self.newPixelImage

	def whiteWipeImage(self, newImage):
		self.newPixelImage = newImage.load()
		self.sendAllWhite()
		self.sendPixelImage(self.newPixelImage, NEW_IMAGE)
		self.oldPixelImage = self.newPixelImage

	def randomDemo(self):
		myImage = Image.new('1', (200, 96), WHITE_ONE)
		draw = ImageDraw.Draw(myImage)
		draw.point((0, 0), fill=BLACK_ZERO)
		draw.point((1, 0), fill=BLACK_ZERO)
		draw.point((0, 1), fill=BLACK_ZERO)
		draw.ellipse((120, 10, 150, 40), fill=BLACK_ZERO, outline=BLACK_ZERO)
		draw.ellipse((120, 60, 170, 90), fill=WHITE_ONE, outline=BLACK_ZERO)
		draw.line([(10,20),(100,20)], fill=BLACK_ZERO)
		draw.line([(10,90),(100,60)], fill=BLACK_ZERO)
		draw.text((30, 30), 'Hello Mark!!!', fill=BLACK_ZERO)
		self.sendImage(myImage)

	def ExplodingBallDemo(self):
		for step in range(0,80,4):
			myImage = Image.new('1', (200, 96), 1)
			draw = ImageDraw.Draw(myImage)
			draw.ellipse((0+step, 0+step, 16+step, 16+step), fill=BLACK_ZERO, outline=BLACK_ZERO)
			self.rawImage(myImage)
		for step in range(0,80,4):
			myImage = Image.new('1', (200, 96), 1)
			draw = ImageDraw.Draw(myImage)
			draw.ellipse((80-step, 80-step, 96+step, 96+step), fill=BLACK_ZERO, outline=BLACK_ZERO)
			self.rawImage(myImage)

	def textDemo(self):
		self.sans16 = ImageFont.truetype(FontSans, 16)
		self.mono12 = ImageFont.truetype(FontMono, 12)
		self.sansNarrow20 = ImageFont.truetype(FontSansNarrow, 20)
		self.serif18 = ImageFont.truetype(FontSerif, 18)
		myImage = Image.new('1', (200, 96), WHITE_ONE)
		draw = ImageDraw.Draw(myImage)
		draw.text((10, 10), 'Font is Default.', fill=BLACK_ZERO)
		draw.text((10, 30), 'Font is Default', fill=BLACK_ZERO)
		draw.text((10, 50), 'Font is Default', fill=BLACK_ZERO)
		draw.text((10, 70), 'Font is Default', fill=BLACK_ZERO)
		self.sendImage(myImage)
		sleep(2)
		myImage = Image.new('1', (200, 96), WHITE_ONE)
		draw = ImageDraw.Draw(myImage)
		draw.text((10, 10), 'Font is Mono 12.', font=self.mono12, fill=BLACK_ZERO)
		draw.text((10, 30), 'Font is Sans 16', font=self.sans16, fill=BLACK_ZERO)
		draw.text((10, 50), 'Font is Serif 18', font = self.serif18, fill=BLACK_ZERO)
		draw.text((10, 70), 'Font is SansNarrow 20', font=self.sansNarrow20, fill=BLACK_ZERO)
		self.sendImage(myImage)

if __name__ == '__main__':
	myEink = EinkDriver()
	myEink.startUp()
	# myEink.sendAllWhite()
	# myEink.sendAllBlack()
	myEink.clearImage()
	myEink.randomDemo()
	sleep(2)
	myEink.ExplodingBallDemo()
	myEink.textDemo()
	myEink.shutdown()


