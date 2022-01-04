from model import modelo
from view import vista


#import numpy as np

class controlador():

    def __init__(self):
        self.cModel = modelo(self)
        self.cVista = vista(self)
        
    # def msgOK(self):
    #     print('esta todo KO')
    #     self.cVista.main()
    #     self.cModel.main()
