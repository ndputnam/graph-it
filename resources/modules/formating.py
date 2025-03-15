from copy import deepcopy
from typing import Union

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QWidget, QLabel, QGridLayout, QPushButton, QComboBox, QSlider, QLineEdit, QMessageBox
from pandas import DataFrame, Series

from resources.modules.stylesheets import button, combobox


class Formater(QWidget):
    def __init__(self, settings):
        """
        Modify data in settings window,
         apply it to a separate formated data Pandas Dataframe.
        :param settings: PlotMap settings window.
        """
        super().__init__(parent=settings)
        # VARS
        self.settings = settings
        self.last_formated_data = deepcopy(self.settings.data.formated_data)

        # SET FORMATED DATA SOURCE NAME
        formated_df_name_label = QLabel('Formated Data Title:')
        self.formated_data_name = QLineEdit('Set Name')


        # MERGE SELECTOR
        self.df_merge_selector = QComboBox()
        self.df_merge_selector.setStyleSheet(combobox)
        self.df_merge_selector.currentIndexChanged.connect(self.merge_selected)
        # MERGE BUTTON
        self.merge_index = 0
        self.df_merge_button = QPushButton("Merge Data: (none)")
        self.df_merge_button.setStyleSheet(button)
        self.df_merge_button.clicked.connect(lambda checked: self.validate_merge_dfs())
        self.df_merge_button.clicked.connect(lambda click: self.open_preview_table())

        # RANGE SELECTOR
        self.range_selector = QSlider()
        self.range_selector.setOrientation(Qt.Orientation.Horizontal)
        self.range_selector.valueChanged.connect(self.format_range)
        if self.settings.data.formated_data is not None:
            QTimer.singleShot(1000, self.update_range_selector)
        # SET RANGE BUTTON
        self.set_range_button = QPushButton('Apply %s Limit to All Columns' % (self.range_selector.value()))
        self.set_range_button.setStyleSheet(button)
        self.set_range_button.clicked.connect(lambda checked: self.set_format_range())
        self.set_range_button.clicked.connect(lambda click: self.open_preview_table())

        # SORT BY COLUMN SElECTOR
        self.format_coord_selector = QComboBox()
        self.format_coord_selector.setStyleSheet(combobox)
        self.format_coord_selector.addItem('Select Column')
        self.format_coord_selector.currentTextChanged.connect(self.sort_by_button_label)
        # SORT BY COLUMN BUTTON
        self.sort_by_button = QPushButton('Sort by: %s' % self.format_coord_selector.currentText())
        self.sort_by_button.setStyleSheet(button)
        self.sort_by_button.clicked.connect(lambda click: self.sort_by())
        self.sort_by_button.clicked.connect(lambda click: self.open_preview_table())

        # ADD INDEX COLUMN BUTTON
        add_index_button = QPushButton('Add An Index Column')
        add_index_button.setStyleSheet(button)
        add_index_button.clicked.connect(lambda click: self.add_index())
        add_index_button.clicked.connect(lambda click: self.open_preview_table())
        # REMOVE INDEX COLUMN BUTTON
        remove_index_button = QPushButton('Remove Index Column')
        remove_index_button.setStyleSheet(button)
        remove_index_button.clicked.connect(lambda click: self.remove_index())
        remove_index_button.clicked.connect(lambda click: self.open_preview_table())

        # LAYOUT
        layout = QGridLayout()
        layout.addWidget(formated_df_name_label, 0, 0)
        layout.addWidget(self.formated_data_name, 0, 1)
        layout.addWidget(self.df_merge_selector, 1, 0)
        layout.addWidget(self.df_merge_button, 1, 1)
        layout.addWidget(self.format_coord_selector, 2, 0)
        layout.addWidget(self.sort_by_button, 2, 1)
        layout.addWidget(self.range_selector, 3, 0)
        layout.addWidget(self.set_range_button, 3, 1)
        layout.addWidget(add_index_button, 4, 0)
        layout.addWidget(remove_index_button, 4, 1)
        layout.addWidget(QLabel('Format By'), 5, 0)
        layout.addWidget(QLabel('This'), 5, 1)
        layout.addWidget(QLabel('Format By'), 6, 0)
        layout.addWidget(QLabel('That'), 6, 1)
        layout.addWidget(QLabel('Format By'), 7, 0)
        layout.addWidget(QLabel('The Other Thing'), 7, 1)
        self.setLayout(layout)

    def check_save_state(self):
        """
        Update save formated data button to indicate
         if formated data has be changed or saved.
        :return: None
        """
        if self.settings.data.formated_data is not None:
            if self.settings.data.formated_data.equals(self.last_formated_data):
                self.settings.save_new_format_button.setText('Formated Data Saved')
            else:
                self.settings.save_new_format_button.setText('Formated Data Changed: SAVE')

    def open_preview_table(self):
        """
        Reimplements the preview window with new data,
         if the preview window is already open.
        :return: None
        """
        if self.settings.preview.isVisible():
            self.settings.open_preview_table()

    def update_range_selector(self):
        """
        Set range selector range based on size of formated data.
        :return: None
        """
        if isinstance(self.settings.data.formated_data, DataFrame):
            index = self.settings.data.formated_data.index
            fdf_min = index[0]
            self.fdf_max = index[-1] + 1
            self.range_selector.setRange(fdf_min, self.fdf_max)
            self.range_selector.setValue(self.fdf_max)

    def set_formated_data(self):
        """
        Establish valid formated data from plot map data,
         if data is a Pandas Dataframe.
        :return: None
        """
        if self.settings.plot_map['data'] is not None and isinstance(self.settings.plot_map['data'], DataFrame):
            self.settings.data.formated_data = deepcopy(self.settings.plot_map['data'])
            self.last_formated_data = deepcopy(self.settings.plot_map['data'])
            self.formated_data_name.setText(self.settings.plot_map['data_name'])
            self.update_range_selector()
        else:
            self.settings.data.formated_data = None
            self.formated_data_name.setText('Add Valid Source Data')
            self.range_selector.setRange(0, 0)

    def set_format_range(self):
        """
        Applies defined range from range selector to formated data.
        :return: None
        """
        if self.settings.data.formated_data is None:
            self.alert_invalid()
        else:
            if self.format_coord_selector.currentIndex() > 0:
                self.update_range_selector()
                column = self.format_coord_selector.itemText(self.format_coord_selector.currentIndex())
                limit = self.range_selector.value()
                self.settings.data.set_upper_range(column, limit)
                self.check_save_state()

    def format_range(self):
        """
        Update range button with range selector value.
        :return: None
        """
        self.set_range_button.setText('Apply %s Limit' % (self.range_selector.value()))

    def sort_by_button_label(self, text:str):
        """
        Update sort by button with coord selector value.
        Update set range button with range selector value and coord selector value.
        :param text: Coord selector value, coordinate names from plot map coordinates.
        :return: None
        """
        self.sort_by_button.setText('Sort by %s Column' % text)
        self.set_range_button.setText('Apply %s Limit to %s' % (self.range_selector.value(), text))

    def sort_by(self):
        """
        Sort formated dataframe by column defined with coord selector.
        :return: None
        """
        if self.settings.data.formated_data is None:
            self.alert_invalid()
        elif self.format_coord_selector.currentText():
            sorted_df = self.settings.data.formated_data.sort_values(by=self.format_coord_selector.currentText())
            self.settings.data.formated_data = sorted_df
            self.check_save_state()

    def add_index(self):
        """
        Add and indexed column to formated Dataframe.
        :return: None
        """
        if self.settings.data.formated_data is None:
            self.alert_invalid()
        else:
            if not 'index' in self.settings.data.formated_data.columns:
                data_size = len(self.settings.data.formated_data[self.settings.data.formated_data.columns[0]])
                ind = [i for i in range(data_size)]
                self.settings.data.formated_data.insert(0, 'index', Series(ind))
                self.format_coord_selector.insertItem(0, 'index')
                self.check_save_state()

    def remove_index(self):
        """
        Remove an existing indexed column from formated Dataframe.
        :return: None
        """
        if self.settings.data.formated_data is None:
            self.alert_invalid()
        else:
            if 'index' in self.settings.data.formated_data.columns:
                self.settings.data.formated_data.drop('index', inplace=True, axis=1)
                self.format_coord_selector.removeItem(0)
                self.check_save_state()

    def alert_invalid(self):
        """
        Notify if formated data doesn't exist.
        :return: None
        """
        QMessageBox.information(self.settings, "Invalid Data Source", "Can Only Format Unstructured Data",
                                buttons=QMessageBox.StandardButton.Ok,
                                defaultButton=QMessageBox.StandardButton.Ok)

    def merge_selected(self, index:int):
        """
        Set index of source data to be merged.
        :param index:  Index of data in Data pqt_sources.
        :return: None
        """
        if index > 0:
            self.merge_index = index
            self.df_merge_button.setText("Merge With %s" % self.settings.data.pqt_sources[index])

    def validate_merge_dfs(self):
        """
        Check for all necessary aspects to merge successfully.
        Need: Dataframe to merge,
              column to merge on,
              column must exist in both Dataframes.
        :return: None
        """
        if self.merge_index > 0:
            if self.format_coord_selector.currentIndex() > 0:
                self.df_merge_button.setText("Merging Data Sources...")
                df2, name = self.settings.data.get_df(self.merge_index)
                if [True for col2 in df2.columns for col1 in self.settings.plot_map['data'].columns if col1 == col2]:
                    check = QMessageBox.information(self, "Merge Data Sources",
                                                    "Begin Merging on Column %s\n With %s and %s\n\n"
                                                    "This Can be an Increasingly Long Process.\n"
                                                    "Please be Patient Until it is Finalized."
                                                    % (self.settings.plot_map['x_coord'],
                                                       self.settings.plot_map['data_name'],
                                                       name),
                                                    buttons=QMessageBox.StandardButton.Ok |
                                                            QMessageBox.StandardButton.Cancel,
                                                    defaultButton=QMessageBox.StandardButton.Cancel)
                    if check == 1024:
                        self.merge_df(df2)
                else:
                    QMessageBox.warning(self, "No Common Columns",
                                        "Both Data Sources Must Contain a Common Column",
                                        buttons=QMessageBox.StandardButton.Ok,
                                        defaultButton=QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(self, "No Column Selected",
                                    "Set the Coordinate to define which column to merge on.",
                                    buttons=QMessageBox.StandardButton.Ok,
                                    defaultButton=QMessageBox.StandardButton.Ok)
        else:
            QMessageBox.warning(self, "No Data Selected",
                                "Select Data to Merge.",
                                buttons=QMessageBox.StandardButton.Ok,
                                defaultButton=QMessageBox.StandardButton.Ok)

    def merge_df(self, df2: Union[DataFrame, dict, None]):
        """
        Merge a second Pandas Dataframe with the formated Dataframe.
        :param df2: secondary Dataframe.
        :return: None
        """
        on_column = self.format_coord_selector.currentText()
        merged_data = self.settings.data.merge_dfs(self.settings.plot_map['data'], df2, on_column)
        if merged_data is not None:
            self.settings.data.formated_data = merged_data
            self.df_merge_button.setText("Data Merged Successfully")
            self.check_save_state()
        else:
            self.df_merge_button.setText("Data Merge Failed...")