from PyQt4.QtGui import *
from PyQt4.QtCore import *
from cwAll import ColorWheelAll
from cwResources import ColorWheelResource, find_avconv_handbrake
import math, numpy, shutil, sys, os, cssutils, subprocess
from progressbar import Percentage, Bar, RotatingMarker, ProgressBar, ETA
from enum import Enum
from optparse import OptionParser

class OperationAnimation(Enum):
    HUETRANSFORM = 1
    SATURATIONTRANSFORM = 2
    VALUETRANSFORM = 3

class ColorWheelOperations(Enum):
    DONOTHING = 1
    EXPANDCOLORWHEEL = 2
    SHRINKCOLORWHEEL = 3

class StupidProgressBar( QWidget ):
    def __init__(self, parent):
        super(StupidProgressBar, self).__init__( parent )
        self.parent = parent
        #
        self.value = 0.0
        self.font = QFont( )
        self.font.setFamily( 'Alef' )
        self.font.setPointSize( 14 )
        self.font.setBold( True )
        self.pen = QPen( )
        self.pen.setColor( QColor( 'black' ) )

    def setValue(self, val):
        assert( val >= 0)
        assert( val <= 1.0)
        self.value = val
        self.update( )

    def paintEvent( self, evt ):
        size = self.size( )
        width = size.width( )
        height = size.height( )
        image = QImage(size, QImage.Format_ARGB32)
        image.fill( QColor("white").rgb() )
        painter = QPainter( self )
        painter.setRenderHint( QPainter.Antialiasing )
        painter.drawImage(0, 0, image )
        painter.fillRect( 0, 0, int( width * self.value ), height,
                          QColor( "#DOEAFF" ) )
        painter.setFont( self.font )
        painter.setPen( self.pen )
        painter.drawText( QRect( 0, 0, width, height ), Qt.AlignCenter,
                          '%d%%' % int( 100 * self.value ) )
                          
        
                    
_nameTable = { OperationAnimation.HUETRANSFORM : 'HUE VIDEO ANIMATION',
               OperationAnimation.SATURATIONTRANSFORM : 'SATURATION VIDEO ANIMATION',
               OperationAnimation.VALUETRANSFORM : 'VALUE VIDEO ANIMATION' }

class CustomRunnable( QThread ):
    partDone = pyqtSignal( int, int, ColorWheelOperations )
    
    def __init__(self, parent ):
        super(CustomRunnable, self).__init__( )
        self.parent = parent

    def run( self ):
        #
        ## now do the animation
        indices_up, indices_down, indices_upagain, upValue, downValue = self.parent.get_indices(
            self.parent.cwa.hsvs )
        
        #
        ## start point wait
        currentIdx = 0
        for idx in xrange( int( 30 * 0.01 * self.parent.startTimeSlider.value( ) ) ):
            self.partDone.emit( currentIdx, 0, ColorWheelOperations.DONOTHING )
            currentIdx += 1

        # go up from zero
        for idx in indices_up:
            self.partDone.emit( currentIdx, idx, ColorWheelOperations.DONOTHING )
            currentIdx += 1

        # wait at top
        for idx in xrange( int( 30 * 0.01 * self.parent.endTimeSlider.value( ) ) ):
            self.partDone.emit( currentIdx, upValue, ColorWheelOperations.DONOTHING )
            currentIdx += 1

        # go down
        for idx in indices_down:
            self.partDone.emit( currentIdx, idx, ColorWheelOperations.SHRINKCOLORWHEEL )
            currentIdx += 1

        # go up again
        if len( indices_upagain ) != 0:
            
            # wait at bottom
            lastIdx = -1
            for idx in xrange( int( 30 * 0.01 * self.parent.endTimeSlider.value( ) ) ):
                self.partDone.emit( currentIdx, idx, ColorWheelOperations.DONOTHING )
                currentIdx += 1
                lastIdx = idx

            if lastIdx != -1:
                self.partDone.emit( currentIdx - 1, lastIdx, ColorWheelOperations.EXPANDCOLORWHEEL )

            # go up
            for idx in indices_upagain:
                self.partDone.emit( currentIdx, idx, ColorWheelOperations.DONOTHING )
                currentIdx += 1

class CustomLabel( QLabel ):
    def __init__(self, parent ):
        super(CustomLabel, self).__init__( "", parent )
        self.actValue = ""

    def setText( self, newText ):
        super(CustomLabel, self).setText( os.path.basename( newText ) )
        self.actValue = newText

    def text( self ):
        return self.actValue

    def clearText( self ):
        super(CustomLabel, self).setText( "" )
        self.actValue = ""

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
        #
        mainLayout.addWidget( self.pbar, 6, 0, 1, 5 )
        mainLayout.addWidget( QLabel("PBAR" ), 6, 5, 1, 1 )
    
    def __init__( self, transform = OperationAnimation.HUETRANSFORM ):
        super(OperationSliderAnimation, self).__init__( )
        self.setFixedWidth( 500 )
        self.setWindowFlags( Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint | Qt.Window )
        self.setSizePolicy(  QSizePolicy.Fixed, QSizePolicy.Fixed )
        self.transform = transform
        self.setWindowTitle( _nameTable[ transform ] )
        self.cwa = ColorWheelAll( )
        #
        ##
        avconv_handbrake_dict = find_avconv_handbrake( )
        if avconv_handbrake_dict is None:
            initQEM = QErrorMessage( )
            initQEM.showMessage( "ERROR, cannot find either ffmpeg/avconv or handbrakeCLI. Exiting...")
            qApp.quit( )
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
        self.pbar = StupidProgressBar( self )
        self.pbar.setValue( 0.0 )
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
        self.bigRedGoButton.clicked.connect( self.bigRedGoRunnable )
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

    def _updateColorWheel( self, currentIdx, currentVal, op ):
        movieDir = self.movieName.actValue.strip( )
        self.setSliderValue( self.cwa, currentVal )
        if self.transform == OperationAnimation.SATURATIONTRANSFORM:
            if op == ColorWheelOperations.SHRINKCOLORWHEEL:
                # get maximum value of saturations
                maxSat = max([ s for (h, s, v) in
                               self.cwa.getTransformedHsvs( ) ])
                if maxSat <= 0.2 * self.cwa.cww.dmax:
                    self.cwa.cww.rescaleWheel( maxSat )
                    self.cwa.update( )
            elif op == ColorWheelOperations.EXPANDCOLORWHEEL:
                maxSat = max([ s for (h, s, v) in
                               self.cwa.getTransformedHsvs( ) ] )
                if maxSat >= 4.75 * self.cwa.cww.dmax:
                    self.cwa.cww.rescaleWheel( min( 1.0, 5 * maxSat ) )
                    self.cwa.update( )
        #
        ##
        p = QPixmap.grabWidget( self.cwa )
        p.save( os.path.join( movieDir, 'movie.%04d.png' % currentIdx ) )
        self.pbar.setValue( 1.0 * ( currentIdx + 1 ) / self.maxIndex )

    def _createMovieAndStop( self ):
        movieDir = self.movieName.actValue.strip( )
        avconv_handbrake_dict = find_avconv_handbrake( )
        aviFile =  os.path.join( os.path.dirname( movieDir ), '%s.avi' %
                                 os.path.basename( movieDir ) )
        mp4File = os.path.join( os.path.dirname( movieDir ), '%s.mp4' %
                                os.path.basename( movieDir ) )
        exec_cmd = [ avconv_handbrake_dict[ 'avconv' ], '-y', '-f', 'image2', '-i',
                     os.path.join( movieDir, 'movie.%04d.png' ),
                     '-vcodec', 'huffyuv', aviFile ]
        proc = subprocess.Popen( exec_cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
        stdout_val, stderr_val = proc.communicate( )
        shutil.rmtree( movieDir )
        
        exec_cmd = [ avconv_handbrake_dict[ 'handbrake' ], '-i', aviFile,
                     '-o', mp4File, '-e', 'x264' ]
        proc = subprocess.Popen( exec_cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
        stdout_val, stderr_val = proc.communicate( )
        os.remove( aviFile )
        #
        self.rotationSpeedDialog.setEnabled( True )
        self.rotationSpeedSlider.setEnabled( True )
        self.startTimeSlider.setEnabled( True )
        self.startTimeDialog.setEnabled( True )
        self.endTimeSlider.setEnabled( True )
        self.endTimeDialog.setEnabled( True )
        self.movieButton.setEnabled( True )
        self.cssButton.setEnabled( True )
        self.bigRedGoButton.setEnabled( True )
        #
        ## now get rid of the texts
        self.movieName.clearText( )
        self.cssFileName.clearText( )
        self.pbar.setValue( 0.0 )
        
    def bigRedGoRunnable( self ):
        self.rotationSpeed( )
        self.startTime( )
        self.endTime( )
        if len( self.cssFileName.actValue.strip( ) ) == 0:
            self.qem.showMessage( "Error, no CSS file chosen." )
        if len( self.movieName.actValue.strip( ) ) == 0:
            self.qem.showMessage( "Error, no movie directory chosen." )
        #
        ##
        self.rotationSpeedDialog.setEnabled( False )
        self.rotationSpeedSlider.setEnabled( False )
        self.startTimeSlider.setEnabled( False )
        self.startTimeDialog.setEnabled( False )
        self.endTimeSlider.setEnabled( False )
        self.endTimeDialog.setEnabled( False )
        self.movieButton.setEnabled( False )
        self.cssButton.setEnabled( False )
        self.bigRedGoButton.setEnabled( False )
        #
        ##
        movieDir = self.movieName.actValue.strip( )
        if not os.path.exists( movieDir ):
            os.mkdir( movieDir )
        cssFileName = self.cssFileName.actValue.strip( )
        css = cssutils.parseFile( cssFileName )
        self.cwa.pushNewColorsFromCSS( css )       
        indices_up, indices_down, indices_upagain, upValue, downValue = self.get_indices( self.cwa.hsvs )
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
        self.maxIndex = maxIndex( )
        #
        ##
        self.runGoRun = CustomRunnable( self )
        self.runGoRun.partDone.connect( self._updateColorWheel )
        self.runGoRun.finished.connect( self._createMovieAndStop )
        self.runGoRun.start( )
        
if __name__=='__main__':
    parser = OptionParser()
    parser.add_option('--dohue', dest='do_hue', action='store_true', default = False,
                      help = 'If chosen, do a HUE transform movie' )
    parser.add_option('--dosat', dest='do_sat', action='store_true', default = False,
                      help = 'If chosen, do a SATURATION transform movie' )
    parser.add_option('--doval', dest='do_val', action='store_true', default = False,
                      help = 'If chosen, do a VALUE transform movie' )
    opts, args = parser.parse_args()
    assert(len(filter( lambda tok: tok is True, ( opts.do_hue, opts.do_sat, opts.do_val ) ) ) == 1 )    
    app = QApplication([])
    #aosa = AllOperationSliderAnimation( )
    #aosa.show( )
    if opts.do_hue:
        osa = OperationSliderAnimation( OperationAnimation.HUETRANSFORM )
    elif opts.do_sat:
        osa = OperationSliderAnimation( OperationAnimation.SATURATIONTRANSFORM )
    else:
        osa = OperationSliderAnimation( OperationAnimation.VALUETRANSFORM )
    osa.show( )
    sys.exit( app.exec_( ) )

    
