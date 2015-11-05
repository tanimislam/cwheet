from PyQt4.QtCore import *
from PyQt4.QtGui import *
import math, copy

class ColorWheelSlider( QWidget ):
    def _layoutWidgets( self ):
        slidersLayout = QGridLayout()
        self.setLayout( slidersLayout )
        # self.setStyleSheet( "background-color: #f9ebfd;" )
        slidersLayout.addWidget( QLabel( "ROT"), 0, 0, 1, 1)
        slidersLayout.addWidget( self.rotationSlider, 0, 1, 1, 4 )
        slidersLayout.addWidget( QLabel("SCALE"), 1, 0, 1, 1)
        slidersLayout.addWidget( self.scalingSlider, 1, 1, 1, 4 )
        slidersLayout.addWidget( QLabel( "VAL"), 2, 0, 1, 1)
        slidersLayout.addWidget( self.valueSlider, 2, 1, 1, 4 )
        #
        slidersLayout.addWidget( self.rotationLabel, 3, 0, 1, 1)
        slidersLayout.addWidget( self.scalingLabel, 3, 1, 1, 1)
        slidersLayout.addWidget( self.valueLabel, 3, 2, 1, 1)
        slidersLayout.addWidget( self.settingButton, 3, 3, 1, 2)        
    
    def __init__(self, parent):
        super(QWidget, self).__init__( parent )
        self.parent = parent
        #
        self.rotationSlider = QSlider(Qt.Horizontal)
        self.rotationSlider.setTickInterval( 30 )
        self.rotationSlider.setTickPosition( QSlider.TicksAbove )
        self.rotationSlider.setMinimum( 0 )
        self.rotationSlider.setMaximum( 360 )
        self.rotationSlider.setValue( 0 )
        self.scalingSlider = QSlider(Qt.Horizontal)
        self.scalingSlider.setTickInterval( 20 )
        self.scalingSlider.setTickPosition( QSlider.TicksBelow )
        self.scalingSlider.setMinimum( -200 )
        self.scalingSlider.setMaximum( 200 )
        self.scalingSlider.setValue( 0 )
        self.valueSlider = QSlider( Qt.Horizontal )
        self.valueSlider.setTickInterval( 10 )
        self.valueSlider.setTickPosition( QSlider.TicksBelow )
        self.valueSlider.setMinimum( -100 )
        self.valueSlider.setMaximum( 100 )
        self.valueSlider.setValue( 0 )
        #
        self.rotationLabel = QLabel("%03d" % 0)
        self.scalingLabel = QLabel("%0.3f" % 1.0 )
        self.valueLabel = QLabel("%0.3f" % 0.0)
        self.settingButton = QPushButton("SET TRANSFORM")
        self.settingButton.setStyleSheet("""
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
        #
        ## actions on sliders and button
        self.rotationSlider.valueChanged.connect( self.rotateColors )
        self.scalingSlider.valueChanged.connect( self.scaleColors )
        self.valueSlider.valueChanged.connect( self.valueColors )
        self.settingButton.clicked.connect( self.setTransform )
        #
        ## initially disabled
        self.scalingSlider.setEnabled( False )
        #
        ## now set the layout
        self._layoutWidgets( )
    
    def rotateColors( self ):
        self.rotationLabel.setText( "%03d" % self.rotationSlider.value() )
        self.parent.update()

    def scaleColors( self ):
        self.scalingLabel.setText( "%0.3f" % math.pow( 10.0, 0.01 * self.scalingSlider.value() ) )
        self.parent.update()

    def valueColors( self ):
        valDif = 0.01 * self.valueSlider.value()
        if valDif > 0:
            self.valueLabel.setText( "+%0.3f" % valDif )
        else:
            self.valueLabel.setText( "%0.3f" % valDif )
            
    def snapBack(self):
        self.rotationSlider.setValue( 0 )
        self.scalingSlider.setValue( 0 )
        self.valueSlider.setValue( 0 )
        self.parent.hsvsTrans = copy.deepcopy( self.parent.hsvs )
        # self.parent.cwt.setEnabled( True )
        self.parent.update()

    def setTransform( self ):
        newHSVs = self.parent.getTransformedHsvs( )
        for idx in xrange(len( self.parent.hsvs )):
            h, s, v = newHSVs[idx]
            self.parent.hsvs[idx] = [ h, s, v ]
        self.snapBack( )

    def paintEvent(self, evt):
        qs = self.size()
        image = QImage( qs.width(), qs.height(), QImage.Format_ARGB32)
        image.fill( QColor( "#f9ebfd" ).rgb() )
        painter = QPainter( self )
        painter.setRenderHint( QPainter.Antialiasing )
        painter.drawImage(0, 0, image )
