#!/usr/bin/env python

import os, sys, logging
from PyQt4.QtGui import QApplication
from optparse import OptionParser
from cwheet.cwAnims import OperationSliderAnimation, OperationAnimation

if __name__=='__main__':
    parser = OptionParser()
    parser.add_option('--dohue', dest='do_hue', action='store_true', default = False,
                      help = 'If chosen, do a HUE transform movie' )
    parser.add_option('--dosat', dest='do_sat', action='store_true', default = False,
                      help = 'If chosen, do a SATURATION transform movie' )
    parser.add_option('--doval', dest='do_val', action='store_true', default = False,
                      help = 'If chosen, do a VALUE transform movie' )
    parser.add_option('--debug', dest='do_debug_logging', action='store_true', default = False,
                      help = 'If chosen, do debug logging.')
    opts, args = parser.parse_args()
    if len(filter( lambda tok: tok is True, ( opts.do_hue, opts.do_sat, opts.do_val ) ) ) != 1:
        parser.parse_args(['-h'])
    if opts.do_debug_logging:
        logfile =  os.path.join( os.path.expanduser('~/temp'), 'debug.log' )                                 
        logging.basicConfig( filename = logfile, level = logging.DEBUG )
    #
    ##
    app = QApplication([])
    if opts.do_hue:
        osa = OperationSliderAnimation( OperationAnimation.HUETRANSFORM )
    elif opts.do_sat:
        osa = OperationSliderAnimation( OperationAnimation.SATURATIONTRANSFORM )
    else:
        osa = OperationSliderAnimation( OperationAnimation.VALUETRANSFORM )
    osa.show( )
    sys.exit( app.exec_( ) )
