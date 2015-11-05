from PyQt4.QtGui import *
from PyQt4.QtCore import *
import os, sys, glob

class ColorWheelResource( object ):
    class __ColorWheelResource(object):
        def __init__(self):
            mainPath = os.path.join( os.path.dirname( os.path.abspath(__file__) ), 'resources' )
            self._styleSheets = {}
            self._fontNames = set([])
            fontNames = []
            for cssFile in glob.glob( os.path.join( mainPath, 'css', '*.css' ) ):
                keyName = os.path.basename( cssFile ).replace('.css', '').strip()
                qFile = QFile( cssFile )
                qFile.open( QIODevice.ReadOnly )                
                self._styleSheets[ keyName ] = QString( qFile.readAll( ) )
                qFile.close()
            for fontFile in glob.glob( os.path.join( mainPath, 'fonts', '*.ttf' ) ):
                fontName = os.path.basename( fontFile ).replace('.ttf', '').strip()
                QFontDatabase.addApplicationFont( fontFile )
            numFonts = len( glob.glob( os.path.join( mainPath, 'fonts', '*.ttf' ) ) )
            ffams = set(reduce(lambda x, y: x + y, [ list( QFontDatabase.applicationFontFamilies(idx) ) for
                                                     idx in xrange(numFonts) ] ) )
            self._fontNames = set( [ str( tok ) for tok in ffams ] )

        def getStyleSheets( self ):
            return sorted( self._styleSheets.keys() )

        def getFontNames( self ):
            return sorted( self._fontNames )

        def getStyleSheet( self, name ):
            assert( name in self._styleSheets )
            return self._styleSheets[ name ]

    _instance = None

    def __new__(cls ):
        if not ColorWheelResource._instance:
            ColorWheelResource._instance = ColorWheelResource.__ColorWheelResource( )
        return ColorWheelResource._instance

if __name__=='__main__':
    app = QApplication(sys.argv)
    cwr = ColorWheelResource()
    print 'fonts: %s' % cwr.getFontNames()
    print 'stylesheets: %s' % cwr.getStyleSheets()
    sys.exit()
