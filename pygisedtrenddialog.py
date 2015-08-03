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
from ui_pygisedtrend import Ui_pygisedtrend
from ui_pygisedtrend_attribute_connect import Ui_pygisedtrend_attribute_connect
from ui_pygisedtrend_text_file_analysis import Ui_pygisedtrend_text_file_analysis
from GSTA import GSTA
from qgis.gui import QgsGenericProjectionSelector, QgsMapCanvasLayer
from qgis.core import *
import math
import processing

# Minimum number of fields needed (with Z)
GSTAMINFIELDCOUNT = 6

# -------------------------------------------------------
# -------------------------------------------------------
#        CLASS FOR TEXT IMPORT DIALOG MANAGEMENT
# -------------------------------------------------------
# -------------------------------------------------------
class pygisedtrendTextFileAnalysisDialog(QtGui.QDialog, Ui_pygisedtrend_text_file_analysis):
    def __init__(self, initFileName):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        # Initialisation
        self.setWindowTitle(initFileName)
        
        # Variables
        self.fileName = initFileName
        self.currentSeparator = ' '
        self.firstLineAsHeader = False
        self.numberLineToSkip = 0
        self.lineItemsList = []
        self.commaDecimalSeparator = False
        
        # Connections definition (new style)
        self.radioSpace.toggled.connect(self.spaceToggled)
        self.radioTabulation.toggled.connect(self.tabulationToggled)
        self.radioComma.toggled.connect(self.commaToggled)
        self.radioSimilicon.toggled.connect(self.similiconToggled)
        self.radioPipe.toggled.connect(self.pipeToggled)
        self.radioOther.toggled.connect(self.otherToggled)
        self.checkBoxHeader.toggled.connect(self.headerToggled)
        self.checkBoxCommaSeparator.toggled.connect(self.commaSeparatorToggled)
        
        # old style because of two signals available (int and QString) and parameter passing
        QtCore.QObject.connect(self.spinBoxSkipLine, QtCore.SIGNAL("valueChanged(int)"),self.lineToSkip)
        QtCore.QObject.connect(self.lineEditOther, QtCore.SIGNAL("textChanged(const QString)"),self.separatorOther)
        
        self.updateTableView()
        
    #----------------------------------------------------
    # Set of functions related to widgets connection
    def spaceToggled(self, value):
        if not value:
            return
        self.currentSeparator = ' '
        self.updateTableView()
        
    def tabulationToggled(self, value):
        if not value:
            return
        self.currentSeparator = '\t'
        self.updateTableView()
    
    def commaToggled(self, value):
        if not value:
            return
        self.currentSeparator = ','
        self.updateTableView()
        
    def similiconToggled(self, value):
        if not value:
            return
        self.currentSeparator = ';'
        self.updateTableView()
        
    def pipeToggled(self, value):
        if not value:
            return
        self.currentSeparator = '|'
        self.updateTableView()
        
    def otherToggled(self, value):
        if not value:
            return
        separator = self.lineEditOther.text()
        if separator != "":
            self.currentSeparator = separator
            self.updateTableView()
        
    def headerToggled(self, value):
        self.firstLineAsHeader = value
        self.updateTableView()
    
    def lineToSkip(self, newValue):
        self.numberLineToSkip = newValue
        self.updateTableView()
        
    def linesToAnalyse(self, newValue):
        self.numberLinesToAnalyse = newValue
        self.updateTableView()
        
    def separatorOther(self, other):
        if other != "":
            self.currentSeparator = other
            self.updateTableView()

    def commaSeparatorToggled(self, value):
            self.commaDecimalSeparator = value
            self.updateTableView()
            
    #-------------------------------------------------------
    # Update the tableView widget base on the user choosen settings
    def updateTableView(self):
        try:
            # Open the text file to analyse
            textFile = open(self.fileName, "r")
        except IOError:
            QtGui.QMessageBox.information(self, u"Text file analysis", u"An error occured with file:\n%s" % self.fileName)
            return
            
        # Read the entire file
        dataFileLines = textFile.readlines()
        
        # Close the file
        textFile.close()

        # Initialisations
        self.tableAnalysisResult.clear()
        self.comboBoxX.clear()
        self.comboBoxY.clear()
        self.comboBoxZ.clear()
        self.comboBoxMean.clear()
        self.comboBoxSorting.clear()
        self.comboBoxSkewness.clear()
            # First item of comboboxes
        self.comboBoxX.addItem(u"None")
        self.comboBoxY.addItem(u"None")
        self.comboBoxZ.addItem(u"None")
        self.comboBoxMean.addItem(u"None")
        self.comboBoxSorting.addItem(u"None")
        self.comboBoxSkewness.addItem(u"None")
        self.tableAnalysisResult.setRowCount(len(dataFileLines))

        fields = []
        currentRow = 0
        currentColumn = 0
        currentFileLineNumber = 0
        
        # Header in the first line
        if self.firstLineAsHeader:
            fields = dataFileLines[currentFileLineNumber].split(self.currentSeparator)
            currentFileLineNumber += 1
            self.tableAnalysisResult.setColumnCount(len(fields))
            self.tableAnalysisResult.setHorizontalHeaderLabels(fields)
            for i in range(len(fields)):
                self.comboBoxX.addItem(fields[i])
                self.comboBoxY.addItem(fields[i])
                self.comboBoxZ.addItem(fields[i])
                self.comboBoxMean.addItem(fields[i])
                self.comboBoxSorting.addItem(fields[i])
                self.comboBoxSkewness.addItem(fields[i])
        else:
        # Read the first line and set the number of columns
            fields = dataFileLines[currentFileLineNumber].split(self.currentSeparator)
            self.tableAnalysisResult.setColumnCount(len(fields))
            currentColumn = 0
            for i in range(len(fields)):
        # Set the name of the columns    
                item = QtGui.QTableWidgetItem(u"V%s" % (i+1))
                self.tableAnalysisResult.setHorizontalHeaderItem(i,item)
        # Fill the comboBox widget with the different fields
                self.comboBoxX.addItem(u"V%s" % (i+1))
                self.comboBoxY.addItem(u"V%s" % (i+1))
                self.comboBoxZ.addItem(u"V%s" % (i+1))
                self.comboBoxMean.addItem(u"V%s" % (i+1))
                self.comboBoxSorting.addItem(u"V%s" % (i+1))
                self.comboBoxSkewness.addItem(u"V%s" % (i+1))
        
        # Number of line(s) to skip
        currentFileLineNumber += self.numberLineToSkip

        # Loop over the number of line to analyse    
        for i in range(len(dataFileLines)-currentFileLineNumber):
            fields = dataFileLines[currentFileLineNumber].split(self.currentSeparator)
            currentFileLineNumber += 1

        # Check for the number of fields, must be the same all along the file
            if len(fields) != self.tableAnalysisResult.columnCount():
                QtGui.QMessageBox.information(self, u"Text file analysis", u"Number of fields at line %d is not equal to %d" % (currentFileLineNumber, self.tableAnalysisResult.columnCount()))
                return
                
        # Fill the table view
            lineItems = []
            currentColumn = 0
            for j in range(len(fields)):
                if self.commaDecimalSeparator:
                    item = QtGui.QTableWidgetItem(fields[j].replace(",", "."))
                else:
                    item = QtGui.QTableWidgetItem(fields[j])
                lineItems.append(item)
                self.tableAnalysisResult.setItem(currentRow, currentColumn, item)
                currentColumn += 1
            currentRow += 1

    #----------------------------------------------------
    # Build the list of usefull dataset and verify that
    # the user define the usefull fields containing the needed data
    def updateLineItemsList(self):
        # empty the list
        self.lineItemsList = []
        
        # default initialisastion of a dictionary
        dictItems = { 'X':9999, 'Y':9999, 'Z':9999, 'M':9999, 'ST':9999, 'SK':9999 }
        
        # Verify that all the need fields have been defined
        if self.comboBoxX.currentText() == u"None" or \
           self.comboBoxY.currentText()  == u"None" or \
           self.comboBoxMean.currentText()  == u"None" or \
           self.comboBoxSorting.currentText()  == u"None" or \
           self.comboBoxSkewness.currentText()  == u"None":
               QtGui.QMessageBox.critical(self, u"Text file analysis", u"Define each field of the file.")
               return False
        
        # Retreive indexes of each fields in the respective comboBoxs
        dictItems['X'] = self.comboBoxX.currentIndex()-1
        dictItems['Y'] = self.comboBoxY.currentIndex()-1
        # Z is not required
        if self.comboBoxZ.currentText() != u"None":
            dictItems['Z'] = self.comboBoxZ.currentIndex()-1
        dictItems['M'] = self.comboBoxMean.currentIndex()-1
        dictItems['ST'] = self.comboBoxSorting.currentIndex()-1
        dictItems['SK'] = self.comboBoxSkewness.currentIndex()-1
        
        # verify that rows are present in the 
        if self.tableAnalysisResult.rowCount() == 0:
            return False
        
        for i in range(self.tableAnalysisResult.rowCount()):
            itemsList = []
            itemsList.append(self.tableAnalysisResult.item(i,dictItems['X']))
            itemsList.append(self.tableAnalysisResult.item(i,dictItems['Y']))
            if dictItems['Z'] != 9999:
                itemsList.append(self.tableAnalysisResult.item(i,dictItems['Z']))
            else:
                itemsList.append(QtGui.QTableWidgetItem("0.0"))
            itemsList.append(self.tableAnalysisResult.item(i,dictItems['M']))
            itemsList.append(self.tableAnalysisResult.item(i,dictItems['ST']))
            itemsList.append(self.tableAnalysisResult.item(i,dictItems['SK']))
            
            self.lineItemsList.append(itemsList)
            
        return True

    #----------------------------------------------------
    # Return the list of items on each lines       
    def getLineItemsList(self):
        if self.updateLineItemsList():
            return self.lineItemsList
        else:
            return []

    
# -------------------------------------------------------
# -------------------------------------------------------
#    CLASS FOR SHAPEFILE IMPORT DIALOG MANAGEMENT
# -------------------------------------------------------        
# -------------------------------------------------------
class pygisedtrendAttributeConnectDialog(QtGui.QDialog, Ui_pygisedtrend_attribute_connect):
    def __init__(self, shapefileName):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        
        # Variable declarations and initialisations
        self.dictLinks = {}
        self.vlayer = QgsVectorLayer(shapefileName, "vectorLayer", "ogr")
        self.field_names = [field.name() for field in self.vlayer.pendingFields() ]
        self.comboShapeAttributeList.addItems(self.field_names)
        self.lineItemsList = []
        # TODO: retreive and set the epsg of the current shapefile
        self.authID = 0
        
        # Connections definition
        QtCore.QObject.connect(self.Add, QtCore.SIGNAL("clicked()"), self.addLink)
        QtCore.QObject.connect(self.Del, QtCore.SIGNAL("clicked()"), self.delLink)
        QtCore.QObject.connect(self.pushButtonClearList, QtCore.SIGNAL("clicked()"), self.clearList)
        
    def getDictLinks(self):
        return self.dictLinks

    #----------------------------------------------------
    # Return the Id of the shapefile geodetic datum amd/or projection
    def getAuthId(self):
        return self.authID

    #---------------------------------------------------
    # Add a new link after verification that it does not exist in the dictLinks list        
    def addLink(self):
        shapeField = self.comboShapeAttributeList.currentText()  # Get shapefile field name
        gstaField = self.comboGstaAttributeList.currentText()   # Get GSTA variable name
        if QtGui.QMessageBox.information(self, u"Shapefile import", u"Add link from %s to %s" %(shapeField,gstaField),QtGui.QMessageBox.Yes|QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
            values = self.dictLinks.values()
            keys = self.dictLinks.keys()
            if not gstaField in keys and not shapeField in values:
                self.dictLinks[gstaField] = shapeField  # Add new link to dictionnary
                self.updateLinkList()
            else:
                QtGui.QMessageBox.information(self, u"Shapefile import", u"One connection per field only allowed.")
                
    #---------------------------------------------------
    # Delete a link if it does exist in the dictLinks list            
    def delLink(self):
        shapeField = self.comboShapeAttributeList.currentText()  # Get shapefile field name
        gstaField = self.comboGstaAttributeList.currentText()   # Get GSTA variable name
        if QtGui.QMessageBox.information(self, u"Shapefile import", u"Delete link from %s to %s" %(shapeField,gstaField),QtGui.QMessageBox.Yes|QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
            values = self.dictLinks.values()
            keys = self.dictLinks.keys()
            if gstaField in keys and shapeField in values:
                del self.dictLinks[gstaField]  # Delete link from dictionnary
                self.updateLinkList()
            else:
                QtGui.QMessageBox.information(self, u"Shapefile import", u"Link between %s and %s does not exist in the list" % (shapeField,gstaField))
 
    #---------------------------------------------------
    # Update the text edit field of the dialog
    def updateLinkList(self):
        self.textEditLinksList.clear()
        for gstaField, shapeField in self.dictLinks.iteritems():
            self.textEditLinksList.append(shapeField + " <--> " + gstaField)
            
    #---------------------------------------------------
    # Clear the text edit field of the dialog and
    # erase all links in the dictLinks list
    def clearList(self):
        if QtGui.QMessageBox.information(self, u"Shapefile import", u"Do you really want to clear the list ?",QtGui.QMessageBox.Yes|QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
            self.dictLinks.clear()
            self.textEditLinksList.clear()

    #----------------------------------------------------
    # Build the list of usefull dataset and verify that
    # the user define the usefull fields containing the needed data
    def updateLineItemsList(self):
        # empty the list of items list
        self.lineItemsList = []
        
        # Verify that all the need fields have been defined
        values = self.dictLinks.keys()
        if not u"Mean" in values and not u"Sorting" in values and not u"Skewness" in values:
            QtGui.QMessageBox.critical(self, u"Shapefile import", u"You have to set each GSTA value.")
            return False
        
        # To be sure that no selection is active yet
        self.vlayer.removeSelection()
        features = processing.features(self.vlayer)
        for feature in features:  # loop over all points
            itemsList = []
            itemsList.append(QtGui.QTableWidgetItem(u"%f"%feature.geometry().asPoint().x()))  # X
            itemsList.append(QtGui.QTableWidgetItem(u"%f"%feature.geometry().asPoint().y()))  # Y
            itemsList.append(QtGui.QTableWidgetItem("0.0"))                             # Z
            idx = self.vlayer.fieldNameIndex(self.dictLinks['Mean'])
            itemsList.append(QtGui.QTableWidgetItem(u"%f"%feature.attributes()[idx]))         # Mean
            idx = self.vlayer.fieldNameIndex(self.dictLinks['Sorting'])
            itemsList.append(QtGui.QTableWidgetItem(u"%f"%feature.attributes()[idx]))         # Sorting
            idx = self.vlayer.fieldNameIndex(self.dictLinks['Skewness'])
            itemsList.append(QtGui.QTableWidgetItem(u"%f"%feature.attributes()[idx]))         # Skewness
            
            self.lineItemsList.append(itemsList)
         
        return True

    #----------------------------------------------------
    # Return the list of items on each lines       
    def getLineItemsList(self):
        if self.updateLineItemsList():
            return self.lineItemsList
        else:
            return []
    
     
# -------------------------------------------------------
# -------------------------------------------------------
#           CLASS FOR MAIN DIALOG MANAGEMENT
# -------------------------------------------------------        
# -------------------------------------------------------
class pygisedtrendDialog(QtGui.QDialog, Ui_pygisedtrend):
    def __init__(self, iface):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        
        # Connections definition
        QtCore.QObject.connect(self.pushButtonShapefile, QtCore.SIGNAL("clicked()"), self.selectShapefile)
        QtCore.QObject.connect(self.pushButtonTextFile, QtCore.SIGNAL("clicked()"), self.selectTextFile)
        QtCore.QObject.connect(self.pushButtonDeteleRow, QtCore.SIGNAL("clicked()"), self.deleteDataRow)
        QtCore.QObject.connect(self.tabDlg, QtCore.SIGNAL("currentChanged(int)"), self.tabChanged)
        QtCore.QObject.connect(self.characteristicDistance, QtCore.SIGNAL("editingFinished()"), self.setCharacteristicDistance)
        QtCore.QObject.connect(self.buttonCompute, QtCore.SIGNAL("clicked()"), self.computeGSTA)
        QtCore.QObject.connect(self.checkBoxXOR, QtCore.SIGNAL("toggled(bool)"), self.computeXOR)
        QtCore.QObject.connect(self.buttonAddTrendCase, QtCore.SIGNAL("clicked()"), self.addTrendCase)
        QtCore.QObject.connect(self.buttonRemoveTrendCase, QtCore.SIGNAL("clicked()"), self.removeTrendCase)
        QtCore.QObject.connect(self.radioSmoothingNo, QtCore.SIGNAL("toggled(bool)"), self.smoothVectorFieldNo)
        QtCore.QObject.connect(self.radioSmoothingYes, QtCore.SIGNAL("toggled(bool)"), self.smoothVectorFieldYes)
        QtCore.QObject.connect(self.sliderAnisotropyDirection, QtCore.SIGNAL("valueChanged(int)"),self.setAnisotropyDirection)
        QtCore.QObject.connect(self.sliderAnisotropyTolerance, QtCore.SIGNAL("valueChanged(int)"),self.setAnisotropyTolerance)
        QtCore.QObject.connect(self.groupAnisotropy, QtCore.SIGNAL("toggled(bool)"), self.computeAnisotropy)
        QtCore.QObject.connect(self.refreshBarrierListButton, QtCore.SIGNAL("clicked()"), self.updateBarrierLayerList)
        self.barrierLayerListWidget.itemClicked.connect(self.barrierLayer)
        QtCore.QObject.connect(self.buttonExportResults, QtCore.SIGNAL("clicked()"), self.exportResults)
        
        # variables definitions
        self.iface = iface
        self.gsta = 0
        
        # Initialisations
        self.tabDlg.setTabEnabled (2,False)
        self.tabDlg.setTabEnabled (3,False)
        self.tabDlg.setTabEnabled (4,False)
        self.updateTableViewData([])
        self.buttonCompute.setEnabled(False)
        self.pushButtonDeteleRow.setEnabled(False)
        
        self.updateBarrierLayerList()
    
    # -----------------------------------------------------
    # Set XOR state
    def computeXOR(self, checked):
        if checked:
            self.gsta.SetXOR(True)
        else:
            self.gsta.SetXOR(False)
            
    # -----------------------------------------------------
    # Set smoothing state No
    def smoothVectorFieldNo(self, checked):
        if checked:
            self.gsta.SetSmoothing(False)
        else:
            self.gsta.SetSmoothing(True)
            
    # -----------------------------------------------------
    # Set smoothing state Yes
    def smoothVectorFieldYes(self, checked):
        if checked:
            self.gsta.SetSmoothing(True)
        else:
            self.gsta.SetSmoothing(False)
            
    # -----------------------------------------------------
    # Set anisotropy state
    def computeAnisotropy(self, checked):
        if checked:
            self.gsta.SetAnisotropy(True)
        else:
            self.gsta.SetAnisotropy(False)
            
    # -----------------------------------------------------
    #    
    def setAnisotropyDirection(self):
        self.gsta.SetDirection(self.sliderAnisotropyDirection.value())
    
    # -----------------------------------------------------
    #    
    def setAnisotropyTolerance(self):
        self.gsta.SetTolerance(self.sliderAnisotropyTolerance.value() / 100.0)
    
    # -----------------------------------------------------
    # Add a new trend case to the list of trend cases
    def addTrendCase(self):
        newTrendCase = ""
        newTrendCaseId = 0
        # Check for finer or coarser
        if self.radioMeanFiner.isChecked():
            newTrendCase += u"F"
            newTrendCaseId += 1
        elif self.radioMeanCoarser.isChecked():
            newTrendCase += u"C"
            newTrendCaseId += 2
        else:
            newTrendCaseId += 1000
            
        # Check for better or porer
        if self.radioSortingBetter.isChecked():
            newTrendCase += u"B"
            newTrendCaseId += 4
        elif self.radioSortingPorer.isChecked():
            newTrendCase += u"P"
            newTrendCaseId += 8
        else:
            newTrendCaseId += 2000
            
        # Check for more positive or more negative skewness
        if self.radioSkewnessPositive.isChecked():
            newTrendCase += u"+"
            newTrendCaseId += 15
        elif self.radioSkewnessNegative.isChecked():
            newTrendCase += u"-"
            newTrendCaseId += 22
        else:
            newTrendCaseId += 4000
        
        # In case of None everywhere 
        if newTrendCase == "":
            return
        
        # Check if the new case is not still present
        # and update the dicionary if new case is not present      
        if not self.gsta.GetGstaTrendCaseDict().has_key(newTrendCase):
            self.caseListEdit.append(newTrendCase)
            self.gsta.GetGstaTrendCaseDict()[newTrendCase] = newTrendCaseId

    # -----------------------------------------------------
    # Delete the selected trend case to the dict of trend cases
    def removeTrendCase(self):
        # User must select a case
        if not self.caseListEdit.textCursor().hasSelection():
             QtGui.QMessageBox.information(self, u"Trend case management", u"Select a trend case to remove")
             return
             
        # Select all the text under the current selection or cursor
        cursor = self.caseListEdit.textCursor()
        cursor.clearSelection()
        cursor.movePosition(cursor.StartOfBlock, cursor.MoveAnchor)
        cursor.movePosition(cursor.EndOfBlock, cursor.KeepAnchor)
        self.caseListEdit.setTextCursor(cursor)
        
        # check if selected text is a valid case
        case = self.caseListEdit.textCursor().selectedText()
        if not self.gsta.GetGstaTrendCaseDict().has_key(case):
            QtGui.QMessageBox.information(self, u"Trend case management", u"Your selected text is not valid")
            return
            
        del self.gsta.GetGstaTrendCaseDict()[case]
        self.caseListEdit.clear()
        for key, value in self.gsta.GetGstaTrendCaseDict().iteritems():
            self.caseListEdit.append(key)
               
    # -----------------------------------------------------
    # Select a text file name        
    def selectTextFile(self):
       textFileName = QtGui.QFileDialog.getOpenFileName(self, u"Select a text file", u"", u"Text file (*.txt *.TXT *.csv *.CSV)");
       if textFileName == "":
           return
           
       textFileAnalisys = pygisedtrendTextFileAnalysisDialog(textFileName)
       if textFileAnalisys.exec_() == QtGui.QDialog.Accepted :
           self.updateTableViewData(textFileAnalisys.getLineItemsList())
           del textFileAnalisys
       else:
           del textFileAnalisys
           return
       
       projSelector = QgsGenericProjectionSelector()
       projSelector.setMessage(u"Select projection for %s" % textFileName)
       projSelector.exec_()
       self.gsta = GSTA(projSelector.selectedAuthId())
       

    # -----------------------------------------------------
    # Return a list of the items present in the table widget
    def getItemsList(self):
        # verify that rows are present in the 
        if self.tableWidgetData.rowCount() == 0:
            return []
        
        itemsList = []
        
        for i in range(self.tableWidgetData.rowCount()):
            items = []
            items.append(self.tableWidgetData.item(i,0))
            items.append(self.tableWidgetData.item(i,1))
            items.append(self.tableWidgetData.item(i,2))
            items.append(self.tableWidgetData.item(i,3))
            items.append(self.tableWidgetData.item(i,4))
            items.append(self.tableWidgetData.item(i,5))
            
            itemsList.append(items)
            
        return itemsList
            
    # -----------------------------------------------------
    # Update the table view content
    # itemList is a list of fields list
    # the table widget will containt the used dataset
    def updateTableViewData(self, itemsList):
        if len(itemsList) == 0:
            # Disable dialog tabs/buttons
            self.tabDlg.setTabEnabled (2,False)
            self.tabDlg.setTabEnabled (3,False)
            self.tabDlg.setTabEnabled (4,False)
            self.buttonCompute.setEnabled(False)
            self.pushButtonDeteleRow.setEnabled(False)
            return
            
        # Enable dialog tabs/buttons    
        self.tabDlg.setTabEnabled (2,True)
        self.tabDlg.setTabEnabled (3,True)
        self.buttonCompute.setEnabled(True)
        self.pushButtonDeteleRow.setEnabled(True)
        # Initialisations of the table widget
        self.tableWidgetData.clear()
        self.tableWidgetData.setColumnCount(GSTAMINFIELDCOUNT)
        self.tableWidgetData.setHorizontalHeaderLabels([u"X",u"Y",u"Z",u"Mean",u"Sorting",u"Skewness"])
        self.tableWidgetData.setRowCount(len(itemsList))
        
        # Fill the table widget
        currentRow = 0
        for i in itemsList:   # over the rows
            currentColumn = 0
            for j in i:       # over the columns
                item = QtGui.QTableWidgetItem(j)
                self.tableWidgetData.setItem(currentRow, currentColumn, item)
                currentColumn += 1
            currentRow += 1

    # -----------------------------------------------------  
    # Fill the list of possible barrier layer based on the current loaded layer
    # of the current QGIS project
    def updateBarrierLayerList(self):
        self.barrierLayerListWidget.clear()
        layers = self.iface.legendInterface().layers()
        for layer in layers:
            layerType = layer.type()
            if layerType == QgsMapLayer.VectorLayer:
                layerItem = QtGui.QListWidgetItem(layer.name(), self.barrierLayerListWidget)
                layerItem.setFlags(layerItem.flags() | QtCore.Qt.ItemIsUserCheckable) # set checkable flag
                layerItem.setCheckState(QtCore.Qt.Unchecked) # and initialize check state
                self.barrierLayerListWidget.insertItem(0,layerItem)
    
    # -----------------------------------------------------  
    # Add or remove layers from barrier layer list if checked or not
    # in the layer list widget
    def barrierLayer(self, item):
        layer = QgsMapLayerRegistry.instance().mapLayersByName(item.text())[0]  # Just one layer
        if item.checkState() == QtCore.Qt.Checked:
            if not layer in self.gsta.GetBarrierLayerList():
                self.gsta.SetBarrierLayerList(layer)
        else:
            if layer in self.gsta.GetBarrierLayerList():
                del self.gsta.GetBarrierLayerList()[self.gsta.GetBarrierLayerList().index(layer)]
                
    
    # -----------------------------------------------------    
    # Get the first and last selected line number in the table widget          
    def getDataRowList(self, selectedItems):
        firstRow = self.tableWidgetData.row(selectedItems[0])
        lastRow = self.tableWidgetData.row(selectedItems[len(selectedItems)-1])
        return [firstRow, lastRow]

    # -----------------------------------------------------    
    # Delete the current line(s) selected in the table widget          
    def deleteDataRow(self):
        if QtGui.QMessageBox.critical(self, u"Data management", u"Delete line %d " % (self.tableWidgetData.currentRow()+1), QtGui.QMessageBox.Yes|QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
            selectedItems = self.getDataRowList(self.tableWidgetData.selectedItems())
            if selectedItems[0] != selectedItems[1]:
                for i in range(selectedItems[0],selectedItems[1]):
                    self.tableWidgetData.removeRow(i)
                else:
                    self.tableWidgetData.removeRow(selectedItems[1])
            else:
                self.tableWidgetData.removeRow(selectedItems[0])
                   
    # -----------------------------------------------------
    # Select a shapefile name
    def selectShapefile(self):
       shapefileName = QtGui.QFileDialog.getOpenFileName(self, u"Select a shapefile", u"", u"ESRI Shapefile (*.shp *.SHP )")
       if shapefileName != u"":
            connectionDlg = pygisedtrendAttributeConnectDialog(shapefileName)
            if connectionDlg.exec_() == QtGui.QDialog.Accepted:
                if len(connectionDlg.getDictLinks()) == 0:
                    return
                self.updateTableViewData(connectionDlg.getLineItemsList())
                self.gsta = GSTA(connectionDlg.getAuthId())
                del connectionDlg
            else:
                QtGui.QMessageBox.critical(self, u"Data management", u"No data imported.")
                del connectionDlg
                return

    # -----------------------------------------------------    
    # Fill the temporary layer dataset with the containts of the table widget
    # called each time the tab of the dialog box change (get the focus)
    def tabChanged(self, index):
        if index != 2:
            return
        errors, featuresCount = self.gsta.SetGstaLayer(self.getItemsList())
        if errors > 0:
            QtGui.QMessageBox.information(self, u"Temporary layer creation", u"%s errors occured\n%s features have been created" % (errors, featuresCount))
        else:
            QtGui.QMessageBox.information(self, u"Temporary layer creation", u"No errors occured\n%s features have been created" % featuresCount)

    # -----------------------------------------------------    
    # Called when the characteristic distance is set 
    def setCharacteristicDistance(self):
        try:
            CD = float(self.characteristicDistance.text())
        except ValueError:
            CD = 0.0
            self.characteristicDistance.setText(u"0.0")
            return
        self.gsta.SetCharacteristicDistance(CD)

    # -----------------------------------------------------    
    # Compute the vector field using user defined settings
    # ----------- CENTRAL FUNCTION OF THE MODULE ----------
    def computeGSTA(self):
        # Characteristic distance have to be set
        if self.gsta.GetCharacteristicDistance() == 0.0:
            QtGui.QMessageBox.information(self, u"Characteristic distance", u"No characteristic defined\nYou have to set this distance beforecomputing vector field")
            self.tabDlg.setTabEnabled (4,False)
            return
        # A trend case list have to be set before
        if len(self.gsta.GetGstaTrendCaseDict()) == 0:
            QtGui.QMessageBox.information(self, u"Trend case(s)", u"No trend case defined\nYou have to choose at least one trend case.")
            self.tabDlg.setTabEnabled (4,False)
            return
        
        # Select all the points of the memory layer    
        # self.gsta.GetGstaLayer().selectAll()
        
        progress = 0  # needed for progress bar
        numSelected = self.gsta.GetGstaLayer().featureCount()
        progressDiag = QtGui.QProgressDialog(u"Processing main loop...",u"Abord operation", 0, 100, self)
        progressDiag.setWindowTitle(u'PyGiSedTrend')
        progressDiag.setWindowModality(QtCore.Qt.WindowModal)
        progressDiag.setMinimumDuration(0)
        
        # ---------- Main loop ------------- #
        # loop over the selected memory layer points
        for feat in self.gsta.GetGstaLayer().getFeatures():
            neighbsList = self.gsta.GetNeighborhood(feat)
            if len(neighbsList) == 0:
                # Update the progress bar dialog
                progress += 1
                progressDiag.setValue(int(100.0 * (float(progress) / float(numSelected))))
                QtGui.qApp.processEvents()
                
                if progressDiag.wasCanceled():
                    self.tabDlg.setTabEnabled (4,False)
                    break
                continue
                
            minDist, maxDist = self.gsta.GetMinMaxDistance(feat,neighbsList)
            angleList = self.gsta.GetAngles(feat,neighbsList)
            distanceList = self.gsta.GetDistances(feat,neighbsList)
            
            E = 0.0
            N = 0.0
            computeCaseDict = {} # store real time computed values
            # loop over the trend case(s) to test
            for key, value in self.gsta.GetGstaTrendCaseDict().iteritems():
                computeCaseDict[key] = {'count':0, 'angle':0, 'module':0, 'E':0, 'N':0} # add a new key to the dict
                for i in range(len(neighbsList)):
                    if self.gsta.IsTrendCaseValid(feat, neighbsList[i], value):
                        computeCaseDict[key]['count'] += 1  # update count for current case
                        component = self.gsta.GetVectorComponent(minDist, maxDist, distanceList[i], angleList[i])
                        E += component['easting']                
                        N += component['northing']
                
                # Angle of the resultant vector in degrees
                dAlpha = math.degrees(math.atan2(N, E))
                if dAlpha < 0.0:
                    dAlpha = dAlpha + 360.0

                # Module of the resultant vector
                dModule = math.sqrt(math.pow(E,2) + math.pow(N,2))
                if((dModule > 0) and (dModule < 1)):
                    dModule = 1
                            
                # strore informations for current case
                computeCaseDict[key]['angle'] = dAlpha
                computeCaseDict[key]['module'] = dModule
                computeCaseDict[key]['E'] = E
                computeCaseDict[key]['N'] = N

            bestcase = u''
            dAlpha = 0.0
            dModule = 0.0
            E = 0.0
            N = 0.0
            if self.gsta.GetXOR():  # XOR is choosen
                # choice of the best case, based on the number of neighbors and modules
                bestKey = self.gsta.GetXORBestCase(computeCaseDict)
                if not computeCaseDict[bestKey]['count'] == 0: 
                    dAlpha = computeCaseDict[bestKey]['angle']
                    dModule = computeCaseDict[bestKey]['module']
                    bestcase = bestKey
            else:
                # Summation of the angles and modules for all cases
                for case in computeCaseDict:
                    E += computeCaseDict[case]['E']
                    N += computeCaseDict[case]['N']
                    bestcase += case + ","
                    
                # Angle of the resultant vector in degrees
                dAlpha = math.degrees(math.atan2(N, E))
                if dAlpha < 0.0:
                    dAlpha = dAlpha + 360.0

                # Module of the resultant vector
                dModule = math.sqrt(math.pow(E,2) + math.pow(N,2))
                if((dModule > 0) and (dModule < 1)):
                    dModule = 1
            
            if dAlpha == 0.0 and dModule == 0.0:
                bestcase = u'None'
                
            # Update the current feature attributes    
            # and store results in the memory layer
            self.gsta.GetGstaLayer().startEditing()
            attrs = { feat.fieldNameIndex('angle'):dAlpha, feat.fieldNameIndex('module'):dModule, feat.fieldNameIndex('bestcase'):bestcase.rstrip(',') }
            self.gsta.GetGstaLayer().dataProvider().changeAttributeValues({ feat.id() : attrs }) 
            self.gsta.GetGstaLayer().commitChanges()
                
            # Progress bar dialog update
            progress += 1
            progressDiag.setValue(int(100.0 * (float(progress) / float(numSelected))))
            QtGui.qApp.processEvents()
            
            if progressDiag.wasCanceled():
                self.tabDlg.setTabEnabled (4,False)
                break
        
        # ---------- Filtering loop -------------- #
        # Manage the filtering of the results
        if self.gsta.GetSmoothing():
            progress = 0
            progressDiag.setLabelText(u'Processing filtering...')  # Change progress dialog text

            # Unselect all points
            #self.gsta.GetGstaLayer().removeSelection()
            # Select all points of the memory layer
            #self.gsta.GetGstaLayer().selectAll()
            
            for feat in self.gsta.GetGstaLayer().getFeatures():
                neighborsList = self.gsta.GetNeighborhood(feat)
                if len(neighbsList) == 0:
                    # Update the progress bar dialog
                    progress += 1
                    progressDiag.setValue(int(100.0 * (float(progress) / float(numSelected))))
                    QtGui.qApp.processEvents()
                
                    if progressDiag.wasCanceled():
                        self.tabDlg.setTabEnabled (4,False)
                        break
                    continue
                    
                angleList = []
                moduleList = []
                angleId = self.gsta.GetGstaLayer().fieldNameIndex('angle')
                moduleId = self.gsta.GetGstaLayer().fieldNameIndex('module')
                for neighbor in neighborsList:
                    angleList.append(neighbor.attributes()[angleId])
                    moduleList.append(neighbor.attributes()[moduleId])
                 
                dAlpha = sum(angleList) / len(angleList)
                if dAlpha < 0.0:
                    dAlpha = dAlpha + 360.0
                    
                dModule = sum(moduleList) / len(moduleList)
                if((dModule > 0) and (dModule < 1)):
                    dModule = 1
                   
                # Store results in the layer feature attributs        
                self.gsta.GetGstaLayer().startEditing()
                attrs = { feat.fieldNameIndex('angle'):dAlpha, feat.fieldNameIndex('module'):dModule, feat.fieldNameIndex('bestcase'):"Filtered" }
                self.gsta.GetGstaLayer().dataProvider().changeAttributeValues({ feat.id() : attrs }) 
                self.gsta.GetGstaLayer().commitChanges()
        
                # Update the progress bar dialog
                progress += 1
                progressDiag.setValue(int(100.0 * (float(progress) / float(numSelected))))
                QtGui.qApp.processEvents()
                
                if progressDiag.wasCanceled():
                    self.tabDlg.setTabEnabled (4,False)
                    break
        
        # Unselect all points
        #self.gsta.GetGstaLayer().removeSelection() 
        # Remove the memory GSTA layer if present
        if self.gsta.GetGstaLayer() in QgsMapLayerRegistry.instance().mapLayers():
            QgsMapLayerRegistry.instance().removeMapLayer	
        # Add the memory layer to the current canvas
        QgsMapLayerRegistry.instance().addMapLayer(self.gsta.GetGstaLayer())
        # set extent to the extent of our layer
        self.iface.mapCanvas().setExtent(self.gsta.GetGstaLayer().extent())
        # set the map canvas layer
        # self.iface.mapCanvas().setLayerSet( [ QgsMapCanvasLayer(self.gsta.GetGstaLayer()) ] )
        
        # Enable the export tab
        self.tabDlg.setTabEnabled (4,True)
        
        return

    # -----------------------------------------------------    
    # Export gsta results to selected file type: shapefile or text file
    def exportResults(self):    
        if self.radioShapefile.isChecked():
            fileName = QtGui.QFileDialog.getSaveFileName(self, u"Select a shapefile name", u"", u"Shapefile (*.shp *.SHP)")
            if not fileName:
                return
            
            # define fields for feature attributes based on the choice of the user
            fields = QgsFields()
            fieldsName = []
            if self.checkAttributeMean.isChecked():
                fields.append(QgsField("mean", QtCore.QVariant.Double))
                fieldsName.append("mean")
            if self.checkAttributeSorting.isChecked():
                fields.append(QgsField("sorting", QtCore.QVariant.Double))
                fieldsName.append("sorting")
            if self.checkAttributeSkewness.isChecked():
                fields.append(QgsField("skewness", QtCore.QVariant.Double))
                fieldsName.append("skewness")
            if self.checkAttributeAngle.isChecked():
                fields.append(QgsField("angle", QtCore.QVariant.Double))
                fieldsName.append("angle")
            if self.checkAttributeModule.isChecked():
                fields.append(QgsField("module", QtCore.QVariant.Double))
                fieldsName.append("module")
            if self.checkAttributeBestcase.isChecked():
                fields.append(QgsField("bestcase", QtCore.QVariant.String))
                fieldsName.append("bestcase")
            
            writer = QgsVectorFileWriter(fileName, "utf8", fields, QGis.WKBPoint, self.gsta.getCrs(), "ESRI Shapefile")
            
            if writer.hasError() != QgsVectorFileWriter.NoError:
                QtGui.QMessageBox.error(self, u"Export dataset", u"Error when creating shapefile: %s" % writer.hasError())
                return

            for feat in self.gsta.GetGstaLayer().getFeatures():
                # Get geometry of the current feature
                geomF = feat.geometry() 
                # add the current feature
                newfeat = QgsFeature()
                newfeat.setGeometry(geomF)
                # Construct the list of values
                values = []
                if 'mean' in fieldsName:
                    idx = self.gsta.GetGstaLayer().fieldNameIndex('mean')
                    values.append(feat.attributes()[idx])
                if 'sorting' in fieldsName:
                    idx = self.gsta.GetGstaLayer().fieldNameIndex('sorting')
                    values.append(feat.attributes()[idx])
                if 'skewness' in fieldsName:
                    idx = self.gsta.GetGstaLayer().fieldNameIndex('skewness')
                    values.append(feat.attributes()[idx])
                if 'angle' in fieldsName:
                    idx = self.gsta.GetGstaLayer().fieldNameIndex('angle')
                    values.append(feat.attributes()[idx])
                if 'module' in fieldsName:
                    idx = self.gsta.GetGstaLayer().fieldNameIndex('module')
                    values.append(feat.attributes()[idx])
                if 'bestcase' in fieldsName:
                    idx = self.gsta.GetGstaLayer().fieldNameIndex('bestcase')
                    values.append(feat.attributes()[idx])
                
                # Add the attributes to the new feature 
                newfeat.setAttributes(values)
                # add the new feature to the layer
                writer.addFeature(newfeat)

            # delete the writer to flush features to disk (optional)
            del writer
        else:
            fileName = QtGui.QFileDialog.getSaveFileName(self, u"Select a shapefile name", u"", u"Text (*.txt *.TXT)")
            if not fileName:
                return
                
            if not u".txt" in fileName and not u".TXT" in fileName:
                fileName += u".txt"
            
            fieldSeparator = u" " # Space by default
            # retreive the choosen separator of the fields
            if self.radioSeparatorTab.isChecked():
                fieldSeparator = u"\t"
            elif self.radioSeparatorSemilicon.isChecked():
                fieldSeparator = u";"
            elif self.radioSeparatorComma.isChecked():
                fieldSeparator = u","
            elif self.radioSeparatorOther.isChecked():
                if self.lineSeparatorOther.text() == "":
                    fieldSeparator = u" " # Space by default
                else:
                    fieldSeparator = self.lineSeparatorOther.text()  
            
            # Open the text file and/or create/erase it    
            try:
                textfile = open(fileName, 'w')
            except IOError as e:
                QtGui.QMessageBox.error(self, u"Export dataset", u"Error when creating text file: %s" % e.strerror)
                return

            # Write the header string at the begining
            header = u"X" + fieldSeparator + u"Y"
            if self.checkAttributeMean.isChecked():
                        header += fieldSeparator + "Mean"
            if self.checkAttributeSorting.isChecked():
                        header += fieldSeparator + "Sorting"
            if self.checkAttributeSkewness.isChecked():
                        header += fieldSeparator + "Skewness"
            if self.checkAttributeAngle.isChecked():
                        header += fieldSeparator + "Angle"
            if self.checkAttributeModule.isChecked():
                        header += fieldSeparator + "Module"
            if self.checkAttributeBestcase.isChecked():
                        header += fieldSeparator + "Bestcase"
            textfile.write(header)

            for feat in self.gsta.GetGstaLayer().getFeatures():
                # Get geometry of the current feature
                geomF = feat.geometry()
                # Write the coordinates at minimum
                textfile.write("\n%6.6f%s%6.6f" % (geomF.asPoint().x(),fieldSeparator,geomF.asPoint().y()))
                if self.checkAttributeMean.isChecked():
                    idx = self.gsta.GetGstaLayer().fieldNameIndex('mean')
                    textfile.write(fieldSeparator + "%.2f" % feat.attributes()[idx])
                if self.checkAttributeSorting.isChecked():
                    idx = self.gsta.GetGstaLayer().fieldNameIndex('sorting')
                    textfile.write(fieldSeparator + "%.2f" % feat.attributes()[idx])
                if self.checkAttributeSkewness.isChecked():
                    idx = self.gsta.GetGstaLayer().fieldNameIndex('skewness')
                    textfile.write(fieldSeparator + "%.2f" % feat.attributes()[idx])
                if self.checkAttributeAngle.isChecked():
                    idx = self.gsta.GetGstaLayer().fieldNameIndex('angle')
                    textfile.write(fieldSeparator + "%.2f" % feat.attributes()[idx])
                if self.checkAttributeModule.isChecked():
                    idx = self.gsta.GetGstaLayer().fieldNameIndex('module')
                    textfile.write(fieldSeparator + "%.2f" % feat.attributes()[idx])
                if self.checkAttributeBestcase.isChecked():
                    idx = self.gsta.GetGstaLayer().fieldNameIndex('bestcase')
                    textfile.write(fieldSeparator + "%s" % feat.attributes()[idx])
            
            textfile.close()
