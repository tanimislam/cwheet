from PyQt4.QtGui import *
from PyQt4.QtCore import *
import os, sys, glob, cssutils

def isValidColorName( mystr ):
    return mystr.lower() in QColor.colorNames( )

def isValidColorString( mystr ):
    if len(mystr) != 7:
        return False
    if not mystr.startswith('#'):
        return False
    mychars = set([ tok for tok in mystr[1:] ])
    if len(mychars - set(['%d' % num for num in xrange(10) ] + ['A','B','C','D','E','F' ])) != 0:
        return False
    return True

def _isvalidrule( rule ):
    if not isinstance(rule, cssutils.css.CSSStyleRule):
        return False
    if not isinstance(rule.style, cssutils.css.CSSStyleDeclaration):
        return False
    valid_children = filter(lambda child: isinstance(child, cssutils.css.Property) and
                            child.name == u'background', rule.style.children())
    if len( valid_children ) == 0:
        return False
    valid_child = valid_children[ 0 ]
    #
    ## check if I have a valid color
    cname = valid_child.value.lower()
    if isValidColorName( cname ):
        return True
    cname = cname.upper()
    return isValidColorString( cname )

def _getcolortuple( rule ):
    key = rule.selectorText.strip().replace('.', '')
    valid_child = filter(lambda child: isinstance(child, cssutils.css.Property) and
                         child.name == u'background', rule.style.children())[0]
    cname = valid_child.value.lower()  
    if cname in QColor.colorNames():  
        color = QColor( cname )
        return ( key, str( color.name() ).strip().upper() )
    return ( key, cname.upper() )

def getBackgroundColorDict( css ):
    validRules = filter( _isvalidrule, css.cssRules )
    colorTupleList = [ _getcolortuple( rule ) for rule in validRules ]
    if not canSaveColorDict( colorTupleList ):
        raise ValueError(' '.join([ "Error, do not have an unique set of colors defined here.",
                                    "Please try again with another source." ]))
    return dict( colorTupleList )

def canSaveColorDict( colorTupleList ):
    keys = zip(*colorTupleList)[0]
    if len(keys) != len(set(keys)):
        return False
    return True

class ColorWheelResource( object ):
    class __ColorWheelResource(object):
        def __init__(self):
            mainPath = os.path.join( os.path.dirname( os.path.abspath(__file__) ), 'resources' )
            self._styleSheets = {}
            self._fontNames = set([])
            self._colorwheel = [  QColor(name) for name in ( '#E5EDE9', '#EDE6CE', '#EDDFEB',
                                                             '#F1EDFE', '#CCD9FD', '#F9EBFD' ) ]
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

        def getColorWheel( self ):
            return self._colorwheel[:]

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
