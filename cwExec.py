#!/usr/bin/env python

import os, sys, logging
from cwheet.cwAll import ColorWheelAll
from PyQt4.QtGui import *
from optparse import OptionParser


if __name__=='__main__':
    parser = OptionParser( )
    parser.add_option('--debug', dest='do_debug', action='store_true', default = False,
                      help = 'If chosen, print out debug messages to stdout.')
    opts, args = parser.parse_args( )
    if opts.do_debug:
        logging.getLogger().setLevel( logging.DEBUG )
    app = QApplication([])
    cwa = ColorWheelAll(mainDiameter = 325 )
    cwa.show()
    sys.exit( app.exec_())
