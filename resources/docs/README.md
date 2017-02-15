INTRODUCTION
============

Hello World! This is the official `README` of the
[cwheet](https://bitbucket.org/tanim_islam/cwheet) (pronounced
***shweet***) Color Wheel tool. Here I document all the steps necessary
to get started on using this tool. This is fairly rudimentary; I have
just started to look at various other `README.md` files on
[Bitbucket](https://bitbucket.org), so please be understanding!

The **cwheet** Color Wheel Tool is a fairly simple way to load and
create your own swatches of color for in CSS format. [The Online Color
Calculator](http://www.sessions.edu/color-calculator) most closely
matches the functionality of this tool. With this tool, one can

-   Create, load, and save color swatches.

-   Interactively modify colors in a color swatch by

    -   explicitly setting the color name and hex color definition in
        a table.

    -   dragging and clicking the selected color in an [HSV color
        wheel](https://en.wikipedia.org/wiki/HSL_and_HSV) and color bar.

    -   Transforming all the colors in the swatch by rotating through
        hue, increasing or decreasing saturation, or changing the offset
        color value.

-   Change the scale of the currently loaded, interactive HSV color
    wheel; and reset a selected color to white (`#FFFFFF`).

This document was converted from a LaTeXsource using
[`Pandoc`](http://pandoc.org/index.html), via

    pandoc -s README.tex -o README.md

INSTALLATION
============

No special installation is necessary to run this file. The requirements
for this python package are located in `requirements.txt`. To install
the requirements as an user, run the command:

    pip --user --upgrade -r requirements.txt

REQUIREMENTS
============

-   [`cssutils`](http://pythonhosted.org/cssutils/): Useful python
    utility to parse CSS files.

-   [`PyQt4`](https://www.riverbankcomputing.com/software/pyqt/intro) :
    Python bindings to the [`Qt4`](http://doc.qt.io/qt-4.8/index.html)
    cross-platform toolkit.

-   *implicitly*, the [`Qt4`](http://doc.qt.io/qt-4.8/index.html)
    cross-platform toolkit.

TODO
====

-   Fully developed documentation, including nice demonstration videos
    that demonstrate useful functionality.

-   Test cases on CSS files that others send to me.

-   The ability to have multiple color wheels within the GUI.

SUPPORT
=======

You may contact the main developer, Tanim Islam, at
[`tanim.islam@gmail.com`](mailto:tanim.islam@gmail.com). Please be
gentle; he works on this in his free time.
