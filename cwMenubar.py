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
        self.prevWidth = -1
        self.prevHeight = -1
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
        numCols = int( numpy.sqrt( len( colorNames ) * 1.0 ) ) # candidate number of cols
        if len( colorNames ) % numCols != 0:
            numCols += 1
        numRows, rem = divmod( len( colorNames ), numCols )
        if rem != 0:
            numRows += 1
        print 'GOT HERE IN PAINT!', len( colorNames ), numRows, numCols
        allHsvs = self.parent.getTransformedHsvs( )
        painter = QPainter( self )
        painter.setRenderHint( QPainter.Antialiasing )
        #
        ## now set the image
        width = 170 * numCols
        height = 170 * numRows
        if width != self.prevWidth or height != self.prevHeight:
            print 'GOT HERE!'
            self.setFixedSize( width, height )
            image = QImage( width, height, QImage.Format_ARGB32 )
            image.fill( QColor( "white" ).rgb( ) )
            painter.drawImage( 0, 0, image )
            self.prevWidth = width
            self.prevHeight = height
        #
        ## now do your plotting
        color = QColor( )
        brush = QBrush( )
        for idx, tup in enumerate( allHsvs ):
            row, col = divmod( idx, numCols )
            h, s, v = tup
            color.setHsvF( h, s, v, 1.0 )
            brush.setColor( color )
            painter.setBrush( brush )
            painter.drawRect( 10 + 170 * row, 10 + 170 * col, 150, 150 )
        font = QFont( )
        font.setFamily( 'Alef' )
        font.setPointSize( 12 )
        font.setBold( True )
        painter.setFont( font )
        pen = QPen( )
        pen.setColor( QColor( "black" ) )
        painter.setPen( pen )
        for idx, colorname in enumerate( colorNames ):
            row, col = divmod( idx, numCols )
            painter.drawText( QRect( 10 + 170 * row, 10 + 170 * col, 150, 150 ),
                              Qt.AlignCenter, colorname )
        

class ColorWheelMenuBar( QMenuBar ):
    def __init__(self, parent ):
        super(ColorWheelMenuBar, self).__init__( parent )
        self.parent = parent
        #
        fileMenu = self.addMenu( '&File' )
        self.saveAction = fileMenu.addAction('&Save CSS' )
        openAction = fileMenu.addAction('&Open CSS' )
        openURLAction = fileMenu.addAction('&Open URL CSS')
        #
        opsMenu = self.addMenu( '&Operations' )
        showExpandedColorSwatchAction = opsMenu.addAction('&Expanded Color Swatch' )
        self._expandedColorSwatch = ColorWheelExpandedColorSwatch( parent )
        #
        helpMenu = self.addAction( '&Help' )
        aboutMenu = self.addAction( '&About' )
        #
        ## actions
        self.saveAction.setShortcut('Shift+Ctrl+S')
        self.saveAction.triggered.connect( self.saveCSSFile )
        openAction.setShortcut('Shift+Ctrl+O')
        openAction.triggered.connect( self.openCSSFile )
        openURLAction.setShortcut('Shift+Ctrl+U')
        openURLAction.triggered.connect( self.openCSSURLFile )
        showExpandedColorSwatchAction.triggered.connect( self.expandColorSwatchAction )
        

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
        except ValueError:
            error = QErrorMessage( )
            
            
                                              

    def openCSSFile( self ):
        while( True ):
            fname = str( QFileDialog.getOpenFileName( self, 'Open CSS File',
                                                      os.path.expanduser( '~' ),
                                                      filter = "*.css" ) )
            if fname.lower().endswith('.css') or len( os.path.basename( fname ) ) == 0:
                break
        if fname.lower().endswith('.css'):
            css = cssutils.parseFile( fname )
            try:
                colorNamesDict = cwResources.getBackgroundColorDict( css )
                colorLabels = sorted( colorNamesDict.keys() )
                colors = [ ]
                self.parent.cws.snapBack( )
                for name in colorLabels:
                    colorName = colorNamesDict[ name ]
                    color = QColor( colorName )
                    h, s, v, a = color.getHsvF( )
                    colors.append([ h, s, v ])
                self.parent.pushNewColors( colors )
                self.parent.cwt.pushData( colorLabels )
                self.parent.update( )
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
