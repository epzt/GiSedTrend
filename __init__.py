# -*- coding: utf-8 -*-
"""
/***************************************************************************
 pygisedtrend
                                 A QGIS plugin
 This plugin allows to perform a Grain Size Trend Analysis
                             -------------------
        begin                : 2014-05-07
        copyright            : (C) 2014 by Emmanuel Poizot/Cnam-Intechmer
        email                : emmanuel.poizot@cnam.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""

def classFactory(iface):
    # load pygisedtrend class from file pygisedtrend
    from pygisedtrend import pygisedtrend
    return pygisedtrend(iface)
