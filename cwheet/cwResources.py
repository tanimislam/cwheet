from PyQt4.QtGui import *
from PyQt4.QtCore import *
import os, sys, glob, cssutils
from functools import reduce
from distutils.spawn import find_executable
from . import resourcePath

def find_avconv_handbrake( ):
    avconv_exec = None
    for exc in ( 'avconv', 'ffmpeg' ):
        avconv_exec = find_executable( exc )
        if avconv_exec is not None: break
    if avconv_exec is None: return None

    handbrake_exec = find_executable( 'HandBrakeCLI' )
    if handbrake_exec is None: return None
    return { 'avconv' : avconv_exec,
             'handbrake' : handbrake_exec }

def isValidColorName( mystr ):
    return mystr.lower() in QColor.colorNames( )

def isValidColorString( mystr ):
    if len(mystr) != 7:
        return False
    if not mystr.startswith('#'):
        return False
    mychars = set([ tok for tok in mystr[1:] ])
    if len(mychars - set(['%d' % num for num in range(10) ] + ['A','B','C','D','E','F' ])) != 0:
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
            self._styleSheets = {}
            self._fontNames = set([])
            #self._colorwheel = [  QColor(name) for name in ( '#E5EDE9', '#EDE6CE', '#EDDFEB',
            #                                                 '#F1EDFE', '#CCD9FD', '#F9EBFD' ) ]
            self._colorwheel = [ QColor(num, num, num) for num in range(240, 210, -5) ]
            self._icons = {}
            fontNames = []
            for cssFile in glob.glob( os.path.join( resourcePath, 'css', '*.css' ) ):
                keyName = os.path.basename( cssFile ).replace('.css', '').strip()
                qFile = QFile( cssFile )
                qFile.open( QIODevice.ReadOnly )                
                self._styleSheets[ keyName ] = str( qFile.readAll( ) )
                qFile.close()
            #
            for fontFile in glob.glob( os.path.join( resourcePath, 'fonts', '*.ttf' ) ):
                fontName = os.path.basename( fontFile ).replace('.ttf', '').strip()
                QFontDatabase.addApplicationFont( fontFile )
            numFonts = len( glob.glob( os.path.join( resourcePath, 'fonts', '*.ttf' ) ) )
            #
            for iconFile in glob.glob( os.path.join( resourcePath, 'icons', '*.png' ) ):
                iconName = os.path.basename( iconFile ).replace( '.png', '').strip( )
                self._icons[ iconName ] = QIcon( iconFile )
            ffams = set(reduce(lambda x, y: x + y, [ list( QFontDatabase.applicationFontFamilies(idx) ) for
                                                     idx in range(numFonts) ] ) )
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

        def getIcons( self ):
            return sorted( self._icons )

        def getIcon( self, name ):
            assert( name in self._icons )
            return self._icons[ name ]

    _instance = None

    def __new__(cls ):
        if not ColorWheelResource._instance:
            ColorWheelResource._instance = ColorWheelResource.__ColorWheelResource( )
        return ColorWheelResource._instance

if __name__=='__main__':
    app = QApplication(sys.argv)
    cwr = ColorWheelResource()
    print('fonts: %s' % cwr.getFontNames())
    print('stylesheets: %s' % cwr.getStyleSheets())
    sys.exit()
