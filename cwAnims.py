from PyQt4.QtGui import *
from PyQt4.QtCore import *
from cwAll import ColorWheelAll
from cwResources import ColorWheelResource
import math, numpy, shutil, sys, os

class CustomLabel( QLabel ):
    def __init__(self, parent ):
        super(CustomLabel, self).__init__( "", parent )
        self.actValue = ""

    def setText( self, newText ):
        super(CustomLabel, self).setText( os.path.basename( newText ) )
        self.actValue = newText

    def text( self ):
        return self.actValue        
        
class RotationSliderAnimation( QWidget ):
    def _initLayout( self ):
        mainLayout = QGridLayout( )
        self.setLayout( mainLayout )
        mainLayout.addWidget( QLabel( "SLOWNESS" ), 0, 0, 1, 1 )
        mainLayout.addWidget( self.rotationSpeedSlider, 0, 1, 1, 4 )
        mainLayout.addWidget( self.rotationSpeedDialog, 0, 5, 1, 1 )
        #
        mainLayout.addWidget( QLabel( "START (s)" ), 1, 0, 1, 1 )
        mainLayout.addWidget( self.startTimeSlider, 1, 1, 1, 4 )
        mainLayout.addWidget( self.startTimeDialog, 1, 5, 1, 1 )
        #
        mainLayout.addWidget( QLabel( "END (s)" ), 2, 0, 1, 1 )
        mainLayout.addWidget( self.endTimeSlider, 2, 1, 1, 4 )
        mainLayout.addWidget( self.endTimeDialog, 2, 5, 1, 1 )
        #
        mainLayout.addWidget( self.movieButton, 3, 0, 1, 1 )
        mainLayout.addWidget( self.movieName, 3, 1, 1, 5 )
        #
        mainLayout.addWidget( self.cssButton, 4, 0, 1, 1 )
        mainLayout.addWidget( self.cssFileName, 4, 1, 1, 5 )
    
    def __init__( self ):
        super(RotationSliderAnimation, self).__init__( )
        self.setFixedWidth( 500 )
        self.setWindowFlags( Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint | Qt.Window )
        self.setSizePolicy(  QSizePolicy.Fixed, QSizePolicy.Fixed )
        self.setWindowTitle( 'ROTATION VIDEO ANIMATION')
        #
        ## now some of the data members
        self.rotationSpeedSlider = QSlider( Qt.Horizontal )
        self.rotationSpeedSlider.setTickInterval( 10 )
        self.rotationSpeedSlider.setTickPosition( QSlider.TicksBelow )
        self.rotationSpeedSlider.setMinimum( 0 )
        self.rotationSpeedSlider.setMaximum( 100 )
        self.rotationSpeedSlider.setValue( 0 )
        self.rotationSpeedDialog = QLineEdit( "%0.3f" %
                                              math.pow( 10, 0.01 * self.rotationSpeedSlider.value() ) )
        self.rotationSpeedDialog.setFixedWidth( 85 )
        #
        self.startTimeSlider = QSlider( Qt.Horizontal )
        self.startTimeSlider.setTickInterval( 10 )
        self.startTimeSlider.setTickPosition( QSlider.TicksBelow )
        self.startTimeSlider.setMinimum( 0 )
        self.startTimeSlider.setMaximum( 100 )
        self.startTimeSlider.setValue( 15 )
        self.startTimeDialog = QLineEdit( "%0.2f" %
                                          ( 0.01 * self.startTimeSlider.value() ) )
        self.startTimeDialog.setFixedWidth( 85 )
        #
        self.endTimeSlider = QSlider( Qt.Horizontal )
        self.endTimeSlider.setTickInterval( 10 )
        self.endTimeSlider.setTickPosition( QSlider.TicksBelow )
        self.endTimeSlider.setMinimum( 0 )
        self.endTimeSlider.setMaximum( 100 )
        self.endTimeSlider.setValue( 30 )
        self.endTimeDialog = QLineEdit( "%0.2f" %
                                        ( 0.01 * self.endTimeSlider.value() ) )
        self.endTimeDialog.setFixedWidth( 85 )
        #
        cwr = ColorWheelResource( )
        self.movieName = CustomLabel( self )
        self.movieButton = QPushButton( "MOVIE NAME" )
        self.movieButton.setStyleSheet( cwr.getStyleSheet( "qpushbutton" ) )
        self.movieName.setStyleSheet( cwr.getStyleSheet( "qlabel" ) )
        #
        self.cssFileName = CustomLabel( self )
        self.cssButton = QPushButton( "EXAMPLE CSS FILE" )
        self.cssButton.setStyleSheet( cwr.getStyleSheet( "qpushbutton" ) )
        self.cssFileName.setStyleSheet( cwr.getStyleSheet( "qlabel" ) )
        #
        ## now make the layout
        self._initLayout( )
        #
        ## add actions
        self.rotationSpeedDialog.returnPressed.connect( self.setRotationSpeed )
        self.startTimeDialog.returnPressed.connect( self.setStartTime )
        self.endTimeDialog.returnPressed.connect( self.setEndTime )
        self.movieButton.clicked.connect( self.setMovieName )
        self.cssButton.clicked.connect( self.setCSSFile )
        self.rotationSpeedSlider.valueChanged.connect( self.rotationSpeed )
        self.startTimeSlider.valueChanged.connect( self.startTime )
        self.endTimeSlider.valueChanged.connect( self.endTime )
        #
        quitAction = QAction( self )
        quitAction.setShortcut( 'Ctrl+Q' )
        quitAction.triggered.connect( qApp.quit )
        self.addAction( quitAction )
        #
        quit2Action = QAction( self )
        quit2Action.setShortcut( 'Esc' )
        quit2Action.triggered.connect( qApp.quit )
        self.addAction( quit2Action )

    def rotationSpeed( self ):
        self.rotationSpeedDialog.setText( "%0.3f" %
                                          math.pow(10, 0.01 * self.rotationSpeedSlider.value( ) ) )

    def startTime( self ):
        self.startTimeDialog.setText( "%0.2f" %
                                      ( 0.01 * self.startTimeSlider.value( ) ) )

    def endTime( self ):
        self.endTimeDialog.setText( "%0.2f" %
                                    ( 0.01 * self.endTimeSlider.value( ) ) )

    def setRotationSpeed( self ):
        try:
            val = float( self.rotationSpeedDialog.text( ) )
            val = max( 1.0, val )
            val = min( 10.0, val )
            tickVal = int( 100 * math.log( val ) / math.log( 10.0 ) )
            self.rotationSpeedSlider.setValue( tickVal )
        except Exception:
            pass
        self.rotationSpeed( )
        

    def setStartTime( self ):
        try:
            startTime = float( self.startTimeDialog.text( ) )
            val = max( 0.0, val )
            val = min( 1.0, val )
            tickVal = int( 100 * val )
            self.startTimeSlider.setValue( tickVal )
        except Exception:
            pass
        self.startTime( )
        
    def setEndTime( self ):
        try:
            endTime = float( self.endTimeDialog.text( ) )
            val = max( 0.0, val )
            val = min( 1.0, val )
            tickVal = int( 100 * val )
            self.endTimeSlider.setValue( tickVal )
        except Exception:
            pass
        self.endTime( )

    def setMovieName( self ):
        print 'HELLO WORLD'

    def setCSSFile( self ):
        dirNameDefault = os.path.join( os.path.dirname( os.path.expanduser(__file__) ),
                                       'resources', 'examples' )
        while( True ):
            fname = str( QFileDialog.getOpenFileName( self, 'Open CSS File',
                                                      dirNameDefault,
                                                      filter = "*.css" ) )
            if fname.lower().endswith('.css') or len( os.path.basename( fname ) ) == 0:
                break
        if fname.lower().endswith( '.css' ):
            self.cssFileName.setText( fname )
        
if __name__=='__main__':
    app = QApplication([])
    rsa = RotationSliderAnimation( )
    rsa.show( )
    sys.exit( app.exec_( ) )
    
