# -*- coding: utf-8 -*-
"""
/***************************************************************************
 pygisedtrendDialog
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
"""
from PyQt4 import QtCore, QtGui
from qgis.core import *
import processing
import math

# Default geodetic system
WGS84 = 4326
# Set default URI for memory vector layer used for GSTA computations
URI = "Point?crs=EPSG:4326&field=Z:double&field=mean:double&field=sorting:double&field=skewness:double&field=angle:double&field=module:double&field=bestcase:string(3)&index=yes"
GSTALAYERNAME = "GSTA_temporary_layer"

class GSTA():
    
    def __init__(self, authid):
        # variable declarations
        self.crs = QgsCoordinateReferenceSystem(authid)
        uri = "Point?crs=%s&field=Z:double&field=mean:double&field=sorting:double&field=skewness:double&field=angle:double&field=module:double&field=bestcase:string(3)&index=yes" % self.crs.authid()
        self.gstaLayer = QgsVectorLayer(uri, GSTALAYERNAME, "memory")
        self.gstaTrendCaseDict = {}
        self.dictSettings = {'characteristicDistance':0.0,'XOR':False,'anisotropy':False,'direction':0.0,'tolerance':0.0, 'smoothing':False,'barrierLayer':[],'3D':False,'3DLayer':[],'3DLayerField':[],'zAtStation':False,'restrictComparison':False,'restrictMeanPourcent':0.0,'restrictSortingPercent':0.0,'restrictSkewnessPercent':0.0}

        # FOR DEBUG
        #self.testLayer = QgsVectorLayer('Polygon', 'poly' , "memory")
        #self.pr = self.testLayer.dataProvider()

    # Return crs of temporary layer
    def getCrs(self):
        return self.crs
 
    # COARSER case : TRUE if point i is coarser than point j
    def C(self, i, j):
        idx = self.gstaLayer.fieldNameIndex('mean')
        if i.attributes()[idx] > j.attributes()[idx]:
            return True
        else:
            return False
  
    # FINER case : TRUE if point i is finer than point j
    def F(self, i,j):
        idx = self.gstaLayer.fieldNameIndex('mean')
        if i.attributes()[idx] < j.attributes()[idx]:
            return True
        else:
            return False

    # BETTER case : TRUE if point i is better sorted than point j
    def B(self, i, j):
        idx = self.gstaLayer.fieldNameIndex('sorting')
        if i.attributes()[idx] > j.attributes()[idx]:
            return True
        else:
            return False

    # PORER case : TRUE if point i is porer sorted than point j
    def P(self, i, j):
        idx = self.gstaLayer.fieldNameIndex('sorting')
        if i.attributes()[idx] < j.attributes()[idx]:
            return True
        else:
            return False

    # Case + : TRUE if point i is more positively skewned regarding point j
    def MP(self, i, j):
        idx = self.gstaLayer.fieldNameIndex('skewness')
        if i.attributes()[idx] < j.attributes()[idx]:
            return True
        else:
            return False

    # Case - : TRUE if point i is more negatively skewned regarding point j
    def MN(self, i, j):
        idx = self.gstaLayer.fieldNameIndex('skewness')
        if i.attributes()[idx] > j.attributes()[idx]:
            return True
        else:
            return False

    # -----------------------------------------------------
    # Return the temporary layer
    def GetGstaLayer(self):
        return self.gstaLayer

    # -----------------------------------------------------
    # Return the trend case list
    def GetGstaTrendCaseDict(self):
        return self.gstaTrendCaseDict
        
    # -----------------------------------------------------
    # Clear the trend case list
    def ClearGstaTrendCaseDict(self):
        self.gstaTrendCaseDict.clear()

    # -----------------------------------------------------
    # Return the characteristic distance value
    def GetCharacteristicDistance(self):
        return self.dictSettings['characteristicDistance']

    # -----------------------------------------------------
    # Set the characteristic distance value
    def SetCharacteristicDistance(self, theValue):
        self.dictSettings['characteristicDistance'] = theValue
        
    # ----------------------------------------
    # 
    def GetXOR(self):
        return self.dictSettings['XOR']

    # -----------------------------------------------------
    # 
    def SetXOR(self, theValue=False):
        self.dictSettings['XOR'] = theValue
    
    # ----------------------------------------
    # 
    def GetAnisotropy(self):
        return self.dictSettings['anisotropy']

    # -----------------------------------------------------
    # 
    def SetAnisotropy(self, theValue=False):
        self.dictSettings['anisotropy'] = theValue
        
    # ----------------------------------------
    # 
    def GetDirection(self):
        return self.dictSettings['direction']

    # -----------------------------------------------------
    # 
    def SetDirection(self, theValue):
        self.dictSettings['direction'] = theValue
        
    # ----------------------------------------
    # 
    def GetTolerance(self):
        return self.dictSettings['tolerance']

    # -----------------------------------------------------
    # 
    def SetTolerance(self, theValue):
        self.dictSettings['tolerance'] = theValue
        
    # ----------------------------------------
    # 
    def GetSmoothing(self):
        return self.dictSettings['smoothing']

    # -----------------------------------------------------
    # 
    def SetSmoothing(self, theValue=False):
        self.dictSettings['smoothing'] = theValue
        
    # ----------------------------------------
    # 
    def GetBarrierLayerList(self):
        return self.dictSettings['barrierLayer']

    # -----------------------------------------------------
    # 
    def SetBarrierLayerList(self, theValue):
        self.dictSettings['barrierLayer'].append(theValue)
        
    # -----------------------------------------------------
    # 
    def ClearBarrierLayerList(self):
        self.dictSettings['barrierLayer'].clear()
        
    # ----------------------------------------
    # 
    def Get3D(self):
        return self.dictSettings['3D']

    # -----------------------------------------------------
    # 
    def Set3D(self, theValue=False):
        self.dictSettings['3D'] = theValue
        
    # ----------------------------------------
    # 
    def Get3DLayer(self):
        return self.dictSettings['3DLayer']

    # -----------------------------------------------------
    # 
    def Set3DLayer(self, theValue):
        self.dictSettings['3DLayer'].clear() # only one layer at a time for instance
        self.dictSettings['3DLayer'].append(theValue)
        
    # ----------------------------------------
    # 
    def Get3DLayerField(self):
        return self.dictSettings['3DLayerField']

    # -----------------------------------------------------
    # 
    def Set3DLayerField(self, theValue):
        self.dictSettings['3DLayerField'].clear()  # only one field at a time for instance
        self.dictSettings['3DLayerField'].append(theValue)
        
    # ----------------------------------------
    # 
    def GetZAtStation(self):
        return self.dictSettings['zAtStation']

    # -----------------------------------------------------
    # 
    def SetZAtStation(self, theValue=False):
        self.dictSettings['zAtStation'] = theValue
        
    # ----------------------------------------
    # 
    def GetRestrictComparison(self):
        return self.dictSettings['restrictComparison']

    # -----------------------------------------------------
    # 
    def SetRestrictComparison(self, theValue=False):
        self.dictSettings['restrictComparison'] = theValue
        
    # ----------------------------------------
    # 
    def GetRestrictMeanPourcent(self):
        return self.dictSettings['restrictMeanPourcent']

    # -----------------------------------------------------
    # 
    def SetRestrictMeanPourcent(self, theValue):
        self.dictSettings['restrictMeanPourcent'] = theValue
        
    # ----------------------------------------
    # 
    def GetRestrictSortingPercent(self):
        return self.dictSettings['restrictSortingPercent']

    # -----------------------------------------------------
    # 
    def SetRestrictSortingPercent(self, theValue):
        self.dictSettings['restrictSortingPercent'] = theValue
        
    # ----------------------------------------
    # 
    def GetRestrictSkewnessPercent(self):
        return self.dictSettings['restrictSkewnessPercent']

    # -----------------------------------------------------
    # 
    def SetRestrictSkewnessPercent(self, theValue):
        self.dictSettings['restrictSkewnessPercent'] = theValue

    # -----------------------------------------------------
    # Fill the temporary layer with the needed values for GSTA computation
    # itemsList is a list of items list obtained from the table widget
    def SetGstaLayer(self, itemsList):    
        if len(itemsList) == 0:
            return
        
        # Empty the temporary layer
        self.gstaLayer.startEditing()
        self.gstaLayer.selectAll()
        self.gstaLayer.deleteSelectedFeatures()
        self.gstaLayer.commitChanges()
        
        # create features to the temporary layer
        errors = 0
        for i in itemsList:
            feature = QgsFeature()
            try:
                X = float(i[0].text())
                Y = float(i[1].text())
                Z = float(i[2].text())
                M = float(i[3].text())
                ST = float(i[4].text())
                SK = float(i[5].text())
                feature.setGeometry( QgsGeometry.fromPoint(QgsPoint(X,Y)))
                values = [Z, M, ST, SK, 0.0, 0.0, u""]
            except ValueError, Argument:
                errors += 1
                continue
                
            feature.setAttributes(values)
            self.gstaLayer.startEditing()
            self.gstaLayer.addFeature(feature, True)
            self.gstaLayer.commitChanges()
            
        return errors, self.gstaLayer.featureCount()

    # -----------------------------------------------------
    # Return a list of features which are the neighboring points
    # present within the characteristic distance
    def GetNeighborhood(self, centralFeature):
        centralPnt = centralFeature.geometry().asPoint()
        
        # In a first step get the nearest points inside a rectangle
        # to limit the search loop
        halfDistance = self.GetCharacteristicDistance() / 1.4
        min_X = centralPnt.x() - halfDistance
        max_X = centralPnt.x() + halfDistance
        min_Y = centralPnt.y() - halfDistance
        max_Y = centralPnt.y() + halfDistance
        # select features inside a rectangle : to restrict the search loop
        self.gstaLayer.select(QgsRectangle(min_X, min_Y, max_X, max_Y), False)
        
        # Return an empty list if no point on the layer
        if self.gstaLayer.selectedFeatureCount() == 0:
            return []
        
        # Initialisation of the list returned
        neighborList = []
           
        # loop over the selected features to construct the neighborhood list
        for f in processing.features(self.gstaLayer):
            geomF = f.geometry()  
            if self.GetAnisotropy() == True:
                # Construction of the ellipse to take into account anisotropy
                ellipse = self.MakeEllipse(centralPnt, self.GetCharacteristicDistance(), self.GetTolerance(), self.GetDirection())
                if not ellipse:
                    return []

                if geomF.asPoint() != centralPnt and ellipse.geometry().contains(geomF):
                    if len(self.GetBarrierLayerList()) > 0:
                        line = QgsFeature()
                        line.setGeometry(QgsGeometry.fromPolyline([geomF.asPoint(),centralFeature.geometry().asPoint()])) # construct segment
                        for layer in self.GetBarrierLayerList():
                            cross = False
                            for feature in processing.features(layer):
                                if line.geometry().crosses(feature.geometry()):
                                    cross = True
                            if not cross:
                                neighborList.append(f)
                    else:
                        neighborList.append(f)
            else:  
                distance = geomF.distance(centralFeature.geometry())
                if distance <= self.GetCharacteristicDistance() and distance > 0.0:
                    if len(self.GetBarrierLayerList()) > 0:
                        line = QgsFeature()
                        line.setGeometry(QgsGeometry.fromPolyline([geomF.asPoint(),centralFeature.geometry().asPoint()])) # construct segment
                        for layer in self.GetBarrierLayerList():
                            cross = False
                            for feature in processing.features(layer):
                                if line.geometry().crosses(feature.geometry()):
                                    cross = True
                            if not cross:
                                neighborList.append(f)
                    else:
                        neighborList.append(f)
                        
        self.gstaLayer.removeSelection()            
        return neighborList
        
    # -----------------------------------------------------
    # Return the maximum and minimum distances between neighboring features 
    # in the list and the central point of interest
    def GetMinMaxDistance(self, central, neighbors):
        if len(neighbors) == 0:
            return 0.0, 0.0
        distances = []
        for i in neighbors:
            distances.append(i.geometry().distance(central.geometry()))
        return min(distances), max(distances)

    # -----------------------------------------------------
    # Return a list of angles between neighboring features 
    # in the list and the central point of interest
    def GetAngles(self, central, neighbors):
        if len(neighbors) == 0:
            return []
        angles = []
        
        ctrlGeom = central.geometry()
        ctrl = ctrlGeom.asPoint()
        
        for i in neighbors:
            nghbGeom = i.geometry()
            nghb = nghbGeom.asPoint()
            angles.append(ctrl.azimuth(nghb))
        return angles
        
    # -----------------------------------------------------
    # Return a list of distances between neighboring features 
    # in the list and the central point of interest
    def GetDistances(self, central, neighbors):
        if len(neighbors) == 0:
            return []
        
        ctrlGeom = central.geometry()
        
        distances = []
        for i in neighbors:
            distances.append(i.geometry().distance(ctrlGeom))
        return distances

    # -----------------------------------------------------
    # Return True if case (value) is valid between i and j 
    def IsTrendCaseValid(self, i, j, value):
        retValue = False
        if value == 6001:    # F
            retValue = self.F(i,j) or self.C(j,i)
        elif value == 6002:  # C
            retValue = self.C(i,j) or self.F(j,i)
        elif value == 5004:  # B
            retValue = self.B(i,j) or self.P(j,i)
        elif value == 5008:  # P
            retValue = self.P(i,j) or self.B(j,i)
        elif value == 3015:  # +
            retValue = self.MP(i,j) or self.MN(j,i)
        elif value == 3022:  # -
            retValue = self.MN(i,j) or self.MP(j,i)
        elif value == 4005:  # FB
           retValue = (self.F(i,j) and self.B(i,j)) or (self.C(j,i) and self.P(j,i))
        elif value == 4009:  # FP
            retValue = (self.F(i,j) and self.P(i,j)) or (self.C(j,i) and self.B(j,i))
        elif value == 2016:  # F+
            retValue = (self.F(i,j) and self.MP(i,j)) or (self.C(j,i) and self.MN(j,i))
        elif value == 2023:  # F-
           retValue = (self.F(i,j) and self.MN(i,j)) or (self.C(j,i) and self.MP(j,i))
        elif value == 4006:  # CB
           retValue = (self.C(i,j) and self.B(i,j)) or (self.F(j,i) and self.P(j,i))
        elif value == 4010:  # CP
            retValue = (self.C(i,j) and self.P(i,j)) or (self.F(j,i) and self.B(j,i))
        elif value == 2017:  # C+
            retValue = (self.C(i,j) and self.MP(i,j)) or (self.F(j,i) and self.MN(j,i))
        elif value == 2024:  # C-
            retValue = (self.C(i,j) and self.MN(i,j)) or (self.F(j,i) and self.MP(j,i))
        elif value == 1019:  # B+
            retValue = (self.B(i,j) and self.MP(i,j)) or (self.P(j,i) and self.MN(j,i))
        elif value == 1026:  # B-
            retValue = (self.B(i,j) and self.MN(i,j)) or (self.P(j,i) and self.MP(j,i))
        elif value == 1023:  # P+
            retValue = (self.P(i,j) and self.MP(i,j)) or (self.B(j,i) and self.MN(j,i))
        elif value == 1030:  # P-
            retValue = (self.P(i,j) and self.MN(i,j)) or (self.B(j,i) and self.MP(j,i))
        elif value == 20:  # FB+
            retValue = (self.F(i,j) and self.B(i,j) and self.MP(i,j)) or (self.C(j,i) and self.P(j,i) and self.MN(j,i))
        elif value == 27:  # FB-
          retValue = (self.F(i,j) and self.B(i,j) and self.MN(i,j)) or (self.C(j,i) and self.P(j,i) and self.MP(j,i))
        elif value == 24:  # FP+
           retValue = (self.F(i,j) and self.P(i,j) and self.MP(i,j)) or (self.C(j,i) and self.B(j,i) and self.MN(j,i))
        elif value == 31:  # FP-
          retValue = (self.F(i,j) and self.P(i,j) and self.MN(i,j)) or (self.C(j,i) and self.B(j,i) and self.MP(j,i))
        elif value == 21:  # CB+
            retValue = (self.C(i,j) and self.B(i,j) and self.MP(i,j)) or (self.F(j,i) and self.P(j,i) and self.MN(j,i))
        elif value == 28:  # CB-
           retValue = (self.C(i,j) and self.B(i,j) and self.MN(i,j)) or (self.F(j,i) and self.P(j,i) and self.MP(j,i))
        elif value == 25:  # CP+
          retValue = (self.C(i,j) and self.P(i,j) and self.MP(i,j)) or (self.F(j,i) and self.B(j,i) and self.MN(j,i))
        elif value == 32:  # CP-
           retValue = (self.C(i,j) and self.P(i,j) and self.MN(i,j)) or (self.F(j,i) and self.B(j,i) and self.MP(j,i))
        return retValue
        
    # -----------------------------------------------------
    # Return E and N component of a vector between two sample points
    # distance is use to perform normalisation of the vector
    def GetVectorComponent(self, mindist, maxdist, distance, azimuth):
        # Compute the vector components
        dNorth = math.sin(math.radians(azimuth))
        dEast = math.cos(math.radians(azimuth))
        dDistance = maxdist - mindist
        if dDistance == 0:
            N = dNorth
            E = dEast
        else:
            N = dNorth * (1.0 - (distance/dDistance))  # Ponderate by the distance
            E = dEast * (1.0 - (distance/dDistance))
        
        return {'easting':E, 'northing':N}
        
    # --------------------------------------------------------
    # Return the key of a dictionary which is the best case
    # Called for the XOR computation
    def GetXORBestCase(self, caseDict):
        # retreive keys matching max count and biggest module
        maxCountKey = max(caseDict, key=lambda k:caseDict[k]['count'])
        maxModuleKey = max(caseDict, key=lambda k:caseDict[k]['module'])
        
        # If both keys are the same, return this key
        if maxCountKey == maxModuleKey:
            return maxModuleKey
    
        # Compute probability for each key
        pKeyOne = 0.5 * ((caseDict[maxCountKey]['count']/caseDict[maxCountKey]['count'])+(caseDict[maxCountKey]['module']/caseDict[maxCountKey]['module']))
        pKeyTwo = 0.5 * ((caseDict[maxModuleKey]['count']/caseDict[maxModuleKey]['count'])+(caseDict[maxModuleKey]['module']/caseDict[maxModuleKey]['module']))
        
        # return the key of highest probability
        if pKeyOne >= pKeyTwo:
            return maxCountKey
        else:
            return maxModuleKey

    # --------------------------------------------------------
    # Return an ellipse as a GqsFeature object
    # centerPoint : point coordinates on which ellipse is centered
    # a : size the major axis of the ellipse (the characteristic distance)
    # ratio : percentage of the major axis size, allows to define the minor axis size
    # direction : orientation (North up) of the major axis of the ellipse
    # nedges : number of points which are part of the ellipse contour, default = 50
    def MakeEllipse(self, centerPoint, a, ratio, direction, nedges=50):
        newring = []

        # Variable checks
        if  (ratio <= 0 ) or (ratio > 1):
            return False

        if (direction < 0 ) or (direction > 180):
            return False

        #  Initialisation of constants
        dt = (2.0 * math.pi) / (nedges - 1.0)
        atob = 1.0 / ratio
        
        # Direction is given in degrees, so is translate in radians
        # and shift from geometric to geographic direction
        costetha = math.cos(((90.0-direction) * math.pi) / 180.0)
        sintetha = math.sin(((90.0-direction) * math.pi) / 180.0)
  
        # Initial point coordinates
        pa = QgsPoint(a, 0.0)  # x = a * cos(0) and y = b * sin(0)
  
        # Storage of initial point 
        newring.append(pa)
  
        cosdt = math.cos(dt)
        sindt = math.sin(dt)
        # Loop to get all ellipse's point
        for i in range(nedges):
            # Next point 
            nextX = (pa.x() * cosdt) - (atob * pa.y() * sindt)
            nextY = (ratio * pa.x() * sindt) + (pa.y() * cosdt)
            pb = QgsPoint(nextX, nextY)
            # Storage in ring
            newring.append(pb) 
            pa = pb
  
        # Retreive ellipse point center
        pb = centerPoint
   
        # Translation and rotation of the contour's points of the ellipse
        for i in range(len(newring)):
            pa = newring[i]  # Get the point
            nextX = (pa.x() * costetha) - (pa.y() * sintetha) + pb.x()
            nextY = (pa.x() * sintetha) + (pa.y() * costetha) + pb.y()
            pr = QgsPoint(nextX, nextY)
            newring[i] = pr  # Set the point

        ellipse = QgsFeature()
        ellipse.setGeometry(QgsGeometry.fromPolygon([newring]))
        
        # FOR DEBUG
        # self.pr.addFeatures([ellipse])

        return ellipse

