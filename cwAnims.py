from PyQt4.QtGui import *
from PyQt4.QtCore import *
from cwAll import ColorWheelAll
from cwResources import ColorWheelResource
import math, numpy, shutil, sys, os, cssutils, subprocess
from progressbar import Percentage, Bar, RotatingMarker, ProgressBar, ETA
from enum import Enum

class OperationAnimation(Enum):
    HUETRANSFORM = 1
    SATURATIONTRANSFORM = 2
    VALUETRANSFORM = 3

_nameTable = { OperationAnimation.HUETRANSFORM : 'HUE VIDEO ANIMATION',
               OperationAnimation.SATURATIONTRANSFORM : 'SATURATION VIDEO ANIMATION',
               OperationAnimation.VALUETRANSFORM : 'VALUE VIDEO ANIMATION' }

class CustomRunnable( QRunnable ):
    def __init__(self, parent ):
        super(CustomRunnable, self).__init__( )
        self.parent = parent
        self.procDone = pyqtSignal( bool )
        self.partDone = pyqtSignal( int )
        self.

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

class AllOperationSliderAnimation( QTabWidget ):
    def __init__( self ):
        super( AllOperationSliderAnimation, self).__init__( )
        self.setFixedWidth( 500 )
        for enm in ( OperationAnimation.HUETRANSFORM, OperationAnimation.SATURATIONTRANSFORM,
                     OperationAnimation.VALUETRANSFORM ):
            self.addTab( OperationSliderAnimation( transform = enm ), _nameTable[ enm ] )

        for idx in xrange(3):
            myAction = QAction( self )
            myAction.setShortcut( 'Ctrl+%d' % (idx + 1) )
            myAction.triggered.connect( self.setCurrentIndex )
            self.addAction( myAction )

        quitAction = QAction( self )
        quitAction.setShortcuts([ 'Ctrl+Q', 'Esc' ])
        quitAction.triggered.connect( qApp.quit )
        self.addAction( quitAction )
        
class OperationSliderAnimation( QWidget ):
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
    
    def __init__( self, transform = OperationAnimation.HUETRANSFORM ):
        super(OperationSliderAnimation, self).__init__( )
        self.setFixedWidth( 500 )
        self.setWindowFlags( Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint | Qt.Window )
        self.setSizePolicy(  QSizePolicy.Fixed, QSizePolicy.Fixed )
        self.transform = transform
        self.setWindowTitle( _nameTable[ transform ] )
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
        quitAction.setShortcuts(['Ctrl+Q', 'Esc'])
        quitAction.triggered.connect( qApp.quit )
        self.addAction( quitAction )
        
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

    def get_indices( self, allhsvs ):        
        slownessTransform = math.pow( 10, 0.01 * self.rotationSpeedSlider.value() )
        if self.transform == OperationAnimation.HUETRANSFORM:
            indices_up = [ QStyle.sliderValueFromPosition( 1, 359, idx,
                                                           int( 360 * slownessTransform ) ) for
                           idx in xrange( int( 360 * slownessTransform ) ) ]
            indices_down = [ QStyle.sliderValueFromPosition(0, 359, idx,
                                                            int( 360 * slownessTransform ) ) for
                             idx in xrange( int( 360 * slownessTransform ), -1, -1 ) ]
            indices_upagain = [ ]
            upValue = 360
            downValue = 0
        elif self.transform == OperationAnimation.SATURATIONTRANSFORM:
            allSats = [ s for (h, s, v) in allhsvs ]
            minSat = max( allSats )
            maxMult = min( 100.0, 1.0 / minSat )
            maxMultInVals = int( 100.0 * math.log( maxMult ) / math.log( 10 ) )
            indices_up = [ QStyle.sliderValueFromPosition(0, maxMultInVals, idx,
                                                          int( maxMultInVals * slownessTransform ) ) for
                           idx in xrange( int( maxMultInVals * slownessTransform ) ) ]
            indices_down = [ QStyle.sliderValueFromPosition( -200, maxMultInVals, idx,
                                                             int( ( 200 + maxMultInVals ) * slownessTransform ) ) for
                             idx in xrange( int( ( 200 + maxMultInVals ) * slownessTransform ), -1, -1 ) ]
            indices_upagain = [ QStyle.sliderValueFromPosition( -200, 0, idx,
                                                                int( 200 * slownessTransform ) ) for
                                idx in xrange( int( 200 * slownessTransform ) ) ]
            upValue = maxMultInVals
            downValue = -200
        else:
            allVals = [ v for ( h, s, v ) in allhsvs ]
            maxVal = max( allVals )
            minVal = min( allVals )
            valChangeUp = 1.0 - minVal
            valChangeDown = maxVal
            changeUp = int( valChangeUp * 100 )
            changeDown = int( valChangeDown * 100 )
            indices_up = [ QStyle.sliderValueFromPosition(0, changeUp, idx, int( changeUp * slownessTransform ) ) for
                           idx in xrange( int( changeUp * slownessTransform ) ) ]
            indices_down = [ QStyle.sliderValueFromPosition( -changeDown, changeUp, idx,
                                                             int( ( changeUp + changeDown ) * slownessTransform ) ) for
                             idx in xrange( int( ( changeUp + changeDown ) * slownessTransform ), -1, -1 ) ]
            indices_upagain = [ QStyle.sliderValueFromPosition( -changeDown, 0, idx,
                                                                int( changeDown * slownessTransform ) ) for
                                idx in xrange( int( changeDown * slownessTransform ) ) ]
            upValue = changeUp
            downValue = -changeDown
            
        return indices_up, indices_down, indices_upagain, upValue, downValue

    def setSliderValue( self, cwa, idx ):
        if self.transform == OperationAnimation.HUETRANSFORM:
            cwa.cws.rotationSlider.setValue( idx )
        elif self.transform == OperationAnimation.SATURATIONTRANSFORM:
            cwa.cws.scalingSlider.setValue( idx )
        else:
            cwa.cws.valueSlider.setValue( idx )
        cwa.update( )
            
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
        movieDir = self.movieName.actValue.strip( )
        cssFileName = self.cssFileName.actValue.strip( )
        if not os.path.exists( movieDir ):
            os.mkdir( movieDir )
        css = cssutils.parseFile( cssFileName )
        cwa.pushNewColorsFromCSS( css )

        #
        ## calculate slowness array coming and going
        indices_up, indices_down, indices_upagain, upValue, downValue = self.get_indices( cwa.hsvs )
        
        def maxIndex( ):
            currIdx = 0
            for idx in xrange( int( 30 * 0.01 * self.startTimeSlider.value( ) ) ):
                currIdx += 1
            for idx in indices_up:
                currIdx += 1
            for idx in xrange( int( 30 * 0.01 * self.endTimeSlider.value( ) ) ):
                currIdx += 1
            for idx in indices_down:
                currIdx += 1
            if len( indices_upagain ) != 0:                
                for idx in xrange( int( 30 * 0.01 * self.endTimeSlider.value( ) ) ):
                    currIdx += 1
                for idx in indices_upagain:
                    currIdx += 1
            for idx in xrange( int( 30 * 0.01 * self.startTimeSlider.value( ) ) ):
                currIdx += 1
            return currIdx

        maxIdx = maxIndex( )
        widgets = [ 'Progress: ', Percentage(), ' ', Bar(marker=RotatingMarker()),
                    ' ', ETA() ]
        pbar = ProgressBar( widgets = widgets, maxval = maxIdx ).start( )
        currentIdx = 0
        
        #
        ## start point wait
        for idx in xrange( int( 30 * 0.01 * self.startTimeSlider.value( ) ) ):
            self.setSliderValue( cwa, 0 )
            p = QPixmap.grabWidget( cwa )
            p.save( os.path.join( movieDir, 'movie.%04d.png' % currentIdx ) )
            currentIdx += 1
            pbar.update( currentIdx )

        # go up from zero
        for idx in indices_up:
            self.setSliderValue( cwa, idx )
            p = QPixmap.grabWidget( cwa )
            p.save( os.path.join( movieDir, 'movie.%04d.png' % currentIdx ) )
            currentIdx += 1
            pbar.update( currentIdx )
            
        # wait at top
        for idx in xrange( int( 30 * 0.01 * self.endTimeSlider.value( ) ) ):
            self.setSliderValue( cwa, upValue )
            p = QPixmap.grabWidget( cwa )
            p.save( os.path.join( movieDir, 'movie.%04d.png' % currentIdx ) )
            currentIdx += 1
            pbar.update( currentIdx )
            
        # go down
        for idx in indices_down:
            self.setSliderValue( cwa, idx )
            p = QPixmap.grabWidget( cwa )
            p.save( os.path.join( movieDir, 'movie.%04d.png' % currentIdx ) )
            currentIdx += 1
            #self.parent.pbar.setValue( int( currentIdx * 1.0 / maxIdx ) )
            #self.parent.pbar.update( )
            pbar.update( currentIdx )

        # go up again
        if len( indices_upagain ) != 0:
            # wait at bottom
            for idx in xrange( int( 30 * 0.01 * self.endTimeSlider.value( ) ) ):
                self.setSliderValue( cwa, downValue )
                p = QPixmap.grabWidget( cwa )
                p.save( os.path.join( movieDir, 'movie.%04d.png' % currentIdx ) )
                currentIdx += 1
                pbar.update( currentIdx )

            # go up
            for idx in indices_upagain:
                self.setSliderValue( cwa, idx )
                p = QPixmap.grabWidget( cwa )
                p.save( os.path.join( movieDir, 'movie.%04d.png' % currentIdx ) )
                currentIdx += 1
                pbar.update( currentIdx )

        # wait again at start
        for idx in xrange( int( 30 * 0.01 * self.startTimeSlider.value( ) ) ):
            cwa.cws.rotationSlider.setValue( 0 )
            cwa.update( )
            p = QPixmap.grabWidget( cwa )
            p.save( os.path.join( movieDir, 'movie.%04d.png' % currentIdx ) )
            currentIdx += 1
            pbar.update( currentIdx )

        pbar.finish( )        
        #
        ## now make the movies
        aviFile =  os.path.join( os.path.dirname( movieDir ), '%s.avi' %
                                 os.path.basename( movieDir ) )
        mp4File = os.path.join( os.path.dirname( movieDir ), '%s.mp4' %
                                os.path.basename( movieDir ) )
        exec_cmd = [ '/usr/bin/ffmpeg', '-f', 'image2', '-i', os.path.join( movieDir, 'movie.%04d.png' ),
                     '-vcodec', 'huffyuv', aviFile ]
        proc = subprocess.Popen( exec_cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
        stdout_val, stderr_val = proc.communicate( )
        shutil.rmtree( movieDir )
        
        exec_cmd = [ os.path.expanduser('~/apps/bin/HandBrakeCLI'), '-i', aviFile,
                     '-o', mp4File, '-e', 'x264' ]
        proc = subprocess.Popen( exec_cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
        stdout_val, stderr_val = proc.communicate( )
        os.remove( aviFile )
        
        # now quit
        qApp.quit( )        
        
if __name__=='__main__':
    app = QApplication([])
    aosa = AllOperationSliderAnimation( )
    aosa.show( )
    sys.exit( app.exec_( ) )
