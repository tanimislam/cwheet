#!/usr/bin/env python

import pylab, numpy, re, math
from matplotlib.patches import Circle, Arrow, Arc
from matplotlib.lines import Line2D

def draw_circle_harmony( ):
    ax = pylab.axes( )
    ax.set_aspect('equal')
    pylab.xlim(-1,1)
    pylab.ylim(-1,1)
    pylab.axis('off')
    innerrad = 0.15
    #
    ##
    angles_deg = 18 + numpy.linspace(0, 360, 6)[:-1]
    angles = numpy.radians(18 + numpy.linspace(0, 360, 6)[:-1])
    theta = numpy.degrees( 2 * math.asin( innerrad / 1.0 ) )
    for angle in zip(angles):
        ax.add_patch(Circle((0.5*numpy.cos(angle), 0.5*numpy.sin(angle)),
                            radius = innerrad, linewidth = 4, facecolor = 'white'))

    for angle_start, angle_end in zip(angles_deg[:-1], angles_deg[1:]):
        angle1 = angle_start + theta
        angle2 = angle_end - theta
        ax.add_patch(Arc((0,0), width = 1.0, height = 1.0, angle = 0.0, theta1 = angle1,
                         theta2 = angle2, linestyle = 'dashed', linewidth = 6 ))

    angle_end = angles_deg[0] + 360
    angle_start = angles_deg[-1]
    angle1 = angle_start + theta
    angle2 = angle_end - theta
    ax.add_patch(Arc((0,0), width = 1.0, height = 1.0, angle = 0.0, theta1 = angle1,
                     theta2 = angle2, linestyle = 'dashed', linewidth = 6 ))
                         
                         
    pylab.savefig('circle_harmony.svg', bbox_inches = 'tight', transparent = True)
    pylab.close( )
    #
    ## now open file, remove all fill:#fffff to fill:none
    lines = [ line.replace('\n', '') for line in open('circle_harmony.svg', 'r') ]
    for idx in xrange(len(lines)):
        line = lines[idx]
        line = line.replace('fill:#ffffff', 'fill:none')
        lines[idx] = line
    with open('circle_harmony.svg', 'w') as openfile:
        for line in lines:
            openfile.write('%s\n'% line )
        

def draw_line_harmony( ):
    ax = pylab.axes( )
    ax.set_aspect('equal')
    pylab.xlim(-1,1)
    pylab.ylim(-1,1)
    pylab.axis('off')
    innerrad = 0.15
    numcircs = 4
    #
    ##
    angle = numpy.radians( 30.0 )
    maxrad = 0.8
    radii = numpy.linspace( -maxrad, maxrad, numcircs )
    #
    ##
    for idx1, idx2 in zip(range(numcircs)[:-1], range(numcircs)[1:]):
        rad1 = radii[idx1]
        rad2 = radii[idx2]
        xs = [ (rad1 + innerrad ) * numpy.cos( angle ), (rad2 - innerrad ) * numpy.cos( angle ) ]
        ys = [ (rad1 + innerrad ) * numpy.sin( angle ), (rad2 - innerrad ) * numpy.sin( angle ) ]
        ax.add_line( Line2D( xs, ys, linestyle = 'dashed', linewidth = 6, color = 'black' ) )
    #
    ## stupid hack to add a line as a patch
    ## if I add a line as a Line2D, then always appears on top :(
    #ax.add_patch(Arrow( -maxrad * numpy.cos(angle),
    #                    -maxrad * numpy.sin(angle),
    #                    2 * maxrad * numpy.cos(angle),
    #                    2 * maxrad * numpy.sin(angle), width = 0,
    #                    linestyle = 'dashed', linewidth = 6, color = 'gray' ))
    for radius in radii:
        ax.add_patch(Circle((radius * numpy.cos(angle),
                             radius * numpy.sin(angle)),
                            radius = innerrad, linewidth = 4, facecolor = 'white'))
    pylab.savefig('line_harmony.svg', bbox_inches = 'tight', transparent = True)
    pylab.close( )
    lines = [ line.replace('\n', '') for line in open('line_harmony.svg', 'r') ]
    for idx in xrange(len(lines)):
        line = lines[idx]
        line = line.replace('fill:#ffffff', 'fill:none')
        lines[idx] = line
    with open('line_harmony.svg', 'w') as openfile:
        for line in lines:
            openfile.write('%s\n'% line )
               
    
if __name__=='__main__':
    draw_circle_harmony( )
    draw_line_harmony( )
