from os import remove
from typing import Union

import numpy as np
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtWidgets import (QLabel, QLineEdit, QComboBox, QPushButton, QGridLayout,QWidget, QDial,
                             QFrame, QMessageBox, QVBoxLayout, QTableView, QDialog, QCheckBox, QSlider)
from pandas import DataFrame

from resources.modules.data import Data
from resources.modules.formating import Formater
from resources.modules.plotting import PLOT_TYPES
from resources.modules.stylesheets import button, combobox
from resources.modules.table import TableModel


class Settings(QWidget):
    def __init__(self, plot_map_obj):
        """
        Window with functionality to adjust plot map parameters,
         applied to the PlotMap table and rendered plot.
        :param plot_map_obj: Connected instance of a PlotMap
        """
        super().__init__()
        from resources.modules.utility import resource_path, COLORS
        # VARS
        self.combo_boxes_updated = False
        self.plot_map_obj = plot_map_obj
        self.plot_map_obj.run_plot_button.setText("LOADING>>>")
        self.plot_map_obj.main_win.setDisabled(True)
        self.plot_map = self.plot_map_obj.plot_map
        self.data = Data(self.plot_map['data'])
        self.avail_data = []

        # WIDOW DETAILS
        self.setWindowTitle('%s SETTINGS | ID: %s' % (self.plot_map['title'], self.plot_map['id']))
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.setWindowIcon(QIcon(resource_path('resources/images/gear.ico')))
        self.resize(200, 200)

        # UPPER LEFT QUAD
        # SAVE AND RUN PLOT
        save_run_button = QPushButton('Save and Run Plot')
        save_run_button.setStyleSheet(button)
        save_run_button.clicked.connect(lambda checked: self.save_plot_map(True))
        # CHANGE TITLE
        plot_map_title_label = QLabel('Plot Title:')
        self.plot_map_title = QLineEdit()
        self.plot_map_title.textChanged.connect(self.set_title)
        # CHANGE COLOR
        self.colors = COLORS
        color_selector_label = QLabel('Background Color:')
        self.color_selector = QComboBox()
        self.color_selector.setStyleSheet("QComboBox::editable {background-color: %s;}" % self.plot_map['color'])
        for c in self.colors:
            self.color_selector.addItem(c)
            self.color_selector.setItemData(self.colors.index(c), QColor(c), Qt.ItemDataRole.DecorationRole)
        self.color_selector.currentIndexChanged.connect(self.set_color)
        # CHANGE DATAFRAME
        data_selector_label = QLabel('Select Data:')
        self.data_selector = QComboBox()
        self.data_selector.setStyleSheet(combobox)
        self.data_selector.currentIndexChanged.connect(self.set_data)
        # DELETE DATA BUTTON
        self.data_delete_button = QPushButton('Delete Data: (none)')
        self.data_delete_button.setStyleSheet(button)
        self.data_delete_button.clicked.connect(lambda checked: self.delete_data())
        # DELETE DATA SELECTOR
        self.data_delete_selector = QComboBox()
        self.data_delete_selector.setStyleSheet(combobox)
        self.data_delete_selector.currentIndexChanged.connect(self.update_delete_selector_button)

        # LOWER LEFT QUAD
        # SAVE PLOT
        pm_save_button = QPushButton('Save Structure')
        pm_save_button.setStyleSheet(button)
        pm_save_button.clicked.connect(lambda checked: self.save_plot_map(False))
        # X DATA
        self.x_coord_selector_label = QLabel('X Coordinate:')
        self.x_coord_selector = QComboBox()
        self.x_coord_selector.setStyleSheet(combobox)
        self.x_coord_selector.currentIndexChanged.connect(self.set_x)
        # Y DATA
        self.y_coord_selector_label = QLabel('Y Coordinate:')
        self.y_coord_selector = QComboBox()
        self.y_coord_selector.setStyleSheet(combobox)
        self.y_coord_selector.currentIndexChanged.connect(self.set_y)
        # Z DATA
        self.z_coord_selector_label = QLabel('Z Coordinate:')
        self.z_coord_selector = QComboBox()
        self.z_coord_selector.setStyleSheet(combobox)
        self.z_coord_selector.currentIndexChanged.connect(self.set_z)
        # CHANGE GRAPH
        plot_name_selector_label = QLabel('Select Plot:')
        self.plot_name_selector = QComboBox()
        self.plot_name_selector.setStyleSheet(combobox)
        self.plot_name_selector.currentTextChanged.connect(self.set_graph_name)
        # X GRID
        self.x_grid = QCheckBox('X-Grid Visible' if self.plot_map['x_grid'] else 'X-Grid Hidden')
        self.x_grid.stateChanged.connect(self.swap_x_grid)
        # Y GRID
        self.y_grid = QCheckBox('Y-Grid Visible' if self.plot_map['y_grid'] else 'Y-Grid Hidden')
        self.y_grid.stateChanged.connect(self.swap_y_grid)
        # PLOT RESOLUTION
        self.dpi_label = QLabel('Set Plot DPI: %s' % self.plot_map['dpi'])
        self.dpi = QDial()
        self.dpi.setRange(10, 500)
        self.dpi.setValue(int(self.plot_map['dpi']))
        self.dpi.valueChanged.connect(self.set_dpi)
        self.dpi.mouseReleaseEvent = self.mouseReleaseEvent
        # FIT TO DISPLAY
        self.fit_display = QCheckBox('Plot Fits To Display' if self.plot_map['fit'] else 'Plot Expandable')
        self.fit_display.stateChanged.connect(self.swap_fit)
        # LABEL EVERY PLOT POINT
        self.label_all = QCheckBox('All Point Labels' if self.plot_map['label_all'] else 'Minimal Point Labels')
        self.label_all.stateChanged.connect(self.swap_label_all)
        # STRETCH HORIZONTAL
        h_value = self.plot_map['horz_stretch']
        self.horz_stretch_label = QLabel('Horz Stretch: %s' % (h_value / 10) if h_value > 0 else 'Auto-Scaling')
        self.horz_stretch = QSlider(Qt.Orientation.Horizontal)
        self.horz_stretch.setRange(0, 100)
        self.horz_stretch.setTickInterval(1)
        # self.horz_stretch.setValue(-1)
        self.horz_stretch.valueChanged.connect(self.set_horz_stretch)
        self.horz_stretch.mouseReleaseEvent = self.mouseReleaseEvent
        # STRETCH VERTICAL
        v_value = self.plot_map['vert_stretch']
        self.vert_stretch_label = QLabel('Vert Stretch:   %s' % (v_value / 10) if v_value > 0 else 'Auto-Scaling')
        self.vert_stretch = QSlider(Qt.Orientation.Horizontal)
        self.vert_stretch.setRange(0, 100)
        self.vert_stretch.setTickInterval(1)
        # self.vert_stretch.setValue(-1)
        self.vert_stretch.valueChanged.connect(self.set_vert_stretch)
        self.vert_stretch.mouseReleaseEvent = self.mouseReleaseEvent

        # RIGHT QUAD
        # FORMATER
        self.formater = Formater(self)
        # PREVIEW TABLE
        self.preview = QDialog(self)
        self.preview_table = QTableView()
        self.preview_table.verticalHeader().setVisible(False)
        self.preview_table_model = TableModel
        preview_layout = QVBoxLayout()
        preview_layout.addWidget(self.preview_table)
        self.preview.setLayout(preview_layout)
        # PREVIEW TABLE BUTTON
        preview_table_button = QPushButton('Preview Formated Table')
        preview_table_button.setStyleSheet(button)
        preview_table_button.clicked.connect(lambda click: self.open_preview_table())
        # SAVE FORMATED DATA SOURCE
        self.save_new_format_button = QPushButton('Save Formated Data')
        self.save_new_format_button.setStyleSheet(button)
        self.save_new_format_button.clicked.connect(lambda checked: self.save_formated())

        # INITIALIZE CONFIG AFTER MAIN WINDOW IS LOADED
        QTimer.singleShot(500, self.set_config)

        # UPPER LEFT FRAME
        upper_left_frame = QFrame()
        upper_left_frame.setFrameShape(QFrame.Shape.WinPanel)
        upper_left_frame.setFrameShadow(QFrame.Shadow.Raised)
        # UPPER LEFT LAYOUT
        upper_left_layout = QGridLayout()
        upper_left_layout.addWidget(plot_map_title_label, 0, 0)
        upper_left_layout.addWidget(self.plot_map_title, 0, 1)
        upper_left_layout.addWidget(color_selector_label, 1, 0)
        upper_left_layout.addWidget(self.color_selector, 1, 1)
        upper_left_layout.addWidget(data_selector_label, 2, 0)
        upper_left_layout.addWidget(self.data_selector, 2, 1)
        upper_left_layout.addWidget(self.data_delete_button, 4, 0)
        upper_left_layout.addWidget(self.data_delete_selector, 4, 1)
        upper_left_frame.setLayout(upper_left_layout)

        # LOWER LEFT FRAME
        lower_left_frame = QFrame()
        lower_left_frame.setFrameShape(QFrame.Shape.WinPanel)
        lower_left_frame.setFrameShadow(QFrame.Shadow.Raised)
        # LOWER LEFT LAYOUT
        lower_left_layout = QGridLayout()
        lower_left_layout.addWidget(plot_name_selector_label, 0, 0)
        lower_left_layout.addWidget(self.plot_name_selector, 0, 1)
        lower_left_layout.addWidget(self.x_coord_selector_label, 1, 0)
        lower_left_layout.addWidget(self.x_coord_selector, 1, 1)
        lower_left_layout.addWidget(self.y_coord_selector_label, 2, 0)
        lower_left_layout.addWidget(self.y_coord_selector, 2, 1)
        lower_left_layout.addWidget(self.z_coord_selector_label, 3, 0)
        lower_left_layout.addWidget(self.z_coord_selector, 3, 1)
        lower_left_layout.addWidget(self.x_grid, 4, 0)
        lower_left_layout.addWidget(self.y_grid, 4, 1)
        lower_left_layout.addWidget(self.dpi_label, 5, 0)
        lower_left_layout.addWidget(self.fit_display, 6, 0)
        lower_left_layout.addWidget(self.label_all, 7, 0)
        lower_left_layout.addWidget(self.dpi, 5, 1, 3, 1)
        lower_left_layout.addWidget(self.horz_stretch_label, 8, 0)
        lower_left_layout.addWidget(self.horz_stretch, 8, 1)
        lower_left_layout.addWidget(self.vert_stretch_label, 9, 0)
        lower_left_layout.addWidget(self.vert_stretch, 9, 1)
        lower_left_frame.setLayout(lower_left_layout)

        # RIGHT FRAME
        right_frame = QFrame()
        right_frame.setFrameShape(QFrame.Shape.WinPanel)
        right_frame.setFrameShadow(QFrame.Shadow.Raised)
        # RIGHT LAYOUT
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.formater)
        right_frame.setLayout(right_layout)

        # MAIN LAYOUT
        self.body = QGridLayout()
        layout_frame = QFrame()
        layout_frame.setFrameShape(QFrame.Shape.StyledPanel)
        layout_frame.setFrameShadow(QFrame.Shadow.Sunken)
        layout = QGridLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setHorizontalSpacing(20)
        layout.addWidget(QLabel('Select Data:'), 0, 0)
        layout.addWidget(save_run_button, 0, 1)
        layout.addWidget(upper_left_frame, 1, 0, 1, 2)
        layout.addWidget(QLabel('Structure Plot:'), 2, 0)
        layout.addWidget(pm_save_button, 2, 1)
        layout.addWidget(lower_left_frame, 3, 0, 1, 2)
        layout.addWidget(preview_table_button, 0, 2)
        layout.addWidget(self.save_new_format_button, 0, 3)
        layout.addWidget(right_frame, 1, 2, 3, 2)
        layout_frame.setLayout(layout)
        self.body.addWidget(layout_frame)
        self.setLayout(self.body)

    def closeEvent(self, event):
        """
        Catches when the settings window is closed,
         and saves the current plot map.
        Closes the preview window manually if it is open.
        :param event: PyQt close event.
        """
        self.setWindowTitle(' < < < [ SAVING: %s ] > > > ' % self.plot_map['data_name'])
        if self.preview.isVisible():
            self.preview.hide()
        self.save_plot_map(False)

    def showEvent(self, event):
        """
        Catches when the settings window is opened,
         and resets the title bar to its default values.
        :param event: PyQt show event.
        """
        self.setWindowTitle('%s SETTINGS | ID: %s' % (self.plot_map['title'], self.plot_map['id']))

    def mouseReleaseEvent(self, event):
        """
        Catches a mouse release event,
         when changing the dpi or stretch values.
        If value has been changed, re-renders the plot.
        :param event: PyQt mouse release event.
        """
        if self.dpi.value() != self.plot_map['dpi']:
            self.plot_map['dpi'] = self.dpi.value()
            self.plot_map_obj.plot_canvas.run()
        if self.horz_stretch.value() != self.plot_map['horz_stretch']:
            self.plot_map['horz_stretch'] = self.horz_stretch.value()
            self.plot_map_obj.plot_canvas.run()
        if self.vert_stretch.value() != self.plot_map['vert_stretch']:
            self.plot_map['vert_stretch'] = self.vert_stretch.value()
            self.plot_map_obj.plot_canvas.run()

    def set_config(self):
        """
        Initializes parameters in the settings window.
        Re-enables the main window after initialized,
         to avoid crashes from overloading.
        Renders a plot if all necessary parameters are set.
        """
        self.update_combo_boxes()
        self.update_fit()
        self.plot_map_obj.main_win.setDisabled(False)
        if self.plot_map_obj.validate_data():
            self.plot_map_obj.run_plot()
        else:
            self.plot_map_obj.reset_run_plot_button_title()

    def update_table(self):
        """
        Resets PlotMap table with current plot map data.
        Resets Formater data with current plot map data.
        """
        self.plot_map_obj.table_model = TableModel(self.plot_map['data'])
        self.plot_map_obj.table_data.setModel(self.plot_map_obj.table_model)
        self.plot_map_obj.table_data.resizeColumnsToContents()
        self.formater.set_formated_data()

    def update_combo_boxes(self):
        """
        Calls: When updating parquet data sources.
               When initializing module.
               When applying new data to the plot map.
               When applying formated data to the plot map.
               When removing parquet data sources.
        Blocked: Changes to data selector.
                 Changes to plot name selector.
                 Changes to coord selectors; x, y, z.
        Blocks plot map changes from combo boxes,
         with establishing they are currently being updated.
        Gets the current list of available Data parquet data sources,
         by calling for an update to the Data pqt_sources
         and updates the methods avail data list.
        Updates each of the selectors that carry the data source options.
        Updates plot name selector, applying plot map coords as appropriate.
        Updates coord selectors.
        Set the current plot map parameters to the PlotMap settings window.
        """
        self.combo_boxes_updated = False
        avail_data = self.data.update_dict()
        if avail_data != self.avail_data:
            self.avail_data = avail_data
        self.update_data_selector()
        self.update_delete_selector()
        self.update_formater_merge_selector()
        self.update_plot_name_selector()
        self.update_coord_selectors()
        self.set_plot_map()
        self.combo_boxes_updated = True

    def update_data_selector(self):
        """
        Clears data selector.
        Reloads data selector with current avail data
        """
        self.data_selector.clear()
        self.avail_data[0] = 'SELECT DATA SOURCE'
        self.data_selector.addItems(self.avail_data)

    def update_delete_selector(self):
        """
        Clears delete selector.
        Reloads delete selector with current avail data
        """
        self.data_delete_selector.clear()
        self.avail_data[0] = 'Select Data'
        self.data_delete_selector.addItems(self.avail_data)

    def update_formater_merge_selector(self):
        """
        Clears Formater merge selector.
        Reloads Formater merge selector with current avail data
        """
        self.formater.df_merge_selector.clear()
        self.avail_data[0] = 'Add Data'
        self.formater.df_merge_selector.addItems(self.avail_data)

    def update_plot_name_selector(self):
        """
        Clear the plot name selector of previous graph names.
        Determines they type of plot that can be rendered,
         using the data name saved in the plot map.
        Reloads the plot name selector with the appropriate,
         graph names that the plot map data can be applied to.
        """
        self.plot_name_selector.clear()
        plot_names = []
        if self.plot_map['data_name']:
            if self.plot_map['data_name'][:3] == 'iso':
                if self.plot_map['data_name'][4:7] == 'tri':
                    plot_names = [plot for plot in PLOT_TYPES.keys() if plot[:3] == 'Tri']
                else:
                    plot_names = [plot for plot in PLOT_TYPES.keys() if plot[:3] == 'Iso']
            else:
                plot_names = [plot for plot in PLOT_TYPES.keys() if plot[:3] not in ['Tri', 'Iso']]
            plot_names.insert(0, 'SELECT PLOT')
        self.plot_name_selector.addItems(plot_names)

    def update_coord_selectors(self):
        """
        Clear all coordinate related selectors to not build up references.
        Obtains all column names from the current data saved in the plot map.
        Reloads all settings window coordinate selectors,
         with the current applicable column names.
        """
        self.x_coord_selector.clear()
        self.y_coord_selector.clear()
        self.z_coord_selector.clear()
        self.formater.format_coord_selector.clear()
        coords = []
        if self.plot_map['data'] is not None:
            coords = [coord for coord in self.plot_map['data']]
            coords.insert(0, '')
        self.x_coord_selector.addItems(coords)
        self.y_coord_selector.addItems(coords)
        self.z_coord_selector.addItems(coords)
        self.formater.format_coord_selector.addItems(coords)
        self.show_coord_selectors()

    def show_coord_selectors(self):
        """
        Gets the necessary coordinates to show in the settings window,
         from the PLOT_TYPES dict specification
         of the save graph name in the plot map.
        Makes calls to show_x, show_y, show_z as required.
        """
        defined = {'x': self.show_x, 'y': self.show_y, 'z': self.show_z}
        required_vars = ()
        if self.plot_map['graph_name']:
            required_vars = PLOT_TYPES[self.plot_map['graph_name']][1]
        [defined[var](True) if var in required_vars else defined[var](False) for var in defined]

    def show_x(self, show:bool):
        """
        Show or Hide x-coord selector,
         based on plot requirements of the graph name.
        :param show: True if required for given plot.
        """
        if show:
            self.x_coord_selector_label.setText('X Coordinate:')
            self.x_coord_selector.show()
        else:
            self.x_coord_selector_label.setText('')
            self.x_coord_selector.hide()

    def show_y(self, show:bool):
        """
        Show or Hide y-coord selector,
         based on plot requirements of the graph name.
        :param show: True if required for given plot.
        """
        if show:
            self.y_coord_selector_label.setText('Y Coordinate:')
            self.y_coord_selector.show()
        else:
            self.y_coord_selector_label.setText('')
            self.y_coord_selector.hide()

    def show_z(self, show: bool):
        """
        Show or Hide z-coord selector,
         based on plot requirements of the graph name.
        :param show: True if required for given plot.
        """
        if show:
            self.z_coord_selector_label.setText('Z Coordinate:')
            self.z_coord_selector.show()
        else:
            self.z_coord_selector_label.setText('')
            self.z_coord_selector.hide()

    def set_plot_map(self):
        """
        Apply plot map values to settings menu options.
        """
        self.plot_map_title.setText(self.plot_map['title'])
        self.color_selector.setCurrentIndex(self.color_selector.findText(self.plot_map['color']))
        if self.plot_map['data_name']:
            self.data_selector.setCurrentIndex(self.data_selector.findText(self.plot_map['data_name']))
        self.plot_name_selector.setCurrentText(self.plot_map['graph_name'])
        self.x_grid.setCheckState(Qt.CheckState.Checked if self.plot_map['x_grid'] else Qt.CheckState.Unchecked)
        self.y_grid.setCheckState(Qt.CheckState.Checked if self.plot_map['y_grid'] else Qt.CheckState.Unchecked)
        self.dpi.setValue(self.plot_map['dpi'])
        self.fit_display.setCheckState(Qt.CheckState.Unchecked if self.plot_map['fit'] else Qt.CheckState.Checked)
        self.label_all.setCheckState(Qt.CheckState.Checked if self.plot_map['label_all'] else Qt.CheckState.Unchecked)
        self.horz_stretch.setValue(self.plot_map['horz_stretch'])
        self.vert_stretch.setValue(self.plot_map['vert_stretch'])


    def set_title(self, title: str):
        """
        Applies a title to this instance of a plot map.
        :param title: User input value.
        """
        self.plot_map['title'] = title
        self.setWindowTitle('%s SETTINGS | ID: %s' % (self.plot_map['title'], self.plot_map['id']))

    def set_color(self, index: int):
        """
        Applies new background color to plot map.
        Sets background color for PlotMap.
        :param index: index of name of color in color selector.
        """
        self.plot_map['color'] = self.colors[index]
        self.color_selector.setStyleSheet("QComboBox::editable"
                                          "{background-color: %s;}" % self.plot_map['color'])
        self.plot_map_obj.set_bg_color()

    def set_data(self, index: int):
        """
        Calls: When selecting a new data source in settings window.
               When updating data source from formated data being saved.
               When primary data source is updated and has changed.
               When setting plot map from updating combo boxes.
        Applies data selector name at index to set a new Pandas Dataframe or dictionary of Numpy arrays,
         if selected data is not identical to existing and combo boxes are not being updated.
        Resets data to None if none are selected in data selector.
        :param index: data selector option index value derived from Data pqt_sources.
        """
        if index > 0:
            if self.combo_boxes_updated:
                data, name = self.data.get_df(index)
                if self.verify_data_change(data):
                    self.reset_plot_map(data, name)
                    self.update_table()
                    self.update_combo_boxes()
        elif self.combo_boxes_updated:
            self.reset_plot_map(None, '')
            self.update_combo_boxes()

    def verify_data_change(self, data: Union[DataFrame, dict, None]) -> bool:
        """
        Compares data structures between plot map data and new data being set.
        Compares data if types are the same.
        :param data: New data, either Pandas Dataframe or dictionary of Numpy Arrays.
        :return: True, if there is a difference between data objects.
        """
        if self.plot_map_obj.main_win.sources_updating:
            self.plot_map['data'] = data
            return False
        elif isinstance(data, DataFrame) and isinstance(self.plot_map['data'], DataFrame):
            if data.equals(self.plot_map['data']):
                return False
        elif isinstance(self.plot_map['data'], np.ndarray):
            if data == self.plot_map['data']:
                return False
        return True

    def reset_plot_map(self, data: Union[DataFrame, dict, None], name:str):
        """
        Clears plot map and sets new data or None from df selector.
        :param data: Pandas Dataframe or dictionary of Numpy arrays.
        :param name: Name of new data
        """
        self.plot_map['data'] = data
        self.plot_map['data_name'] = name
        self.plot_map['graph_name'] = ''
        self.plot_map['x_coord'] = ''
        self.plot_map['y_coord'] = ''
        self.plot_map['z_coord'] = ''

    def set_x(self, index:int):
        """
        Sets X coordinate from x-coord selector.
        Updates x-coord selector label with the size of the plot map column.
        :param index: index of x-coord selector
        """
        if self.combo_boxes_updated:
            self.plot_map['x_coord'] = self.x_coord_selector.currentText() if index > 0 else ''
            info = len(self.plot_map['data'][self.plot_map['x_coord']]) if self.plot_map['x_coord'] else ''
            if info:
                self.x_coord_selector_label.setText('X Coordinate: %s' % info)

    def set_y(self, index:int):
        """
        Sets Y coordinate from y-coord selector.
        Updates y-coord selector label with the size of the plot map column.
        :param index: index of y-coord selector
        """
        if self.combo_boxes_updated:
            self.plot_map['y_coord'] = self.y_coord_selector.currentText() if index > 0 else ''
            info = len(self.plot_map['data'][self.plot_map['y_coord']]) if self.plot_map['y_coord'] else ''
            if info:
                self.y_coord_selector_label.setText('Y Coordinate: %s' % info)

    def set_z(self, index:int):
        """
        Sets Z coordinate from z-coord selector.
        Updates z-coord selector label with the size of the plot map column.
        :param index: index of z-coord selector
        """
        if self.combo_boxes_updated:
            self.plot_map['z_coord'] = self.z_coord_selector.currentText() if index > 0 else ''
            info = len(self.plot_map['data'][self.plot_map['z_coord']]) if self.plot_map['z_coord'] else ''
            if info:
                self.z_coord_selector_label.setText('Z Coordinate: %s' % info)

    def set_graph_name(self, text:str):
        """
        Applies graph name to the plot map.
        Sets coordinate selectors.
        :param text: Graph name from plot name selector.
        """
        if text:
            if self.combo_boxes_updated and text != 'SELECT PLOT':
                self.plot_map['graph_name'] = text
                self.show_coord_selectors()
            self.apply_coords()
        else:
            self.plot_name_selector.setCurrentIndex(0)

    def apply_coords(self):
        """
        Sets coordinate values from plot map coords,
         based on the graph name prefix.
        If isometric, set the values specifically.
        """
        if self.plot_map['graph_name'][:3] in ['Iso', 'Tri']:
            self.x_coord_selector.setCurrentIndex(1)
            self.y_coord_selector.setCurrentIndex(2)
            self.z_coord_selector.setCurrentIndex(3)
        else:
            self.x_coord_selector.setCurrentText(self.plot_map['x_coord'])
            self.y_coord_selector.setCurrentText(self.plot_map['y_coord'])
            self.z_coord_selector.setCurrentText(self.plot_map['z_coord'])

    def swap_x_grid(self):
        """
        Turn on and off horizontal grid bars.
        """
        if self.combo_boxes_updated:
            self.plot_map['x_grid'] = not self.plot_map['x_grid']
            self.plot_map_obj.plot_canvas.run()
        self.x_grid.setText('X-Grid Visible' if self.plot_map['x_grid'] else 'X-Grid Hidden')

    def swap_y_grid(self):
        """
        Turn on and off vertical grid bars
        """
        if self.combo_boxes_updated:
            self.plot_map['y_grid'] = not self.plot_map['y_grid']
            self.plot_map_obj.plot_canvas.run()
        self.y_grid.setText('Y-Grid Visible' if self.plot_map['y_grid'] else 'Y-Grid Hidden')

    def set_dpi(self, dpi:int):
        """
        Defines plot DPI, self adjusts to nearest ten value.
        Uses call to mouseReleaseEvent to update RenderPlot and set value to plot map.
        :param dpi: DPI value to apply to rendered plot.
        """
        dpi = int(dpi - (dpi % 10))
        self.dpi_label.setText('Set Plot DPI: %s' % dpi)
        self.dpi.setValue(dpi)
        self.plot_map_obj.run_plot_button.setText(' < < < RENDERING PLOT > > > ')

    def swap_fit(self):
        """
        Defines how the graph is to be drawn,
         within the confines of the display,
         or expanded to full size with scrolling.
        """
        if self.combo_boxes_updated:
            self.plot_map['fit'] = not self.plot_map['fit']
            self.plot_map_obj.plot_canvas.run()
        self.update_fit()

    def update_fit(self):
        """
        Displays or hides the plot size modifier selectors,
         shown if it is not fit to plot display.
        """
        if self.plot_map['fit']:
            self.fit_display.setText('Plot Fits To Display')
            self.label_all.hide()
            self.horz_stretch_label.hide()
            self.horz_stretch.hide()
            self.vert_stretch_label.hide()
            self.vert_stretch.hide()
        else:
            self.fit_display.setText('Plot Expandable')
            self.label_all.show()
            self.horz_stretch_label.show()
            self.horz_stretch.show()
            self.vert_stretch_label.show()
            self.vert_stretch.show()

    def swap_label_all(self):
        """
        Sets if to label all data points on plot,
         or to only label the minimum necessary.
        """
        if self.combo_boxes_updated:
            self.plot_map['label_all'] = not self.plot_map['label_all']
            self.plot_map_obj.plot_canvas.run()
        self.label_all.setText('All Point Labels' if self.plot_map['label_all'] else 'Minimal Point Labels')

    def set_horz_stretch(self, value):
        """
        Defines plot width when it is not fit to plot display.
        Uses call to mouseReleaseEvent to update RenderPlot and set value to plot map.
        :param value: Multiplier applied to current plot display width.
        """
        self.horz_stretch_label.setText('Horz Stretch: %s' % (value / 10) if value > 0 else 'Auto-Scaling')
        self.plot_map_obj.run_plot_button.setText(' < < < RENDERING PLOT > > > ')

    def set_vert_stretch(self, value):
        """
        Defines plot height when it is not fit to plot display.
        Uses call to mouseReleaseEvent to update RenderPlot and set value to plot map.
        :param value: Multiplier applied to current plot display height.
        """
        self.vert_stretch_label.setText('Vert Stretch:   %s' % (value / 10) if value > 0 else 'Auto-Scaling')
        self.plot_map_obj.run_plot_button.setText(' < < < RENDERING PLOT > > > ')

    def open_preview_table(self):
        """
        Creates and opens a window to preview changes made to formated data,
         if formated data exists.
        """
        if self.data.formated_data is not None:
            self.preview.setWindowTitle('Preview for Formated %s' % self.formater.formated_data_name.text())
            self.preview_table_model = TableModel(self.data.formated_data)
            self.preview_table.setModel(self.preview_table_model)
            self.preview_table.resizeColumnsToContents()
            self.preview.setGeometry(0, 30, self.preview_table.size().width(), self.preview_table.size().width())
            self.preview.show()
        else:
            QMessageBox.information(self, "No Data Source Set",
                                    "Verify There is a Data Source to Format,\nset 'Select Data' Option.",
                                    buttons=QMessageBox.StandardButton.Ok, defaultButton=QMessageBox.StandardButton.Ok)

    def save_formated(self):
        """
        Save formated data from Formater, from Data.
        """
        name = self.formater.formated_data_name.text()
        if name not in ['', 'Set Name'] and self.data.formated_data is not None:
            check = 1024
            if name in self.data.pqt_sources:
                check = QMessageBox.warning(self, "Save Source Data",
                                            "OverWrite Data: %s?" % name,
                                            buttons=QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
                                            defaultButton=QMessageBox.StandardButton.Cancel)
            if check == 1024:
                self.plot_map['data_name'] = name
                self.plot_map['data'] = self.formater.last_formated_data = self.data.save_formated(name)
                self.update_table()
                self.update_combo_boxes()
                self.data_selector.setCurrentIndex(self.data_selector.findText(self.plot_map['data_name']))
                self.formater.check_save_state()
        else:
            QMessageBox.information(self, "New Data Format is Unnamed",
                                    "Verify There is Data to Format.\nSet Name to Save Formated Data.",
                                    buttons=QMessageBox.StandardButton.Ok, defaultButton=QMessageBox.StandardButton.Ok)

    def save_plot_map(self, run_plot: bool):
        """
        Save current plot map.
        :param run_plot: Whether to render a plot after saving
        """
        from resources.modules.utility import save_plot_map
        self.plot_map_obj.update_data(self.plot_map)
        save_plot_map(self.plot_map_obj)
        if run_plot:
            self.plot_map_obj.run_plot()

    def update_delete_selector_button(self, index:int):
        """
        Update delete button with data parquet to remove.
        :param index: Index of Data pqt_sources
        """
        if index > 0:
            self.data_delete_button.setText('Delete Data: %s' % self.data.pqt_sources[index])
        else:
            self.data_delete_button.setText('Delete Data: ')

    def delete_data(self):
        """
        Delete data parquet after verification check.
        """
        index = self.data_delete_selector.currentIndex()
        if index > 0:
            check = QMessageBox.warning(self, "Delete Source Data",
                                        "Permanently Remove %s as Source Data?" % self.data_delete_selector.currentText(),
                                        buttons=QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
                                        defaultButton=QMessageBox.StandardButton.Cancel)
            if check == 1024:
                remove('saved/data/' + self.data.pqt_sources[index] + '.pqt')
                self.update_combo_boxes()