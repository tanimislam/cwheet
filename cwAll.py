from PyQt4.QtCore import *
from PyQt4.QtGui import *
from cwWidgets import ColorWheelWidget, ColorWheelBar, ColorWheelValues
from cwTable import ColorWheelTable
from cwSlider import ColorWheelSlider
from cwButtons import ColorWheelButtons
from cwMenubar import ColorWheelMenuBar
import sys, math

class ColorWheelAll( QWidget ):
    def _layoutLeftWidget( self ):
        leftWidget = QWidget( )
        leftLayout = QVBoxLayout( )
        leftWidget.setLayout( leftLayout )
        #
        ## color widget layout
        leftLayout.addWidget( self._layoutColorWidget( ) )
        #
        ## now button layer
        leftLayout.addWidget( self.cwbut )
        #
        ## now sliders
        leftLayout.addWidget( self.cws )
        #
        return leftWidget

    def _layoutRightWidget( self ):
        rightWidget = QWidget( )
        rightLayout = QVBoxLayout( )
        rightWidget.setLayout( rightLayout )
        rightWidget.setStyleSheet("background-color: #EDDFEB;")
        rightLayout.addWidget( self.cwt )
        rightLayout.addWidget( QWidget( ) )
        rightLayout.addWidget( self._layoutColorWheelValuesScrollArea( ) )
        return rightWidget

    def _layoutColorWidget( self ):
        colorWidget = QWidget( )
        colorLayout = QGridLayout( )
        colorWidget.setStyleSheet( "background-color: white;" )
        colorWidget.setLayout( colorLayout )
        width = 1.6 * self.mainWidth + 1.2 * self.mainDiameter
        height = 1.2 * self.mainDiameter
        colorWidget.setFixedSize( width, height )
        colorLayout.addWidget( self.cwb, 0, 0, 1, 1 )
        colorLayout.addWidget( self.cww, 0, 1, 1, 1 )
        return colorWidget

    def _layoutColorWheelValuesScrollArea( self ):
        scrollArea = QScrollArea( )
        scrollArea.setWidget( self.cwv )
        scrollArea.setFixedSize( 300, 250 )
        scrollArea.setHorizontalScrollBarPolicy( Qt.ScrollBarAlwaysOff )
        return scrollArea
        
        
    def __init__(self, mainWidth = 30, mainDiameter = 256 ):
        super(ColorWheelAll, self).__init__()
        self.setWindowTitle( 'CWHEET v0.1 (Beta)' )
        #
        self.hsvs = [ [ 0, 0.0, 1.0 ] ]
        self.currentIndex = -1
        self.cww = ColorWheelWidget( self, mainDiameter )
        self.cwb = ColorWheelBar( self, mainWidth, mainDiameter )
        self.cws = ColorWheelSlider( self )
        self.cwbut = ColorWheelButtons( self )
        self.cwt = ColorWheelTable( self )
        self.cwv = ColorWheelValues( self )
        self.cwmb = ColorWheelMenuBar( self )
        self.mainWidth = mainWidth
        self.mainDiameter = mainDiameter
        #
        mainLayout = QVBoxLayout( )
        self.setLayout( mainLayout )
        mainLayout.addWidget( self.cwmb )
        #
        topWidget = QWidget( )
        topLayout = QHBoxLayout( )
        topWidget.setLayout( topLayout )
        topLayout.addWidget( self._layoutLeftWidget( ) )
        topLayout.addWidget( self._layoutRightWidget( ) )
        mainLayout.addWidget( topWidget )
        #
        self.setSizePolicy( QSizePolicy( QSizePolicy.Fixed, QSizePolicy.Fixed ) )
        self.setWindowFlags( Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint )
        #
        ##
        removeColorAction = QAction( self )
        removeColorAction.setShortcut( 'Ctrl+Z' )
        removeColorAction.triggered.connect( self.removeColor )
        self.addAction( removeColorAction )
        #
        snapBackAction = QAction( self )
        snapBackAction.setShortcut( 'Ctrl+Y' )
        snapBackAction.triggered.connect( self.cws.snapBack )
        self.addAction( snapBackAction )
        
        
    #def keyPressEvent(self, evt):
    #    if evt.key() == Qt.Key_Z:
    #        self.removeColor()
    #    elif evt.key() == Qt.Key_Y:
    #        self.cws.snapBack()
    #    QWidget.keyPressEvent(self, evt )

    def getTransformedHsvs( self ):
        rotVal = self.cws.rotationSlider.value() * 1.0 / 360.0
        scaleVal = math.pow( 10.0, 0.01 * self.cws.scalingSlider.value() )
        valTrans = 0.01 * self.cws.valueSlider.value()
        scaleMax = max([ s for (h,s,v) in self.hsvs ])
        if scaleMax != 0:
            scaleVal = min( scaleVal, 1.0 / scaleMax )
            self.cws.scalingSlider.setEnabled( True )
        else:
            self.cws.scalingSlider.setEnabled( False )
        newHsvs = []
        for tup in self.hsvs:
            h, s, v = tup
            sv = min( self.cww.dmax, s * scaleVal )
            hv = h + rotVal
            if hv > 1:
                hv -= 1
            vv = min(1.0, v + valTrans )
            vv = max(0.0, vv )
            newHsvs.append([hv, sv, vv])
        return newHsvs
        

    #
    #def paintEvent(self, evt):
    #    self.cww.update()
    #    self.cwb.update()
    #    self.cws.update()
    #    self.cwbut.update()
    #    self.cwv.update()
    #
    ## now set the coordinates
    #hsvsCoords = [ QPoint( s * self.cww.master_radius * math.cos( 2 * math.pi * h ),
    #                       -s * self.cww.master_radius * math.sin( 2 * math.pi * h ) ) + self.cww.center for
    #               (h, s, v) in self.hsvs ]
    #self.qrects = [ QRect( coord - QPoint(5, 5), coord + QPoint(5, 5) ) for coord in hsvsCoords ]

    def removeColor(self):
        if len( self.hsvs ) > 1:
            if self.currentIndex == -1:
                self.hsvs.pop()
            else:
                self.hsvs.pop( self.currentIndex )
            self.cwt.subtractRow( )
            self.currentIndex = -1    
            self.update()

if __name__=='__main__':
    app = QApplication([])
    cwa = ColorWheelAll(mainDiameter = 325 )
    cwa.show()
    sys.exit( app.exec_())
