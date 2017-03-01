from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys, math, numpy
from cwResources import ColorWheelResource

class ColorWheelButtons( QWidget ):
    def __init__(self, parent):
        super(QWidget, self).__init__( parent )
        self.parent = parent
        buttonLayout = QGridLayout( )
        self.setLayout( buttonLayout )
        self.scaleButton = QPushButton( "SCALE" )
        self.resetScaleButton = QPushButton( "RESET SCALE" )
        self.recenterLastButton = QPushButton( "RESET LCOLOR" )
        self.normalizeColorValueButton = QPushButton( "NORM CVALUE" )
        self.turnToLineButton = QPushButton( "TURN TO LINE" )
        cwr = ColorWheelResource()
        for but in ( self.scaleButton, self.resetScaleButton,
                     self.recenterLastButton,
                     self.normalizeColorValueButton,
                     self.turnToLineButton ):
            but.setStyleSheet( cwr.getStyleSheet( 'qpushbutton' ) )
        buttonLayout.addWidget( self.scaleButton, 0, 0, 1, 1 )
        buttonLayout.addWidget( self.resetScaleButton, 0, 1, 1, 1 )
        buttonLayout.addWidget( self.recenterLastButton, 0, 2, 1, 1 )
        buttonLayout.addWidget( self.normalizeColorValueButton, 0, 3, 1, 1)
        buttonLayout.addWidget( self.turnToLineButton, 1, 0, 1, 1 )
        buttonLayout.addWidget( QLabel("UNDER CONSTRUCTION"), 1, 1, 1, 3 )
        #
        ## actions on buttons
        self.scaleButton.clicked.connect( self.rescaleColor )
        self.resetScaleButton.clicked.connect( self.resetScaleColor )
        self.recenterLastButton.clicked.connect( self.recenterLastColor )
        self.normalizeColorValueButton.clicked.connect( self.normCValue )
        self.turnToLineButton.clicked.connect( self.turnToLine )

    def turnToLine( self ):
        # self.parent.cws.setTransform( )
        if len( self.parent.hsvs ) < 2:
            return
        minVal = min([ v for ( h, s, v) in self.parent.hsvs ])
        maxVal = max([ v for ( h, s, v) in self.parent.hsvs ])
        vecX = numpy.sum([ s * math.cos( 2 * math.pi * h ) for
                           ( h, s, v ) in self.parent.hsvs ])
        vecY = numpy.sum([ -s * math.sin( 2 * math.pi * h ) for
                           ( h, s, v ) in self.parent.hsvs ])
        if numpy.allclose([ vecX, vecY ], [ 0.0 ] * 2 ):
            return
        theta = math.atan2( -vecY, vecX )
        if theta < 0:
            theta += 2 * math.pi
        hNew = theta / ( 2 * math.pi )
        minS = min([ s for ( h, s, v) in self.parent.hsvs ])
        maxS = max([ s for ( h, s, v) in self.parent.hsvs ])
        #
        ## now perform the transform
        numPoints = len( self.parent.hsvs )
        for idx in xrange(len(self.parent.hsvs)):
            sNew = minS + (maxS - minS) / ( numPoints - 1) * idx
            vNew = 1.0 - ( 1.0 - minVal ) / ( numPoints - 1) * idx
            self.parent.hsvs[idx] = [ hNew, sNew, vNew ]
        self.parent.update( )

    def rescaleColor(self):
        maxSat = max([ s for (h, s, v) in self.parent.hsvs ])
        if maxSat <= 1e-6:
            maxSat = 0.01
        self.parent.cww.rescaleWheel( dmax = maxSat )

    def resetScaleColor( self ):
        self.parent.cww.rescaleWheel( dmax = 1.0 )

    def recenterLastColor( self ):
        self.parent.hsvs[ self.parent.currentIndex ] = [ 0.0, 0.0, 1.0 ]
        self.parent.update()

    def normCValue( self ):
        if len( self.parent.hsvs ) > 1:
            avgVal = numpy.average([ v for (h, s, v) in self.parent.hsvs ])
            for idx in xrange(len( self.parent.hsvs )):
                self.parent.hsvs[idx][-1] = avgVal
            self.parent.update()

    def paintEvent(self, evt):
        qs = self.size()
        image = QImage( qs.width(), qs.height(), QImage.Format_ARGB32)
        image.fill( QColor( "#E6E6E6" ).rgb() )
        painter = QPainter( self )
        painter.setRenderHint( QPainter.Antialiasing )
        painter.drawImage(0, 0, image )
