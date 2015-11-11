from PyQt4.QtGui import *
from PyQt4.QtCore import *
from cwAll import ColorWheelAll
from cwResources import ColorWheelResource
import math, numpy, shutil, sys, os, cssutils, subprocess
from progressbar import Percentage, Bar, RotatingMarker, ProgressBar, ETA

class CustomRunnable( QRunnable ):
    def __init__(self, parent ):
        super(CustomRunnable, self).__init__( )
        self.parent = parent

    def run( self ):
        cwa = ColorWheelAll( )
        #
        ## now do the animation
        currentIdx = 0
        movieDir = self.parent.movieName.actValue.strip( )
        cssFileName = self.parent.cssFileName.actValue.strip( )
        if not os.path.exists( movieDir ):
            os.mkdir( movieDir )
        css = cssutils.parseFile( cssFileName )
        cwa.pushNewColorsFromCSS( css )

        def maxIndex( ):
            currIdx = 0
            for idx in xrange( int( 30 * 0.01 * self.parent.startTimeSlider.value( ) ) ):
                currIdx += 1
            for idx in xrange( 1, 360 ):
                currIdx += 1
            for idx in xrange( int( 30 * 0.01 * self.parent.endTimeSlider.value( ) ) ):
                currIdx += 1
            for idx in xrange( 359, -1, -1 ):
                currIdx += 1
            return currIdx

        maxIdx = maxIndex( )        
        
        #
        ## start point wait
        for idx in xrange( int( 30 * 0.01 * self.parent.startTimeSlider.value( ) ) ):
            cwa.cws.rotationSlider.setValue( 0 )
            cwa.update( )
            #p = QPixmap.grabWidget( cwa )
            #p.save( os.path.join( movieDir, 'movie.%04d.png' % currentIdx ) )
            currentIdx += 1
            self.parent.pbar.setValue( int( currentIdx * 1.0 / maxIdx ) )
            self.parent.pbar.update( )

        # rotate up
        for idx in xrange( 1, 360 ):
            cwa.cws.rotationSlider.setValue( idx )
            cwa.update( )
            #p = QPixmap.grabWidget( cwa )
            #p.save( os.path.join( movieDir, 'movie.%04d.png' % currentIdx ) )
            currentIdx += 1
            self.parent.pbar.setValue( int( currentIdx * 1.0 / maxIdx ) )
            self.parent.pbar.update( )

        # wait at end
        for idx in xrange( int( 30 * 0.01 * self.parent.endTimeSlider.value( ) ) ):
            cwa.cws.rotationSlider.setValue( 360 )
            cwa.update( )
            #p = QPixmap.grabWidget( cwa )
            #p.save( os.path.join( movieDir, 'movie.%04d.png' % currentIdx ) )
            currentIdx += 1
            self.parent.pbar.setValue( int( currentIdx * 1.0 / maxIdx ) )
            self.parent.pbar.update( )

        # rotate down
        for idx in xrange( 359, -1, -1 ):
            cwa.cws.rotationSlider.setValue( idx )
            cwa.update( )
            #p = QPixmap.grabWidget( cwa )
            #p.save( os.path.join( movieDir, 'movie.%04d.png' % currentIdx ) )
            currentIdx += 1
            self.parent.pbar.setValue( int( currentIdx * 1.0 / maxIdx ) )
            self.parent.pbar.update( )

class CustomLabel( QLabel ):
    def __init__(self, parent ):
        super(CustomLabel, self).__init__( "", parent )
        self.actValue = ""

    def setText( self, newText ):
        super(CustomLabel, self).setText( os.path.basename( newText ) )
        self.actValue = newText

    def text( self ):
        return self.actValue

class CustomErrorMessage( QErrorMessage ):
    def __init__(self, parent ):
        super(CustomErrorMessage, self).__init__( parent )
        self.parent = parent
        self.button = max( filter(lambda obj: isinstance( obj, QPushButton ), self.children() ) )
        self.button.clicked.connect( self.hideMe )
        #
        escAction = QAction( self )
        escAction.setShortcut( 'Esc' )
        escAction.triggered.connect( self.hideMe )
        self.addAction( escAction )

    def closeEvent( self, evt ):
        self.hideMe( )

    def hideMe( self ):
        self.hide( )
        self.parent.setEnabled( True )

    def showMessage(self, msg):
        super(CustomErrorMessage, self).showMessage( msg )
        self.parent.setEnabled( False )
        self.setEnabled( True )
        
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
        #
        mainLayout.addWidget( self.bigRedGoButton, 5, 0, 1, 6 )
    
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
        self.bigRedGoButton = QPushButton( "BIG RED GO BUTTON MAKE MOVIE" )
        self.setStyleSheet( cwr.getStyleSheet( "qpushbutton" ) )
        #
        self.qem = CustomErrorMessage( self )
        self.pbar = QProgressBar( self )
        self.pbar.setVisible( False )
        self.pbar.setFixedSize( 450, 50 )
        self.pbar.setMinimum( 0 )
        self.pbar.setMaximum( 99 )
        self.pbar.setWindowFlags( Qt.CustomizeWindowHint | Qt.Window )
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
        self.bigRedGoButton.clicked.connect( self.bigRedGo )
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

    def closeEvent( self, evt ):
        qApp.quit( )
        
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
        #dialog = QFileDialog( this )
        #dialog.setFileMode( QFileDialog.Directory )
        #dialog.setOption( QFileDialog.ShowDirsOnly )
        #dialog.setAcceptMode( QFileDialog.AcceptSave )
        while( True ):            
            dirname = str( QFileDialog.getSaveFileName( self, 'Save Movie File',
                                                        os.path.expanduser( '~' ),
                                                        options = QFileDialog.ShowDirsOnly ) )
            if not os.path.exists( dirname ) or len( os.path.basename( dirname ) ) == 0:
                break
            print 'Sorry, %s exists' % dirname 
        if not len( os.path.basename( dirname ) ) == 0:
            self.movieName.setText( dirname )

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

    def bigRedGo( self ):
        self.rotationSpeed( )
        self.startTime( )
        self.endTime( )
        if len( self.cssFileName.actValue.strip( ) ) == 0:
            self.qem.showMessage( "Error, no CSS file chosen." )
        if len( self.movieName.actValue.strip( ) ) == 0:
            self.qem.showMessage( "Error, no movie directory chosen." )

        #runGoRun = CustomRunnable( self )
        #self.setEnabled( False )
        #self.pbar.setVisible( True )
        #self.pbar.setEnabled( True )
        #qtp = QThreadPool( )
        #qtp.setMaxThreadCount( 1 )
        #qtp.start( runGoRun )
        self.setEnabled( False )
        cwa = ColorWheelAll( )
        #
        ## now do the animation
        currentIdx = 0
        movieDir = self.movieName.actValue.strip( )
        cssFileName = self.cssFileName.actValue.strip( )
        if not os.path.exists( movieDir ):
            os.mkdir( movieDir )
        css = cssutils.parseFile( cssFileName )
        cwa.pushNewColorsFromCSS( css )

        def maxIndex( ):
            currIdx = 0
            for idx in xrange( int( 30 * 0.01 * self.startTimeSlider.value( ) ) ):
                currIdx += 1
            for idx in xrange( 1, 360 ):
                currIdx += 1
            for idx in xrange( int( 30 * 0.01 * self.endTimeSlider.value( ) ) ):
                currIdx += 1
            for idx in xrange( 359, -1, -1 ):
                currIdx += 1
            return currIdx

        maxIdx = maxIndex( )
        widgets = [ 'Progress: ', Percentage(), ' ', Bar(marker=RotatingMarker()),
                    ' ', ETA() ]
        pbar = ProgressBar( widgets = widgets, maxval = maxIdx ).start( )
        
        #
        ## start point wait
        for idx in xrange( int( 30 * 0.01 * self.startTimeSlider.value( ) ) ):
            cwa.cws.rotationSlider.setValue( 0 )
            cwa.update( )
            p = QPixmap.grabWidget( cwa )
            p.save( os.path.join( movieDir, 'movie.%04d.png' % currentIdx ) )
            currentIdx += 1
            pbar.update( currentIdx )

        # rotate up
        for idx in xrange( 1, 360 ):
            cwa.cws.rotationSlider.setValue( idx )
            cwa.update( )
            p = QPixmap.grabWidget( cwa )
            p.save( os.path.join( movieDir, 'movie.%04d.png' % currentIdx ) )
            currentIdx += 1
            pbar.update( currentIdx )
            
        # wait at end
        for idx in xrange( int( 30 * 0.01 * self.endTimeSlider.value( ) ) ):
            cwa.cws.rotationSlider.setValue( 360 )
            cwa.update( )
            p = QPixmap.grabWidget( cwa )
            p.save( os.path.join( movieDir, 'movie.%04d.png' % currentIdx ) )
            currentIdx += 1
            pbar.update( currentIdx )
            
        # rotate down
        for idx in xrange( 359, -1, -1 ):
            cwa.cws.rotationSlider.setValue( idx )
            cwa.update( )
            p = QPixmap.grabWidget( cwa )
            p.save( os.path.join( movieDir, 'movie.%04d.png' % currentIdx ) )
            currentIdx += 1
            #self.parent.pbar.setValue( int( currentIdx * 1.0 / maxIdx ) )
            #self.parent.pbar.update( )
            pbar.update( currentIdx )
        
        #
        ## now start making the movies
        exec_cmd = [ '/usr/bin/ffmpeg', '-f', 'image2', '-i', os.path.join( movieDir, 'movie.%04d.png' ),
                     '-vcodec', 'huffyuv', os.path.join( os.path.dirname( movieDir ), '%s.avi' %
                                                         os.path.basename( movieDir ) ) ]
        proc = subprocess.Popen( exec_cmd, stdout = subprocess.PIPE, stderr = subprocess.OUT )
        stdout_val, stderr_val = subprocess.communicate( )
        

        # now quit
        pbar.finish( )
        qApp.quit( )
        
if __name__=='__main__':
    app = QApplication([])
    rsa = RotationSliderAnimation( )
    rsa.show( )
    sys.exit( app.exec_( ) )
    
