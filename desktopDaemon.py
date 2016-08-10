#!/usr/bin/python3
import socket
from evdev import UInput, ecodes as e
from time import sleep

def readData(readerIP, readerPort):
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.SOL_TCP)
		s.connect((readerIP, readerPort))
	except:
		raise Exception('NetworkError: Socket creation failed.')

	#print("Sending Read request.")
	cmd = bytearray([10, 255, 2, 128, 117])
	s.send(cmd)

	# Reading response
	out = s.recv(2048)
	cnt = out[5]
	#print("Response: " + " ".join("%02x" % b for b in out))

	#print("Sending get tag data request.")
	cmd = bytearray([10, 255, 3, 65, 16, 163])
	s.send(cmd)

	# Reading response
	out = s.recv(2048)

	#print("Response: " + " ".join("%02x" % b for b in out))

	
	tagCount = out[4]

	if tagCount == 0:
		raise Exception("WARNING: No tags in range!!!")

	out = out[6:]
	tagArray = []
	patron = ''

	for i in range(tagCount):
		out = out[1:]
		data = out[:12][::-1]
		out = out[13:]
		if data[1] == 0x9e:
			raise Exception("WARNING: Attempted to read empty tag.")
		if data[0] == 0x01:
			data = data.decode()
			patron = ''.join([c if ord(c) != 0 else '' for c in data[1:]])
		else:
			data = data.decode()
			data = ''.join([c if ord(c) != 0 else '' for c in data])
			tagArray += [data]

	return {'patron':patron, 'books':tagArray}

	

if __name__ == '__main__':

	readerIP = "192.168.240.131"
	readerPort = 100

	rfid_data = readData(readerIP, readerPort)
	print(rfid_data)

	books = rfid_data['books']
	patron = rfid_data['patron']
	ui = UInput()

	#Alt-tabing, for testing purpose only
	ui.write(e.EV_KEY, e.ecodes['KEY_LEFTALT'], 1)  # KEY down
	ui.write(e.EV_KEY, e.ecodes['KEY_TAB'], 1)  # KEY down
	ui.write(e.EV_KEY, e.ecodes['KEY_TAB'], 0)  # KEY up
	ui.write(e.EV_KEY, e.ecodes['KEY_LEFTALT'], 0)  # KEY up

	ui.syn()
	sleep(.5)

	#sending patronid 
	keyboard_events = [e.ecodes['KEY_' + i.upper()] for i in patron]

	for key in keyboard_events:
		ui.write(e.EV_KEY, key, 1)  # KEY down
		ui.write(e.EV_KEY, key, 0)  # KEY up
	
	ui.write(e.EV_KEY, e.ecodes['KEY_ENTER'], 1)  # KEY down
	ui.write(e.EV_KEY, e.ecodes['KEY_ENTER'], 0)  # KEY up
	ui.syn()

	sleep(.5)

	for book in books:
		keyboard_events = [e.ecodes['KEY_' + i.upper()] for i in book]
		for key in keyboard_events:
			ui.write(e.EV_KEY, key, 1)  # KEY down
			ui.write(e.EV_KEY, key, 0)  # KEY up
		ui.write(e.EV_KEY, e.ecodes['KEY_ENTER'], 1)  # KEY down
		ui.write(e.EV_KEY, e.ecodes['KEY_ENTER'], 0)  # KEY up
		ui.syn()
		sleep(.5)


	ui.close()