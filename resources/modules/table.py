from copy import deepcopy

from PyQt6.QtCore import Qt, QAbstractTableModel
from PyQt6.QtGui import QColor
from numpy import int64, interp
from pandas import DataFrame, isna


class TableModel(QAbstractTableModel):
    def __init__(self, data):
        """
        Define parameters for color coding.
        Restructure dictionary into flattened Dataframe if needed.
        :param data: Panda Dataframe or dictionary of Numpy arrays
        """
        super().__init__()
        self._data = deepcopy(data)
        self.colors = [QColor(0, 255, 255, 100), QColor(0, 231, 255, 100), QColor(0, 206, 255, 100),
                       QColor(0, 181, 255, 100), QColor(0, 157, 255, 100), QColor(0, 132, 255, 100),
                       QColor(0, 108, 255, 100), QColor(0, 84, 255, 100), QColor(0, 59, 255, 100),
                       QColor(0, 34, 255, 100), QColor(0, 10, 255, 100), QColor(14, 0, 255, 100),
                       QColor(39, 0, 255, 100), QColor(63, 0, 255, 100), QColor(88, 0, 255, 100),
                       QColor(112, 0, 255, 100), QColor(137, 0, 255, 100), QColor(161, 0, 255, 100),
                       QColor(186, 0, 255, 100), QColor(210, 0, 255, 100), QColor(235, 0, 255, 100)]
        if isinstance(self._data, dict):
            for col in self._data:
                self._data[col] = self._data[col].reshape(-1)
            self._data = DataFrame(self._data)
        self.colors_min = [self._data[col][self._data[col].idxmin()] for col in self._data]
        self.colors_max = [self._data[col][self._data[col].idxmax()] for col in self._data]

    def data(self, index, role=...):
        """
        Structure table data.
        :param index: Index for referenced data.
        :param role: Specify data role in reference.
        :return: Data value at index.
        """
        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            if isna(value):
                value = ''
            return str(value)
        if role == Qt.ItemDataRole.BackgroundRole:
            value = self._data.iloc[index.row(), index.column()]
            if (isinstance(value, int) or isinstance(value, float) or isinstance(value, int64)) and not isna(value):
                min_col_val = self.colors_min[index.column()]
                max_col_val = self.colors_max[index.column()]
                value = int(interp(value, [min_col_val, max_col_val], [0, 20]))
                return self.colors[value]

    def rowCount(self, parent=...):
        """
        Structure table rows.
        :param parent: Unused.
        :return: Number of rows.
        """
        return self._data.shape[0]

    # def columnCount(self, index):
    def columnCount(self, parent=...):
        """
        Structure table columns.
        :param parent: Unused.
        :return: Number of columns.
        """
        return self._data.shape[1]

    def headerData(self, section, orientation, role=...):
        """
        Structures table header and body.
        :param section: Index for data in column or row.
        :param orientation: Vert or horz alignment.
        :param role: Specify header role in reference.
        :return: Column and row data
        """
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])
            if orientation == Qt.Orientation.Vertical:
                return str(self._data.index[section])