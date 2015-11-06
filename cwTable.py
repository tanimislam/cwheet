from PyQt4.QtCore import *
from PyQt4.QtGui import *
import copy, time
from cwResources import ColorWheelResource, isValidColorString

class ColorWheelTableModel( QAbstractTableModel ):
    def __init__(self, parent = None ):
        super(ColorWheelTableModel, self).__init__(parent)
        self.colorNames = []
        self.headerData = [ 'index', 'name', 'color', 'swatch' ]
        self.parent = parent
        self._colorwheel = ColorWheelResource().getColorWheel()

    def pushData(self, newColorNames ):
        #
        ## first remove all rows that exist
        initRowCount = self.rowCount(None)
        self.beginRemoveRows( QModelIndex(), 0, initRowCount - 1 )
        self.colorNames = []
        self.endRemoveRows( )
        #
        ## now add in the data from tabledata
        self.beginInsertRows( QModelIndex(), 0, len( newColorNames ) - 1 )
        self.colorNames = copy.deepcopy( newColorNames )
        self.endInsertRows( )

    def rowCount(self, parent ):
        return len( self.colorNames )

    def columnCount(self, parent ):
        return len( self.headerData )

    def data(self, index, role ):
        if not index.isValid():
            return QVariant( )
        row = index.row()
        col = index.column()
        if role == Qt.BackgroundRole:
            if col < 3:
                return QBrush( self._colorwheel[ index.row() % 6 ] )
            else:
                hsvTrans = self.parent.getTransformedHsvs( )
                hv, sv, vv = hsvTrans[ row ]
                color = QColor( )
                color.setHsvF( hv, sv, vv, 1.0 )
                return QBrush( color )
        elif role != Qt.DisplayRole:
            return QVariant( )
        if col == 0:
            return QVariant( row + 1 )
        elif col == 1:
            return QVariant( self.colorNames[ row ] )
        elif col == 2:
            hsvTrans = self.parent.getTransformedHsvs( )
            hv, sv, vv = hsvTrans[ row ]
            color = QColor()
            color.setHsvF( hv, sv, vv, 1.0 )
            name = str( color.name() ).upper( )
            return QVariant( name )
        else:
            return QVariant( )

    def setData(self, index, value, role ):
        if not index.isValid():
            return
        row = index.row()
        col = index.column()
        if col == 0:
            return
        elif col == 1:
            self.colorNames[ row ] = str( value.toString() )
        elif col == 2:
            name = str( value.toString() )
            color = QColor( name )
            h, s, v, a = color.getHsvF()
            self.parent.hsvs[ row ] = [ h, s, v ]
            self.parent.update()

    def flags(self, index ):
        col = index.column()
        if col != 0:
            return Qt.ItemFlags( Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        else:
            return Qt.ItemFlags( Qt.ItemIsEnabled )

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant( self.headerData[col] )
        return QVariant( )

    def addRow( self, newColorName ):
        self.beginInsertRows( QModelIndex(), len( self.parent.hsvs ),
                              len( self.parent.hsvs ) )
        self.colorNames.append( newColorName )
        self.endInsertRows( )
        

    def subtractRow( self ):
        currIdx = self.parent.currentIndex
        if currIdx == -1:
            currIdx = len( self.parent.hsvs ) - 1
            self.colorNames.pop( )
        else:
            self.colorNames.pop( currIdx )
        self.beginRemoveRows( QModelIndex(), currIdx, currIdx )
        self.endRemoveRows( )

    def setColor( self, row, cname ):
        assert( row >= 0 )
        assert( row < len( self.parent.hsvs ) )
        color = QColor( cname )
        h, s, v, a = color.getHsvF()
        self.parent.hsvs[ row ] = [ h, s, v ]
        self.parent.update( )

    def getColor(self, row ):
        assert( row >= 0 )
        assert( row < len( self.parent.hsvs ) )
        h, s, v = self.parent.hsvs[ row ]
        color = QColor( )
        color.setHsvF(h, s, v, 1.0 )
        return str( color.name() ).upper() 

class ColorWheelTable(QTableView):
    def __init__(self, parent):
        super(QTableView, self).__init__( parent )
        self.parent = parent
        self.tm = ColorWheelTableModel( self.parent )
        self.setModel( self.tm )
        self.setItemDelegateForColumn(0, EntryDelegate( self ) )
        self.setItemDelegateForColumn(1, NameDelegate( self ) )
        self.setItemDelegateForColumn(2, HexColorDelegate( self ) )
        self.setItemDelegateForColumn(3, ColorBarDelegate( self ) )

        # set style
        cwr = ColorWheelResource()
        self.setStyleSheet( cwr.getStyleSheet( 'qtableview' ) )

        # show grid
        self.setShowGrid( True )

        # set fixed vertical headers
        self.verticalHeader().setResizeMode( QHeaderView.Fixed )
        self.horizontalHeader().setResizeMode( QHeaderView.Fixed )
        qf = self.horizontalHeader().font()
        qf.setBold( True )
        qf.setPointSize( 12 )
        self.horizontalHeader().setFont( qf )
        self.verticalHeader().setFont( qf )
        self.horizontalHeader().setDefaultAlignment( Qt.AlignLeft )

        # hide vertical header
        self.verticalHeader().setVisible( False )

        # disable sorting
        self.setSortingEnabled( False )

        # other stuff
        self.setSelectionBehavior( QTableView.SelectRows )
        
        # end button scroll to bottom
        toBotAction = QAction( self )
        toBotAction.setShortcut( 'End' )
        toBotAction.triggered.connect( self.scrollToBottom )
        self.addAction( toBotAction )

        # home button scroll to top
        toTopAction = QAction( self )
        toTopAction.setShortcut( 'Home' )
        toTopAction.triggered.connect( self.scrollToTop )
        self.addAction( toTopAction )

        # up one page
        upOnePageAction = QAction( self )
        upOnePageAction.setShortcut( 'PgUp' )
        upOnePageAction.triggered.connect( self.scrollUpOnePage )
        self.addAction( upOnePageAction )

        # down one page
        downOnePageAction = QAction( self )
        downOnePageAction.setShortcut( 'PgDown' )
        downOnePageAction.triggered.connect( self.scrollDownOnePage )
        self.addAction( downOnePageAction )

        # clear selection
        clearSelectionAction = QAction( self )
        clearSelectionAction.setShortcut( 'Ctrl+U' )
        clearSelectionAction.triggered.connect( self.clearSelection )
        self.addAction( clearSelectionAction )
        #
        ##
        self.clicked.connect( self.setSelectedColor )

        # now put in the name
        self.addRow( )

        # now do final resizing
        self.setColumnWidth( 0, 50 )
        self.setColumnWidth( 1, 90 )
        self.setColumnWidth( 2, 80 )
        self.setColumnWidth( 3, 80 )

        # now selection behavior, only rows, only a single row at a time
        self.setSelectionBehavior( QAbstractItemView.SelectRows )
        self.setSelectionMode( QAbstractItemView.SingleSelection )

    def addRow( self ):
        self.tm.addRow( 'default' )
        colorNames = self.getColorNames()
        if len(colorNames) != len(set(colorNames)):
            self.parent.cwmb.disableSaveAction( )
        else:
            self.parent.cwmb.enableSaveAction( )

    def subtractRow( self ):
        self.tm.subtractRow( )
        colorNames = self.getColorNames()
        if len(colorNames) != len(set(colorNames)):
            self.parent.cwmb.disableSaveAction( )
        else:
            self.parent.cwmb.enableSaveAction( )

    def scrollUpOnePage( self ):
        self.scrollContentsBy( 0, -self.size().height() )

    def scrollDownOnePage( self ):
        self.scrollContentsBy( 0, self.size().height() )

    def setSelectedColor( self, index ):
        if not index.isValid():
            return
        row = index.row( )
        self.parent.currentIndex = row
        self.parent.update( )

    def getColorNames( self ):
        return self.tm.colorNames[:]

    def getColorNamesDict( self ):
        return { self.tm.colorNames[ row ] : self.tm.getColor( row ) for
                 row in xrange( len( self.tm.colorNames ) ) }

    def pushData( self, colorNames ):
        assert(len( colorNames) == len(self.parent.hsvs) )
        self.tm.pushData( colorNames )

    #def mouseReleaseEvent( self, evt ):
    #    if evt.button() == Qt.RightButton:
    #        self.clearSelection()
        
class EntryDelegate(QItemDelegate):
    def __init__(self, owner):
        super(EntryDelegate, self).__init__(owner)

    def createEditor(self, parent, option, index):
        rowNumber = index.row()
        editor = QLabel( "%02d" % ( rowNumber + 1 ), parent )
        return editor

    def setEditorData(self, editor, index ):
        rowNumber = index.row()
        editor.setText( "%02d" % ( rowNumber + 1 ) )

class NameDelegate(QItemDelegate):
    def __init__(self, owner):
        super(NameDelegate, self).__init__(owner)

    def createEditor(self, parent, option, index):
        rowNumber = index.row()
        model = index.model()
        name = model.colorNames[ rowNumber ]
        editor = QLineEdit( name, parent )
        return editor

    def setEditorData(self, editor, index ):
        rowNumber = index.row()
        model = index.model()
        name = model.colorNames[ rowNumber ]
        editor.setText( name )

    def setModelData( self, editor, model, index ):
        candText = str( editor.text() ).strip()
        rowNumber = index.row( )
        currName = model.colorNames[ rowNumber ]
        if len(candText) == 0 or len(candText.split()) > 1:
            editor.setText( currName )
        else:
            model.colorNames[ rowNumber ] = candText

class HexColorDelegate(QItemDelegate):
    def __init__(self, owner):
        super(HexColorDelegate, self).__init__(owner)

    def createEditor(self, parent, option, index):
        rowNumber = index.row()
        model = index.model()
        hexColor = model.getColor( rowNumber )
        editor = QLineEdit( hexColor, parent )
        return editor

    def setEditorData(self, editor, index):
        rowNumber = index.row()
        model = index.model()
        hexColor = model.getColor( rowNumber )
        editor.setText( hexColor )

    def setModelData(self, editor, model, index):
        candText = str( editor.text() ).strip().upper()
        rowNumber = index.row( )
        model = index.model()
        currentColor = model.getColor( rowNumber )
        if len(candText) == '':
            editor.setText( currentColor )
            return
        if not isValidColorString( candText ):
            editor.setText( currentColor )
            return
        model.parent.cws.setTransform( )
        model.setColor( rowNumber, candText )

class ColorBarDelegate(QItemDelegate):
    def __init__(self, owner):
        super(ColorBarDelegate, self).__init__( owner )
        
    def createEditor( self, parent, option, index ):
        editor = QLabel( parent )
        return editor
