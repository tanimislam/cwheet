from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys, math
from cwResources import ColorWheelResource

class ColorWheelValues( QWidget ):
    def __init__(self, parent ):
        super( QWidget, self).__init__( parent )
        self.parent = parent
        self.setFixedSize( 280, 1520 )
        self.image = None

    def paintEvent( self, evt ):
        qs = self.size( )
        width = qs.width()
        height = qs.height()
        #
        xStart = 10
        xEnd = qs.width() - 10
        xSpan = qs.width() - 20
        if self.image is None:
            self.image = QImage( qs.width(), qs.height(), QImage.Format_ARGB32 )
            self.image.fill( QColor( "white" ).rgb() )
        #
        spanHeight = height - 20
        numEls = int( spanHeight / 15 ) + 1
        #
        painter = QPainter( self )
        painter.setRenderHint( QPainter.Antialiasing )
        painter.drawImage(0, 0, self.image )
        pen = QPen( )
        color = QColor( )
        allHsvs = self.parent.getTransformedHsvs()
        if self.parent.currentIndex == -1:
            currentIndex = len( self.parent.hsvs ) - 1
        else:
            currentIndex = self.parent.currentIndex
        
        pen.setWidth( 1 )
        for idx, tup in enumerate( allHsvs ):
            h, s = tup[:2]
            for xpos in range( xStart, xEnd + 1):
                v = QStyle.sliderValueFromPosition( 0, 100, xpos - xStart, xSpan ) * 0.01
                color.setHsvF( h, s, v, 0.5 )
                pen.setColor( color )
                painter.setPen( pen )
                painter.drawLine( xpos, 20 + idx * 30 - 10, xpos, 20 + idx * 30 + 10 )
        
        pen.setColor( QColor( "red" ) )
        pen.setWidth( 2.5 )
        painter.setPen( pen )
        for idx, tup in enumerate(allHsvs):
            if idx == currentIndex:
                continue            
            h, s, v = tup
            vInt = int( 100 * v )
            xDiff = QStyle.sliderPositionFromValue( 0, 100, vInt, xSpan )
            qp = QPoint( xStart + xDiff, 20 + idx * 30 )
            painter.drawEllipse( qp, 5, 5 )
            painter.drawText( qp + QPoint( 5, 10 ), "%d" % ( idx + 1 ) )
            painter.drawLine( xStart, 20 + idx * 30, xEnd, 20 + idx * 30 )

        pen.setColor( QColor( "orange" ) )
        painter.setPen( pen )
        for idx, tup in enumerate(allHsvs):
            if idx != currentIndex:
                continue
            h, s, v = tup
            loc = idx % numEls
            vInt = int( 100 * v )
            xDiff = QStyle.sliderPositionFromValue( 0, 100, vInt, xSpan )
            qp = QPoint( xStart + xDiff, 20 + loc * 30 )
            painter.drawEllipse( qp, 5, 5 )
            painter.drawText( qp + QPoint( 5, 10 ), "%d" % ( idx + 1 ) )
            painter.drawLine( xStart, 20 + idx * 30, xEnd, 20 + idx * 30 )

class ColorWheelBar( QWidget ):
    def __init__(self, parent, mainWidth = 30, mainDiameter = 256 ):
        QWidget.__init__(self, parent)
        
        self.parent = parent
        #self.setObjectName( 'color0Widget' )
        #self.setStyleSheet( _cwr.getStyleSheet( 'qwidget' ) )

        # this is the size of the pixel wheel
        self.height = int( 1.1 * mainDiameter )
        self.width = int( 1.5 * mainWidth )
        self.setMinimumSize( self.width, self.height )
        self.setMaximumSize( self.width, self.height )
        self.mainDiameter = mainDiameter
        self.xStart = int( 0.5 * self.width - 0.5 * mainWidth )
        self.xEnd = int( 0.5 * self.width + 0.5 * mainWidth )

        # these are used for the current value selection image
        self.bMouseDown = False      

        # center of the widget
        self.center = QPoint( 0.5 * self.width, 0.5 * self.height )
        

    def paintEvent(self, evt):
        painter = QPainter( self )
        painter.setRenderHint( QPainter.Antialiasing )
        pen = QPen()
        pen.setWidth( 1 )
        #
        h, s, v = self.parent.getTransformedHsvs()[ self.parent.currentIndex ]
        color = QColor()
        for y in range( self.height ):
            qp = QPoint( 0.5 * self.width, y)
            val = self._getValueColor( qp )
            if val < 0:
                continue
            if val > 1:
                continue
            color.setHsvF(h, s, val, 1.0 )
            pen.setColor( color )
            painter.setPen( pen )
            painter.drawLine( self.xStart, y, self.xEnd, y )

        pen.setWidth( 2 )
        pen.setColor( Qt.red )
        painter.setPen( pen )
        valPoint = QPoint( 0.5 * self.width, 0.5 * self.height + ( 0.5 - v ) * self.mainDiameter )
        painter.drawEllipse( valPoint, 5, 5 )
        painter.drawLine( self.xStart, valPoint.y(), self.xEnd, valPoint.y() )
            
    def _getValueColor( self, qp ):
        qdiff = self.center - qp
        val = ( qdiff.y() + self.mainDiameter * 0.5 ) * 1.0 / self.mainDiameter
        return val

    def _setValSat( self, val ):
        self.parent.hsvs[ self.parent.currentIndex ][-1] = val
        self.parent.update()

    def mousePressEvent( self, evt ):
        self.bMouseDown = True
        self._alterValue( QPoint( evt.x(), evt.y() ) )

    def mousereleaseEvent( self, evt ):
        self.bMouseDown = False

    def mouseMoveEvent( self, evt ):
        if self.bMouseDown:
            self._alterValue( QPoint( evt.x(), evt.y() ) )

    def _alterValue( self, qp ):
        val = self._getValueColor( qp )
        if val < 0:
            val = 0.0
        elif val > 1:
            val = 1.0
        self.valPoint = QPoint( 0.5 * self.width, 0.5 * self.height + 0.5 * self.mainDiameter -
                                val * self.mainDiameter )
        self._setValSat( val )
    
class ColorWheelWidget( QWidget ):
    def __init__(self, parent, mainDiameter = 256 ):
        super(QWidget, self).__init__( parent )
        self.parent = parent
        #self.setObjectName( 'color0Widget' )
        #self.setStyleSheet( _cwr.getStyleSheet( 'qwidget' ) )
        self.setMouseTracking( True )

        # this is the pixel diameter of the actual color wheel
        self.dim = int( 1.1 * mainDiameter )
        self.setMinimumSize( self.dim, self.dim )
        self.setMaximumSize( self.dim, self.dim )

        # sets the radius of this widget
        self.master_radius = int(0.5 * mainDiameter) + 1
        self.dmax = 1.0

        # the color wheel image, only needs to be generated once
        self.image = QImage( self.dim, self.dim, QImage.Format_ARGB32 )
        self.image.fill( QColor( Qt.white ).rgb() )
        
        # center of this widget
        self.center = QPoint( 0.5 * self.dim, 0.5 * self.dim )

        # these are used for the current color selection image
        self.bMouseDown = False
        
        for y in range( self.dim ):
            for x in range( self.dim ):
                qp = QPoint(x, y)
                d = self.getDist(qp, self.center) / self.master_radius
                if d <= 1:
                    color = QColor()
                    hue = self.getHue( qp )
                    color.setHsvF(hue, d, 1.0, 1.0)
                    self.image.setPixel(x,y, color.rgba())
                else:
                    color = QColor()
                    color.setAlpha(1)
                    self.image.setPixel(x, y, Qt.white)

    def getDist(self, xycoord, orig ):
        qdiff = xycoord - orig
        return math.sqrt(qdiff.x()**2 + qdiff.y()**2)

    def getHue(self, qp):
        qdiff = qp - self.center
        theta = math.atan2( -qdiff.y(), qdiff.x() )
        if theta < 0:
            theta += 2 * math.pi
        return theta / (2 * math.pi )

    def rescaleWheel(self, dmax = 1.0 ):
        assert( dmax > 0 )
        assert( dmax <= 1)
        self.dmax = dmax
        self.image.fill( QColor( Qt.white ).rgb() )
        for y in xrange( self.dim ):
            for x in xrange( self.dim ):
                qp = QPoint(x, y)
                d = self.getDist(qp, self.center) / self.master_radius * self.dmax
                if d <= dmax:
                    color = QColor()
                    hue = self.getHue( qp )
                    color.setHsvF(hue, d, 1.0, 1.0)
                    self.image.setPixel(x, y, color.rgba())
                else:
                    color = QColor()
                    color.setAlpha(1)
                    self.image.setPixel(x, y, Qt.white)
        self.parent.update()

    def paintEvent( self, evt ):
        painter = QPainter( self )
        painter.setRenderHint( QPainter.Antialiasing )
        pen = QPen()
        pen.setColor( Qt.black )
        pen.setWidth( 2 )
        painter.setPen( pen )

        painter.drawImage( 0, 0, self.image )
        painter.drawEllipse( self.center, self.master_radius, self.master_radius )
        pen.setColor( Qt.red )
        painter.setPen( pen )
        if self.parent.currentIndex == -1:
            currentIndex = len( self.parent.hsvs ) - 1
        else:
            currentIndex = self.parent.currentIndex
        for idx, tup in enumerate( self.parent.getTransformedHsvs( ) ):
            if idx == currentIndex:
                continue
            hv, sv, vv = tup
            theta = 2 * math.pi * hv
            svf = min(1.0, sv / self.dmax )
            huePoint = QPointF( svf * self.master_radius * math.cos( theta ),
                                -svf * self.master_radius * math.sin( theta ) ) + self.center
            painter.drawEllipse( huePoint, 5, 5 )
            painter.drawText( huePoint + QPointF( 5.0, 10.0), "%d" % ( idx + 1 ) )

        pen.setColor( Qt.blue )
        painter.setPen( pen )
        for idx, tup in enumerate( self.parent.getTransformedHsvs( ) ):
            if idx != currentIndex:
                continue
            hv, sv, vv = tup
            theta = 2 * math.pi * hv
            svf = min(1.0, sv / self.dmax )
            huePoint = QPointF( svf * self.master_radius * math.cos( theta ),
                                -svf * self.master_radius * math.sin( theta ) ) + self.center
            painter.drawEllipse( huePoint, 5, 5 )
            painter.drawText( huePoint + QPointF( 5.0, 10.0), "%d" % ( idx + 1 ) )
            
    def mousePressEvent( self, evt ):
        if evt.button() == Qt.RightButton: # create a new point at that location
            h, s = self._getNewHueSat( evt.pos() )
            self._addColor(h, s)
        else:            
            self._alterColor( evt.pos() )
        self.bMouseDown = True
            
    def mouseReleaseEvent( self, evt ):
        self.bMouseDown = False

    def mouseMoveEvent( self, evt ):
        if self.bMouseDown:
            self._alterColor( evt.pos() )

    def _setHueSat(self, h, s ):
        self.parent.hsvs[ self.parent.currentIndex ][:2] = [h, s]
        self.parent.update()

    def _getNewHueSat(self, qp):
        d = self.getDist( qp, self.center) / self.master_radius * self.dmax
        if d <= self.dmax:
            hue = self.getHue( qp )
            return hue, d
        else:
            qdiff = qp - self.center
            qdiff = qdiff * self.master_radius / math.sqrt( qdiff.x()**2 + qdiff.y()**2 )
            qpf = self.center + qdiff
            hue = self.getHue( qpf )
            return hue, self.dmax
            
    def _alterColor(self, qp):
        d = self.getDist( qp, self.center) / self.master_radius * self.dmax
        if d <= self.dmax:
            hue = self.getHue( qp )
            self._setHueSat( hue, d )
        else:
            qdiff = qp - self.center
            qdiff = qdiff * self.master_radius / math.sqrt( qdiff.x()**2 + qdiff.y()**2 )
            qpf = self.center + qdiff
            hue = self.getHue( qpf )
            self._setHueSat( hue, self.dmax )

    
    def _addColor(self, h = 0.0, s = 0.0):
        self.parent.hsvs.append( [ h, s, 1.0 ] )
        self.parent.cwt.addRow( )
        self.parent.currentIndex = -1
        self.parent.update( )
