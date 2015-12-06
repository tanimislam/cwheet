#!/usr/bin/env python

import pylab, numpy
from matplotlib.patches import Circle, Arrow

def draw_circle_harmony( ):
    ax = pylab.axes( )
    ax.set_aspect('equal')
    pylab.xlim(-1,1)
    pylab.ylim(-1,1)
    pylab.axis('off')
    #
    ##
    ax.add_patch(Circle((0,0), radius = 0.5, linewidth = 6,
                        linestyle = 'dashed', facecolor = 'white'))
    angles = numpy.radians(18 + numpy.linspace(0, 360, 6)[:-1])
    for angle in angles:
        ax.add_patch(Circle((0.5*numpy.cos(angle), 0.5*numpy.sin(angle)),
                            radius = 0.15, linewidth = 4, facecolor = 'white'))
    pylab.savefig('circle_harmony.svg', bbox_inches = 'tight')
    pylab.close( )

def draw_line_harmony( ):
    ax = pylab.axes( )
    ax.set_aspect('equal')
    pylab.xlim(-1,1)
    pylab.ylim(-1,1)
    pylab.axis('off')
    #
    ##
    angle = numpy.radians( 30.0 )
    maxrad = 0.8
    radii = numpy.linspace( -maxrad, maxrad, 4 )
    #
    ## stupid hack to add a line as a patch
    ## if I add a line as a Line2D, then always appears on top :(
    ax.add_patch(Arrow( -maxrad * numpy.cos(angle),
                        -maxrad * numpy.sin(angle),
                        2 * maxrad * numpy.cos(angle),
                        2 * maxrad * numpy.sin(angle), width = 0,
                        linestyle = 'dashed', linewidth = 6, color = 'gray' ))
    for radius in radii:
        ax.add_patch(Circle((radius * numpy.cos(angle),
                             radius * numpy.sin(angle)),
                            radius = 0.15, linewidth = 4, facecolor = 'white'))
    pylab.savefig('line_harmony.svg', bbox_inches = 'tight')
    pylab.close( )
               
    
if __name__=='__main__':
    draw_circle_harmony( )
    draw_line_harmony( )
