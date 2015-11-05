from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys, math

class ColorWheelButtons( QWidget ):
    def __init__(self, parent):
        super(QWidget, self).__init__( parent )
        self.parent = parent
        #        
        # self.setStyleSheet("background-color: ivory;")
        buttonLayout = QGridLayout( )
        self.setLayout( buttonLayout )
        self.scaleButton = QPushButton( "SCALE" )
        self.resetScaleButton = QPushButton( "RESET SCALE" )
        self.recenterLastButton = QPushButton( "RESET LCOLOR" )
        self.normalizeColorValueButton = QPushButton( "NORM CVALUE" )
        for but in ( self.scaleButton, self.resetScaleButton, self.recenterLastButton,
                     self.normalizeColorValueButton ):
            but.setStyleSheet("""
            border-width: 2px;
            border-color: blue;
            border-style: solid;
            border-radius: 7px;
            padding: 3px;
            font-size: 12px;
            font-weight: bold;
            padding-left: 5px;
            padding-right: 5px;
            min-width: 50px;
            min-height: 13px;
            """)
        buttonLayout.addWidget( self.scaleButton, 0, 0, 0, 1 )
        buttonLayout.addWidget( self.resetScaleButton, 0, 1, 1, 1 )
        buttonLayout.addWidget( self.recenterLastButton, 0, 2, 1, 1 )
        buttonLayout.addWidget( self.normalizeColorValueButton, 0, 3, 1, 1)
        #
        ## actions on buttons
        self.scaleButton.clicked.connect( self.rescaleColor )
        self.resetScaleButton.clicked.connect( self.resetScaleColor )
        self.recenterLastButton.clicked.connect( self.recenterLastColor )

    def rescaleColor(self):
        maxSat = max([ s for (h, s, v) in self.parent.hsvs ])
        if maxSat <= 1e-6:
            maxSat = 0.01
        self.parent.cww.rescaleWheel( dmax = maxSat )


    def resetScaleColor( self ):
        self.parent.cww.rescaleWheel( dmax = 1.0 )

    def recenterLastColor( self ):
        self.parent.hsvs[-1] = [ 0.0, 0.0, 1.0 ]
        self.parent.update()

    def paintEvent(self, evt):
        qs = self.size()
        image = QImage( qs.width(), qs.height(), QImage.Format_ARGB32)
        image.fill( QColor( "ivory" ).rgb() )
        painter = QPainter( self )
        painter.setRenderHint( QPainter.Antialiasing )
        painter.drawImage(0, 0, image )
