from PyQt4.QtGui import *
from PyQt4.QtCore import *

class ColorWheelMenuBar( QMenuBar ):
    def __init__(self, parent ):
        super(ColorWheelMenuBar, self).__init__( parent )
        self.parent = parent
        #
        fileMenu = self.addMenu( '&File' )
        saveAction = fileMenu.addAction('&Save CSS' )
        openAction = fileMenu.addAction('&Open CSS' )
        openURLAction = fileMenu.addAction('&Open URL CSS')
        #
        opsMenu = self.addMenu( '&Operations' )
        showExpandedColorSwatchAction = opsMenu.addAction('&Expanded Color Swatch' )
        #
        helpMenu = self.addAction( '&Help' )
