from PyQt4.QtGui import *
from PyQt4.QtCore import *

class ColorWheelMenuBar( QMenuBar ):
    def __init__(self, parent ):
        super(ColorWheelMenuBar, self).__init__( parent )
        self.parent = parent

        self.addMenu( QMenu('File', parent) )
        self.addMenu( QMenu('Operations', parent) )
        self.addMenu( QMenu('Help', parent) )

        print 'Hello World'
