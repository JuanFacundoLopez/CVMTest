# from GUIvista import iniciarVista
from re import X
from PyQt5.QtGui import QAbstractOpenGLFunctions, QWindow
import numpy as np
from numpy.core.fromnumeric import size
from numpy.lib.function_base import angle, place
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph import PlotWidget, plot
from pyqtgraph.functions import Color, colorStr
from pyqtgraph.graphicsItems.AxisItem import AxisItem
from scipy.fft import fft
import pyqtgraph as pg
from PyQt5.QtWidgets import * 

import struct
import pyaudio
from scipy.fftpack import fft, fftfreq

import sys
import time


class vista(object):

    def __init__(self, Controller):
        super().__init__()
        self.vController = Controller
        self.app = QtGui.QApplication(sys.argv)
        
        self.win = QMainWindow()
        self.win.setWindowTitle("SAMPA ") 
        self.win.setGeometry(50, 50, 1600, 950)
        
        #agregar menues
        self.win.statusBar()
        menubar = self.win.menuBar()
        fileMenu = menubar.addMenu('&Archivos')
        toolMenu = menubar.addMenu('&Herramientas')
        confMenu = menubar.addMenu('&Configuracion')
        viewMenu = menubar.addMenu('&Vista')
        helpMenu = menubar.addMenu('&Ayuda')
        
        # Acciones del menu
        # acciones de archivos
        exitAction = QAction('&Exit', self.win)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.app.quit)
        fileMenu.addAction(exitAction)
        
        # acciones de herramientas
        toolAction = QAction('&Calibracion',self.win)
        toolMenu.addAction(toolAction)

        # acciones de herramientas
        confAction = QAction('&Herramientas',self.win)
        confMenu.addAction(confAction)

        # acciones de herramientas
        viewAction = QAction('&Vistas',self.win)
        viewMenu.addAction(viewAction)       

        # acciones de herramientas
        helpAction = QAction('&Ayuda',self.win)
        helpMenu.addAction(helpAction)  
        
        #agregar grafico
        # creating a widget object
        self.widget = QWidget(self.win)
        
        #agregar botones al costado
        self.btn = QPushButton("Play", self.widget)
        self.btn.setGeometry(50, 200, 100, 30)
        self.btn.clicked.connect(self.dalePlay)

        # se agrega una ventana para graficar 
        self.winGraph = pg.GraphicsWindow(parent=self.widget, title='Spectrum Analyzer')
        self.winGraph.setWindowTitle('Spectrum Analyzer')    
        self.winGraph.setGeometry(250, 10, 1320, 890)
        
        # agrego 'ejes' como objetos. 1- declaro los labels, 2- creo un objeto 'eje', 3- seteo labels, 4- agrego la grilla 
        wf_xlabels = [(0, '0'), (512,'512'), (1024, '1024'), (1536,'1536'), (2048, '2048'), (2560,'2560'),(3072, '3072'), (3584,'3584'), (4096, '4096')]
        wf_xaxis = pg.AxisItem(orientation='bottom')
        wf_xaxis.setTicks([wf_xlabels])
        wf_xaxis.setGrid(100)

        # agrego 'ejes' como objetos. 1- declaro los labels, 2- creo un objeto 'eje', 3- seteo labels, 4- agrego la grilla
        wf_ylabels = [(-1, '-1'), (-0.5,'-0.5'), (0, '0'), (0.5,'0.5'), (1, '1')]
        wf_yaxis = pg.AxisItem(orientation='left')
        wf_yaxis.setTicks([wf_ylabels])
        wf_yaxis.setRange(-1,1)
        wf_yaxis.setGrid(100)

        # agrego 'ejes' como objetos. 1- declaro los labels, 2- creo un objeto 'eje', 3- seteo labels, 4- agrego la grilla
        sp_xlabels = [
            (np.log10(10), '10'), (np.log10(20), '20'),(np.log10(30), '30'),(np.log10(40), '40'),(np.log10(50), '50'),
            (np.log10(60), '60'), (np.log10(70), '70'),(np.log10(80), '80'),(np.log10(90), '90'),(np.log10(100), '100'),
            (np.log10(200), '200'), (np.log10(300), '300'),(np.log10(400), '400'),(np.log10(500), '500'),(np.log10(600), '600'),
            (np.log10(700), '700'), (np.log10(800), '800'),(np.log10(900), '900'),(np.log10(1000), '1000'),(np.log10(2000), '2000'),
            (np.log10(3000), '3000'), (np.log10(4000), '4000'),(np.log10(5000), '5000'),(np.log10(6000), '6000'),(np.log10(7000), '7000'),
            (np.log10(8000), '8000'), (np.log10(9000), '9000'),(np.log10(10000), '10000'),(np.log10(20000), '20000'), (np.log10(22050), '22050'),
        ]
        sp_xaxis = pg.AxisItem(orientation='bottom')
        sp_xaxis.setTicks([sp_xlabels])
        sp_xaxis.setGrid(100)
        
        # agrego 'ejes' como objetos. 1- declaro los labels, 2- creo un objeto 'eje', 3- seteo labels, 4- agrego la grilla
        sp_ylabels = [(np.log10(0.1),'0.1'), (np.log10(1),'1'), (np.log10(10),'10'), (np.log10(100),'100'),
                        (np.log10(1000),'1000'), (np.log10(10000),'10000'), (np.log10(100000),'100000'), (np.log10(1000000),'1000000'),
                        (np.log10(10000000),'10000000')]
        sp_yaxis = pg.AxisItem(orientation='left')
        sp_yaxis.setTicks([sp_ylabels])
        sp_yaxis.setGrid(100)
        sp_yaxis.setLogMode(True)
        
        # Agrego 2 objetos de plot 
        self.waveform = self.winGraph.addPlot(title='Forma de onda', row=0, col=0, axisItems={'bottom': wf_xaxis, 'left': wf_yaxis})
        self.spectrum = self.winGraph.addPlot(title='Espectrograma', row=1, col=0, axisItems={'bottom': sp_xaxis, 'left': sp_yaxis})

        # Agrego 2 graficos y seteo como logaritmicos
        self.wf = self.waveform.plot(pen='c', width=3)
        self.sp = self.spectrum.plot(pen='m', width=3)
        
        self.sp.setLogMode(yMode=True, xMode=True)


        # Agrego 2 labels para mostrar las fundamentales
        self.labFerc = pg.LabelItem(parent=self.spectrum  ,text='Frecuencia fundamental:',colorStr= 'w') # aca esta el label
        self.labFerc.setGeometry(200,120,100,50)
        self.labFercMax = pg.LabelItem(parent=self.spectrum  ,text='Frecuencia max:',colorStr= 'w') # aca esta el label
        self.labFercMax.setGeometry(200,150,100,50)        


        # Seteo los rangos para el grafico del espectro
        self.spectrum.setYRange(np.log10(0.1), np.log10(10000000), padding=0.005)
        self.spectrum.setXRange(np.log10(20), np.log10(22050), padding=0.005)

        
        # Seteo los rangos para el grafico de la forma de onda
        self.waveform.setYRange(-2, 2, padding=0)
        self.waveform.setXRange(0,4096)

        # setting this widget as central widget of the main window
        self.win.setCentralWidget(self.widget)
        self.win.show() 
        
        # pyaudio stuff
        self.FORMAT = pyaudio.paInt16
        self.RATE = 44100
        self.CHUNK = 2048 * 2

        # Declaro el componente x en el espectro
        self.f = np.linspace(0, int(self.RATE/2), int(self.CHUNK/2))

        # Creo el objeto para la captura y emision de audio
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.FORMAT, channels=1, rate=self.RATE, input=True, output=True, frames_per_buffer=self.CHUNK)

    # Funcion del boton. Creo un timer que se ejecuta cada 22 ms
    def dalePlay(self):
        self.frecFundMax=0
        if self.timer.isActive():
            self.timer.stop() 
            self.btn.setText('Play')
        else:
            self.timer.start(22) 
            self.btn.setText('Stop')

    # Funcion que se ejecuta cada 22 ms, toma datos de la placa de sonido y expone en los plots
    def update(self):

        # Forma de onda en el tiempo
        wf_data = self.stream.read(self.CHUNK)
        wf_data = struct.unpack(str(2 * self.CHUNK) + 'B', wf_data)
        wf_data = np.array(wf_data, dtype='b')[::2] 
        time_data = np.linspace(0,self.CHUNK,self.CHUNK)
        self.wf.setData(time_data, (wf_data/128))

        # Espectro
        yf = fft(np.array(wf_data, dtype='int8'))
        yf = np.abs(yf[0:int(self.CHUNK/2)])
        listYf = list(yf)
        self.frecFund = listYf.index(np.max(yf))*int(self.RATE / 2)/int(self.CHUNK / 2)
        self.frecFundMax = self.frecFundMax if self.frecFundMax > self.frecFund else self.frecFund 
        self.labFerc.setText('Frecuencia funcamental:'+ str(int(self.frecFund)))
        self.labFercMax.setText('Frecuencia funcamental:'+ str(int(self.frecFundMax)))
        self.sp.setData(self.f, yf[0:len(yf)])

    def animation(self):
        #el timer se utiliza para automatizar la actualizacion de display
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        
        #inicializa la ventana
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()
        
    