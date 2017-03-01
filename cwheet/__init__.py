import os
from matplotlib import rcParams
from PyQt4.QtGui import QColor
from functools import reduce

rcParams['backend.qt4'] = 'PyQt4'

shufflecolors = [ QColor(val) for val in ( 'red', 'blue', 'green', 'orange', 'magenta', 'black' ) ]

resourcePath = os.path.join( reduce(lambda x,y: os.path.dirname( x ),
                                    [ os.path.abspath(__file__), 1, 2 ] ),
                             'resources' )
