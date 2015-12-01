from PyQt4.QtGui import *
from PyQt4.QtCore import *
import cssutils, os, subprocess, cwResources
import math, numpy

class ColorWheelExpandedColorSwatch( QWidget ):
    def __init__( self, parent ):
        super(ColorWheelExpandedColorSwatch, self).__init__( parent )
        self.parent = parent
        self.setVisible( False )
        self.setWindowFlags( Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint | Qt.Window )
        self.setSizePolicy( QSizePolicy.Fixed, QSizePolicy.Fixed )
        self.setWindowTitle( 'EXPANDED COLOR SWATCH' )
        #
        ## hide window action
        hideAction = QAction( self )
        hideAction.setShortcut( 'Esc' )
        hideAction.triggered.connect( self.hideMe )
        self.addAction( hideAction )

    def hideMe( self ):
        self.setVisible( False )

    def paintEvent( self, evt ):
        colorNames = self.parent.cwt.getColorNames( )
        numCols = int( numpy.sqrt( len( colorNames ) * 1.0 ) ) + 1 # candidate number of cols
        numRows, rem = divmod( len( colorNames ), numCols )
        if rem != 0:
            numRows += 1
        allHsvs = self.parent.getTransformedHsvs( )
        painter = QPainter( self )
        painter.setRenderHint( QPainter.Antialiasing )
        #
        ## now set the image
        width = 170 * numCols
        height = 170 * numRows
        self.setFixedSize( width, height )
        image = QImage( width, height, QImage.Format_ARGB32 )
        image.fill( QColor( "white" ).rgb( ) )
        painter.drawImage( 0, 0, image )
        #
        ## now do your plotting
        color = QColor( )
        brush = QBrush( )
        for idx, tup in enumerate( allHsvs ):
            row, col = divmod( idx, numCols )
            h, s, v = tup
            color.setHsvF( h, s, v, 1.0 )
            brush.setColor( color )
            painter.fillRect( 10 + 170 * col, 10 + 170 * row, 150, 150, color )
        font = QFont( )
        font.setFamily( 'Alef' )
        font.setPointSize( 14 )
        font.setBold( True )
        painter.setFont( font )
        pen = QPen( )
        pen.setColor( QColor( "black" ) )
        painter.setPen( pen )
        for idx, colorname in enumerate( colorNames ):
            row, col = divmod( idx, numCols )
            painter.drawText( QRect( 10 + 170 * col, 10 + 170 * row, 150, 150 ),
                              Qt.AlignCenter, colorname )

class ReadmeWidget( QWidget ):
    def __init__( self, parent ):
        super( ReadmeWidget, self ).__init__( parent )
        self.parent = parent
        self.setStyleSheet('font-family: Alef;')
        layout = QVBoxLayout( )
        self.setLayout( layout )
        qf = QFont( )
        qf.setFamily( 'Alef' )
        qf.setPointSize( 12 )
        qfm = QFontMetrics( qf )
        width = qfm.boundingRect( ''.join(['A'] * 55)).width()
        self.setFixedWidth( width )
        self.setFixedHeight( 600 )
        myTextArea = QTextEdit( )
        myTextArea.setReadOnly( True )
        myTextArea.setHtml( open( 'resources/docs/README.html', 'r').read( ) )
        layout.addWidget( myTextArea )
        self.hide( )
        #
        ##
        self.setWindowFlags( Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint | Qt.Window )
        self.setSizePolicy( QSizePolicy.Fixed, QSizePolicy.Fixed )
        self.setWindowTitle( 'README' )
        escAction = QAction( self )
        escAction.setShortcut( 'Esc' )
        escAction.triggered.connect( self.hideMe )
        self.addAction( escAction )

    def hideMe( self ):
        self.hide( )
        self.parent.parent.setEnabled( True )

    def readMe( self ):
        self.show( )
        self.parent.parent.setEnabled( False )

    def closeEvent( self, evt ):
        self.hideMe( )


class AboutmeWidget( QWidget ):
    def __init__( self, parent ):
        super( AboutmeWidget, self ).__init__( parent )
        self.parent = parent
        self.setStyleSheet('font-family: Alef;')
        layout = QVBoxLayout( )
        self.setLayout( layout )
        qf = QFont( )
        qf.setFamily( 'Alef' )
        qf.setPointSize( 12 )
        qfm = QFontMetrics( qf )
        width = qfm.boundingRect( ''.join(['A'] * 45)).width()
        self.setFixedWidth( width )
        self.setFixedHeight( 300 )
        myTextArea = QTextEdit( )
        myTextArea.setReadOnly( True )
        myTextArea.setHtml( open( 'resources/docs/ABOUT.html', 'r').read( ) )
        layout.addWidget( myTextArea )
        self.hide( )
        #
        ##
        self.setWindowFlags( Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint | Qt.Window )
        self.setSizePolicy( QSizePolicy.Fixed, QSizePolicy.Fixed )
        self.setWindowTitle( 'ABOUT' )
        escAction = QAction( self )
        escAction.setShortcut( 'Esc' )
        escAction.triggered.connect( self.hideMe )
        self.addAction( escAction )

    def hideMe( self ):
        self.hide( )
        self.parent.parent.setEnabled( True )

    def aboutTool( self ):
        self.show( )
        self.parent.parent.setEnabled( False )

    def closeEvent( self, evt ):
        self.hideMe( )
        
class ColorWheelMenuBar( QWidget ):
    def __init__(self, parent ):
        super(ColorWheelMenuBar, self).__init__( )
        self.parent = parent
        #
        self.readmeWindow = ReadmeWidget( self )
        self.aboutmeWindow = AboutmeWidget( self )
        #
        fileMenu = self.parent.menuBar().addMenu( '&File' )
        self.saveAction = fileMenu.addAction('&Save CSS' )
        openAction = fileMenu.addAction('&Open CSS' )
        openURLAction = fileMenu.addAction('&Open URL CSS')
        quitAction = fileMenu.addAction( '&Quit' )
        screenshotAction = fileMenu.addAction( '&Screenshot' )
        #
        opsMenu = self.parent.menuBar().addMenu( '&Operations' )
        showExpandedColorSwatchAction = opsMenu.addAction('&Expanded Color Swatch' )
        self._expandedColorSwatch = ColorWheelExpandedColorSwatch( parent )
        transformAction = opsMenu.addAction('&Set Transform')
        snapBackAction = opsMenu.addAction('&Snap Back')
        removeColorAction = opsMenu.addAction( '&Remove Color' )
        #
        helpMenu = self.parent.menuBar().addMenu( '&Help' )
        readmeAction = helpMenu.addAction( '&Readme' )
        aboutAction = helpMenu.addAction( '&About' )
        #
        ## actions
        self.saveAction.setShortcut('Shift+Ctrl+S')
        self.saveAction.triggered.connect( self.saveCSSFile )
        openAction.setShortcut('Shift+Ctrl+O')
        openAction.triggered.connect( self.openCSSFile )
        openURLAction.setShortcut('Shift+Ctrl+U')
        openURLAction.triggered.connect( self.openCSSURLFile )
        screenshotAction.setShortcut( 'Shift+Ctrl+1' )
        screenshotAction.triggered.connect( self.parent.takeScreenshot )
        quitAction.setShortcut( 'Ctrl+Q' )
        quitAction.triggered.connect( qApp.quit )
        readmeAction.triggered.connect( self.readmeWindow.readMe )
        aboutAction.triggered.connect( self.aboutmeWindow.aboutTool )
        #
        showExpandedColorSwatchAction.setShortcut( 'Shift+Ctrl+W' )
        showExpandedColorSwatchAction.triggered.connect( self.expandColorSwatchAction )
        snapBackAction.setShortcut( 'Ctrl+Y' )
        snapBackAction.triggered.connect( self.parent.cws.snapBack )
        transformAction.setShortcut( 'Shift+Ctrl+T' )
        transformAction.triggered.connect( self.parent.cws.setTransform )
        removeColorAction.setShortcut( 'Ctrl+Z' )
        removeColorAction.triggered.connect( self.parent.removeColor )
        
    def paintEvent( self, evt ):
        self._expandedColorSwatch.update( )
        
    def enableSaveAction( self ):
        self.saveAction.setEnabled( True )
        
    def disableSaveAction( self ):
        self.saveAction.setEnabled( False )

    def expandColorSwatchAction( self ):
        if len(self.parent.cwt.getColorNames( )) <= 1:
            return
        if not self._expandedColorSwatch.isVisible( ):
            self._expandedColorSwatch.setVisible( True )
            
    def openCSSURLFile( self ):
        while(True):
            myURL, ok = QInputDialog.getText( self, 'Open CSS URL. Can end by pressing cancel or by putting in blank.',
                                              "URL:", QLineEdit.Normal )
            if not ok:
                return
            myURL = myURL.strip()
            if len( myURL ) == 0:
                return
            status = (myURL.startswith('http://') or myURL.startswith('https://'))
            status = status and myURL.endswith('.css')
            if status:
                break
        css = None
        try:
            css = cssutils.parseURL( myURL )
            self.parent.pushNewColorsFromCSS( css )
        except ValueError:
            error = QErrorMessage( )
            
    def openCSSFile( self ):
        while( True ):
            fname = str( QFileDialog.getOpenFileName( self, 'Open CSS File',
                                                      #os.path.expanduser( __file__ ),
                                                      os.path.expanduser( '~' ),
                                                      filter = "*.css" ) )
            if fname.lower().endswith('.css') or len( os.path.basename( fname ) ) == 0:
                break
        if fname.lower().endswith('.css'):
            css = cssutils.parseFile( fname )
            try:
                self.parent.pushNewColorsFromCSS( css )
            except ValueError:
                error = QErrorMessage()
                message = ' '.join([ 
                    "Error, do not have an unique set of colors defined here."
                    "Problem with file %s." % fname,
                    "Please try again with another CSS file." ])
                error.showMessage( message )
                error.exec_()

    def saveCSSFile( self ):
        #
        ## first perform the transform
        self.parent.cws.setTransform( )
        #
        ##
        colorNames = self.parent.cwt.getColorNames()
        if len(colorNames) != len(set(colorNames)):
            return
        while( True ):
            fname = str( QFileDialog.getSaveFileName( self, 'Save CSS File',
                                                      os.path.expanduser( '~' ),
                                                      filter = "*.css" ) )
            if fname.lower().endswith('.css') or len( os.path.basename( fname ) ) ==0:
                break
        if fname.lower().endswith( '.css' ):
            colorNameDict = self.parent.cwt.getColorNamesDict( )
            with open(fname, 'w') as openfile:
                for key in sorted( colorNameDict ):
                    openfile.write('.%s {\n' % key )
                    openfile.write('\tbackground: %s;\n' % colorNameDict[ key ] )
                    openfile.write('}\n\n')
