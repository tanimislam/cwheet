from PyQt4.QtGui import *
from PyQt4.QtCore import *
import cssutils, os, subprocess, cwResources

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
        #
        helpMenu = self.addAction( '&Help' )
        #
        ## actions
        self.saveAction.setShortcut('Shift+Ctrl+S')
        self.saveAction.triggered.connect( self.saveCSSFile )
        openAction.setShortcut('Shift+Ctrl+O')
        openAction.triggered.connect( self.openCSSFile )

    def enableSaveAction( self ):
        self.saveAction.setEnabled( True )
        
    def disableSaveAction( self ):
        self.saveAction.setEnabled( False )

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
