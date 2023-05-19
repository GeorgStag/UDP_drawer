import matplotlib.pyplot as plt
import socket
import os
os.environ['KIVY_IMAGE'] = 'pil'
import sys
if hasattr(sys, '_MEIPASS'):
    os.environ['KIVY_NO_CONSOLELOG'] = '1'

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup

from kivy.config import Config
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '300')
Config.write()


class GameScreen(GridLayout):

	def __init__(self, **kwargs):
		super(GameScreen, self).__init__(**kwargs)
		plt.figure()
		plt.close()

		self.cols = 2

		self.message_check = "not q, space or empty"

		self.sent = {"x":[], "y":[]}
		self.corr = {"x":[], "y":[]}
		self.mot = {"x":[], "y":[]}

		self.fig = None
		self.ax= None
		self.col = ['black', 'blue', 'green']
		self.labels = ['point1', 'point2', 'point3']

		self.UDPServerSocket = None
		self.ip = "0.0.0.0"
		self.port = 8000
		self.bufferSize = 1024

		self.add_widget(Label(text='Set your ip and port'))
		self.ipportkey = TextInput(text="127.0.0.1:8000", multiline=False)
		self.add_widget(self.ipportkey)

		self.add_widget(Label(text='Choose the update time in seconds'))
		self.render = TextInput(text="1", multiline=False)
		self.add_widget(self.render)

		self.start_button = Button(text='Start', font_size=32, background_color = "lightgreen")
		self.start_button.bind(on_press=self.start)
		self.add_widget(self.start_button)

		self.cancel_button = Button(text='Exit', font_size=32, background_color = "red")
		self.cancel_button.bind(on_press=self.cancel)
		self.add_widget(self.cancel_button)

		self.add_widget(Label(text=''))

		self.info_button = Button(text='Info', font_size=32, background_color = "grey")
		self.info_button.bind(on_press=self.info_popup)
		self.add_widget(self.info_button)


	def start(self, instance):
		address = self.ipportkey.text.split(":")
		self.ip = address[0]
		self.port = int(address[1])
		self.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
		self.UDPServerSocket.bind((self.ip, self.port))
		print("UDP server up and listening \n")
		self.message_check = "not null"
		self.fig, self.ax = plt.subplots()
		self.ax.set(xlim=(-100, 100), ylim=(-100, 100))
		while  (self.message_check != "") and (self.message_check != " "):
			message, address = self.UDPServerSocket.recvfrom(self.bufferSize)
			message = message.decode()
			print("Message from Client:{}".format(message))
			print("Client IP Address:{}".format(address))
			print(' ')
			points = (message[1:-1]).split("],[")
			temp = points[0].split(',')
			self.sent["x"].append(float(temp[0]))
			self.sent["y"].append(float(temp[1]))
			temp = points[1].split(',')
			self.corr["x"].append(float(temp[0]))
			self.corr["y"].append(float(temp[1]))
			temp = points[2].split(',')
			self.mot["x"].append(float(temp[0]))
			self.mot["y"].append(float(temp[1]))
			self.update_plot(instance)
			plt.savefig("last.png")
		self.UDPServerSocket.close()
		plt.close()
		return 0

	def cancel(self, instance):
		App.get_running_app().stop()

	def update_plot(self, instance):
		self.ax.clear()
		#self.ax.set(xlim=(-100, 100), ylim=(-100, 100))
		self.ax.set(xlabel='x', ylabel='y', title='Points from listener')
		ind = 0
		for i in [self.sent,self.corr,self.mot]:
			x = i["x"]
			y = i["y"]
			self.ax.scatter(x, y, label = self.labels[ind], color = self.col[ind])
			ind = ind + 1
		plt.legend(loc="lower right")
		plt.draw()
		timeout = float(self.render.text)
		plt.pause(timeout)

	def info_popup(self, instance):
		info = '''- Send packets to the declared UDP \n- Your message should be in format "[x,y],[x,y],[x,y]" \n- The plot will start printing after pressing the "Start" button! \n- Press escape to return to main panel'''
		popup = Popup(title='Info', content=Label(text=info),  auto_dismiss=True)
		popup.open()


class Carte_Track(App):
	def build(self):
		return GameScreen()

if __name__ == '__main__':
	Carte_Track().run()