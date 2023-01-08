# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ProjectReportDockWidget
                                 A QGIS plugin
 Generate reports (CSV and HMTMIL) about project, layers, fields and layout
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2023-01-05
        git sha              : $Format:%H$
        copyright            : (C) 2023 by Patricio Soriano. SIGdeletras.com
        email                : pasoriano@gmail.com
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

import os
import shutil

from qgis.PyQt import QtGui, QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal
from qgis._core import Qgis

from qgis.core import QgsProject, QgsVectorLayer, QgsWkbTypes, QgsRasterLayer

from .QProjectReport import QProjectReport

from PyQt5.QtWidgets import QMessageBox, QLabel

from qgis.gui import (
    QgsMessageBar,
)

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'project_report_dockwidget_base.ui'))


class ProjectReportDockWidget(QtWidgets.QDockWidget, FORM_CLASS):
    closingPlugin = pyqtSignal()

    def __init__(self, iface, parent=None):
        """Constructor."""
        super(ProjectReportDockWidget, self).__init__(parent)
        self.setupUi(self)

        self.iface = iface

        self.btnCreateReport.setEnabled(False)
        self.btnCreateReport.clicked.connect(self.check_folder)
        self.directoryWidget.fileChanged.connect(self.set_folder)
        self.folder_path = ''

        self.qgs_project = QgsProject.instance()

        self.check_csv.setChecked(False)
        self.check_html.setChecked(False)

        self.check_project.setChecked(False)
        self.check_layers.setChecked(False)
        self.check_layouts.setChecked(False)
        self.check_fields.setChecked(False)

        self.check_csv.toggled.connect(self.check_options)
        self.check_html.toggled.connect(self.check_options)

        self.check_project.clicked.connect(self.check_options)
        self.check_layers.toggled.connect(self.check_options)
        self.check_layouts.toggled.connect(self.check_options)
        self.check_fields.toggled.connect(self.check_options)

        self.options_outputs = [
            self.check_csv.isChecked(),
            self.check_html.isChecked(),
        ]

        self.options_objets = [
            self.check_project.isChecked(),
            self.check_layers.isChecked(),
            self.check_layouts.isChecked(),
            self.check_fields.isChecked(),
        ]
        self.lb_info.setText('The output directory and at least one object and one type of output must be indicated')

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

    def check_folder(self):
        """Check if the report folder for the project exists, and delete it if necessary."""

        if os.path.exists(self.project.report_directory):
            reply = QMessageBox.question(self.iface.mainWindow(), 'Folder already exists',
                                         'The report folder %s already exists for this project. '
                                         'If you continue, '
                                         'all your content will be deleted and recreated. '
                                         'Do you want to continue?' % self.project.report_directory,
                                         QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                shutil.rmtree(self.project.report_directory)
                self.create_reports()
            else:
                pass
        else:
            self.create_reports()

    def create_reports(self):
        """Generate various reports for the QGIS project depending on the state of various `check_*` attributes."""

        self.project.scaffolding()

        if self.check_project.isChecked() and self.check_csv.isChecked():
            self.project.createCSVProject()

        if self.check_layers.isChecked() and self.check_csv.isChecked():
            self.project.createCSVLayers()

        if self.check_fields.isChecked() and self.check_csv.isChecked():
            self.project.createCSVLayerFields()

        if self.check_layouts.isChecked() and self.check_csv.isChecked():
            self.project.createCSVLayouts()

        if self.check_html.isChecked():
            self.project.create_html(self.options_objets)

        success_message = '😎 Project reports have been created in <b>%s</b>' % (
            self.project.report_directory)

        self.iface.messageBar().pushMessage("Success", success_message, level=Qgis.Success, duration=10)

    def set_folder(self):
        """Set the output folder for the reports"""
        self.folder_path = self.directoryWidget.filePath()
        self.project = QProjectReport(self.qgs_project, self.folder_path)
        self.check_options()

    def check_options(self):
        """Check the options selected in the GUI and update the state of the "Create Report"
        button and a message label accordingly"""

        self.options_outputs = [
            self.check_csv.isChecked(),
            self.check_html.isChecked(),
        ]

        self.options_objets = [
            self.check_project.isChecked(),
            self.check_layers.isChecked(),
            self.check_fields.isChecked(),
            self.check_layouts.isChecked(),
        ]

        any_check_objets = [False, False, False, False]
        any_check_outputs = [False, False]

        if self.options_objets == any_check_objets or self.options_outputs == any_check_outputs \
                or self.folder_path == '':
            self.btnCreateReport.setEnabled(False)
            self.lb_info.setText('The output directory and at least one object and one type of output must be indicated')
        else:
            self.lb_info.setText('')
            self.btnCreateReport.setEnabled(True)


