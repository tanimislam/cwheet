from PyQt4.QtCore import *
from PyQt4.QtGui import *
from cwWidgets import ColorWheelWidget, ColorWheelBar, ColorWheelValues
from cwTable import ColorWheelTable
from cwSlider import ColorWheelSlider
from cwButtons import ColorWheelButtons
from cwMenubar import ColorWheelMenuBar
from cwResources import ColorWheelResource, getBackgroundColorDict
import sys, math, os

class ColorWheelAll( QMainWindow ):
    def _layoutLeftWidget( self ):
        leftWidget = QWidget( )
        leftLayout = QVBoxLayout( )
        leftWidget.setLayout( leftLayout )
        # leftWidget.setStyleSheet("background-color: #E6E6E6;")
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
        rightWidget.setStyleSheet("background-color: #E6E6E6;")
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
        
        
    def __init__(self, mainWidth = 30, mainDiameter = 325 ):
        super(ColorWheelAll, self).__init__()
        self.setWindowTitle( 'CWHEET v0.1 (Beta)' )
        cwr = ColorWheelResource( )
        self.setWindowIcon( cwr.getIcon( 'cwheet-icon' ) )
        #
        self.hsvs = [ [ 0, 0.0, 1.0 ] ]
        self.currentIndex = -1
        self.cww = ColorWheelWidget( self, mainDiameter )
        self.cwb = ColorWheelBar( self, mainWidth, mainDiameter )
        self.cws = ColorWheelSlider( self )
        self.cwbut = ColorWheelButtons( self )
        self.cwmb = ColorWheelMenuBar( self )
        self.cwt = ColorWheelTable( self )
        self.cwv = ColorWheelValues( self )
        self.mainWidth = mainWidth
        self.mainDiameter = mainDiameter
        #
        self.setMenuBar( self.cwmb )
        #
        centerWidget = QWidget( )
        centerLayout = QHBoxLayout( )
        centerWidget.setLayout( centerLayout )
        centerLayout.addWidget( self._layoutLeftWidget( ) )
        centerLayout.addWidget( self._layoutRightWidget( ) )
        self.setCentralWidget( centerWidget )
        self.setWindowFlags( Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint )
        self.layout().setSizeConstraint( QLayout.SetFixedSize )
        # self.setSizePolicy( QSizePolicy.Fixed, QSizePolicy.Fixed )
        screenshotAction = QAction( self )
        screenshotAction.setShortcut( 'Shift+Ctrl+P' )
        screenshotAction.triggered.connect( self.takeScreenshot )
        self.addAction( screenshotAction )

    def takeScreenshot( self ):
        while( True ):
            fname = str( QFileDialog.getSaveFileName( self, 'Save Screen Shot',
                                                      os.path.expanduser( '~' ),
                                                      filter = "*.png" ) )
            if fname.lower().endswith('.png') or len( os.path.basename( fname ) ) == 0:
                break
        if fname.lower().endswith( '.png' ):
            p = QPixmap.grabWidget( self )
            p.save( fname )
        
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

    def pushNewColors( self, newHsvs ):
        self.cws.setTransform( )
        self.currentIndex = -1
        self.hsvs = newHsvs[:]
        self.update( )

    def removeColor(self):
        if len( self.hsvs ) > 1:
            if self.currentIndex == -1:
                self.hsvs.pop()
            else:
                self.hsvs.pop( self.currentIndex )
            self.cwt.subtractRow( )
            self.currentIndex = -1    
            self.update()

    def pushNewColorsFromCSS( self, css ):
        colorNamesDict = getBackgroundColorDict( css )
        colorLabels = sorted( colorNamesDict.keys() )
        colors = [ ]
        self.cws.snapBack( )
        for name in colorLabels:
            colorName = colorNamesDict[ name ]
            color = QColor( colorName )
            h, s, v, a = color.getHsvF( )
            colors.append([ h, s, v ])
        self.pushNewColors( colors )
        self.cwt.pushData( colorLabels )
        self.update( )

if __name__=='__main__':
    app = QApplication([])
    cwa = ColorWheelAll(mainDiameter = 325 )
    cwa.show()
    sys.exit( app.exec_())
