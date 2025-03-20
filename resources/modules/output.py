from json import dump

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from PyQt6.QtWidgets import (QDialog, QPushButton, QLabel, QLineEdit, QComboBox,
                             QSlider, QMessageBox, QGridLayout, QFileDialog, QTextEdit)

from resources.modules.utility import COLORS


class OutputOptions(QDialog):
    def __init__(self, main_win):
        """
        Outputs the currently rendered plot as a designated image or data style.
        :param main_win: Main Window.
        """
        QDialog.__init__(self, parent=main_win)
        # WINDOW DETAILS
        self.setWindowTitle('Plot Output Options')
        self.setWindowIcon(main_win.icon)
        # VARS
        self.spec = main_win.spec
        self.tabs = main_win.tabs
        self.plots = main_win.plots
        # SET OUTPUT DIRECTORY
        self.output_dir = self.spec['output_dir'] if self.spec['output_dir'] else 'saved/outputs'
        output_dir_button = QPushButton('Change Output Folder')
        output_dir_button.clicked.connect(self.set_output_dir)
        # SET OUTPUT NAME
        output_name_label = QLabel('Set Name For Image:')
        self.output_name = QLineEdit(self)
        # SET OUTPUT EXTENSION TYPE
        output_format_label = QLabel('Set Image Type:')
        self.output_formats = ['png', 'pdf', 'svg', 'eps', 'ps']
        self.output_format = self.output_formats[0]
        select_format = QComboBox(parent=self)
        select_format.addItems(self.output_formats)
        select_format.currentIndexChanged.connect(self.set_output_format)
        # SET OUTPUT RESOLUTION
        output_resolution_label = QLabel('Set Resolution:')
        self.output_resolutions = {'low (100 dpi)': 100, 'mid (300 dpi)': 300,
                                   'high (1200 dpi)': 1200, 'ultra (2000 dpi)': 2000}
        self.output_res = self.output_resolutions['mid (300 dpi)']
        select_res = QComboBox(parent=self)
        select_res.addItems([res for res in self.output_resolutions.keys()])
        select_res.currentTextChanged.connect(self.set_output_res)
        select_res.setCurrentIndex(1)
        # SET OUTPUT TRANSPARENCY
        output_trans_label = QLabel('Set Transparency:')
        self.output_trans = False
        self.select_output_trans = QPushButton('Opaque Image')
        self.select_output_trans.clicked.connect(lambda click: self.set_output_trans())
        # SET OUTPUT PADDING
        self.output_padding = 0.0
        self.output_padding_label = QLabel('Image Padding: %s"' % self.output_padding)
        select_output_padding = QSlider(self)
        select_output_padding.setOrientation(Qt.Orientation.Horizontal)
        select_output_padding.setRange(0, 20)
        select_output_padding.valueChanged.connect(self.set_output_padding)
        select_output_padding.setValue(1)
        # SET OUTPUT BACKGROUND COLOR
        self.output_color = COLORS[0]
        select_color_label = QLabel('Set BG Color')
        self.select_output_color = QComboBox()
        self.select_output_color.setStyleSheet("QComboBox::editable {background-color: %s;}" % self.output_color)
        for i in range(len(COLORS)):
            self.select_output_color.addItem(COLORS[i])
            self.select_output_color.setItemData(i, QColor(COLORS[i]), Qt.ItemDataRole.DecorationRole)
        self.select_output_color.setCurrentIndex(COLORS.index(self.output_color))
        self.select_output_color.currentIndexChanged.connect(self.set_output_color)
        # OUTPUT RENDERED PLOT BUTTON
        output_button = QPushButton('Output', parent=self)
        output_button.clicked.connect(lambda click: self.output())
        # PRINT RENDERED PLOT BUTTON
        self.print_button = QPushButton('Print', parent=self)
        self.print_button.clicked.connect(lambda click: self.print())
        # MAIN LAYOUT
        output_win_layout = QGridLayout(self)
        output_win_layout.addWidget(output_dir_button, 0, 0, 1, 2)
        output_win_layout.addWidget(output_name_label, 1, 0)
        output_win_layout.addWidget(self.output_name, 1, 1)
        output_win_layout.addWidget(output_format_label, 2, 0)
        output_win_layout.addWidget(select_format, 2, 1)
        output_win_layout.addWidget(output_resolution_label, 3, 0)
        output_win_layout.addWidget(select_res, 3, 1)
        output_win_layout.addWidget(output_trans_label, 4, 0)
        output_win_layout.addWidget(self.select_output_trans, 4, 1)
        output_win_layout.addWidget(self.output_padding_label, 5, 0)
        output_win_layout.addWidget(select_output_padding, 5, 1)
        output_win_layout.addWidget(select_color_label, 6, 0)
        output_win_layout.addWidget(self.select_output_color, 6, 1)
        output_win_layout.addWidget(output_button, 7, 0)
        output_win_layout.addWidget(self.print_button, 7, 1)
        self.setLayout(output_win_layout)

    def set_output_dir(self):
        """
        Define output directory to place rendered output.
        will save this location as a reference point for future outputs.
        """
        output_dir = QFileDialog.getExistingDirectory(self, 'Destination Folder For Outputting Plot', self.output_dir)
        if output_dir:
            self.spec['output_dir'] = self.output_dir = output_dir
            with open('saved/spec.json', 'w') as f: dump(self.spec, f)

    def set_output_format(self, index:int):
        """
        Defines output extension format.
        :param index: Index reference for list of available extensions.
        """
        self.output_format = self.output_formats[index]

    def set_output_res(self, index:int):
        """
        Define output image resolution level.
        Levels: low: 100 dpi - good image with low memory size.
                mid: 300 dpi - default, standard high quality image.
                high 1200 dpi - high resolution image.
                ultra 2000 dpi - highest possible value, rare use case.
        :param index: Index reference for dictionary of levels.
        """
        self.output_res = self.output_resolutions[index]

    def set_output_trans(self):
        """
        Sets whether to give output image a transparent background.
        """
        self.output_trans = not self.output_trans
        if self.output_trans: self.select_output_trans.setText('Transparent Image')
        else: self.select_output_trans.setText('Opaque Image')

    def set_output_padding(self, index:int):
        """
        Defines boarder padding for output image.
        :param index:
        """
        self.output_padding = index / 10
        self.output_padding_label.setText('Image Padding: %s"' % self.output_padding)

    def set_output_color(self, index:int):
        """
        Set primary background color of output image.
        :param index: Index reference for color name in COLORS.
        """
        self.output_color = COLORS[index]
        self.select_output_color.setStyleSheet("QComboBox::editable {background-color: %s;}" % self.output_color)

    def output(self):
        """
        Verifies plot data is valid to output.
        Renders and outputs current plot map plot.
        Output extensions: .png, .pdf, .svg, .eps, .ps
        """
        plot_fig = self.plots[self.tabs.currentIndex()].plot_canvas.fig
        axes = plot_fig.axes
        if axes:
            name = self.output_name.text()
            if name:
                plot_fig.savefig('%s/%s.%s' % (self.output_dir, name, self.output_format),
                                 transparent=self.output_trans, dpi=self.output_res, bbox_inches='tight',
                                 pad_inches=self.output_padding, facecolor=self.output_color, edgecolor='black')
            else:
                QMessageBox.critical(self, "No Name Set", "Input Name to Output Plot.",
                                     buttons=QMessageBox.StandardButton.Ok,
                                     defaultButton=QMessageBox.StandardButton.Ok)
        else:
            QMessageBox.critical(self, "No Plot Created", "Run Plot to Create Plot Object to be Output.",
                                 buttons=QMessageBox.StandardButton.Ok,
                                 defaultButton=QMessageBox.StandardButton.Ok)

    def print(self):
        """
        IN DEVELOPMENT
        Will print out the current PlotMap rendered graph.
        """
        plot_fig = self.plots[self.tabs.currentIndex()].plot_canvas.canvas.figure
        plot_canvas = self.plots[self.tabs.currentIndex()].plot_canvas
        axes = plot_fig.axes
        if axes:
            self.print_button.setText('Print Function\nIn Development')
            try:
                # print('print testing')
                # buffer = plot_canvas.canvas.print_to_buffer()
                # print('buffer: %s' % buffer)

                # win = QDialog(self)
                # button = QPushButton()
                # win.printRequested = button.clicked
                # text = QTextEdit()
                # win.printFinished = text.textChanged
                # win_layout = QGridLayout()
                # win_layout.addWidget(button)
                # win_layout.addWidget(text)
                # win.setLayout(win_layout)
                # win.show()
                # printer = Printer(win)
                # printer.preview()

                # name = self.output_name.text()
                # img = plot_fig.savefig('%s/%s.%s' % (self.output_dir, name, self.output_format),
                #                  transparent=self.output_trans, dpi=self.output_res, bbox_inches='tight',
                #                  pad_inches=self.output_padding, facecolor=self.output_color, edgecolor='black')

                text_edit = QTextEdit()
                text_edit.setPlainText('Printing Functionality is in Development\nand Will be Available Shortly.')

                printer = QPrinter()
                dialog = QPrintDialog(printer, plot_canvas)
                # dialog.setOption(QAbstractPrintDialog.PrintDialogOption.PrintPageRange)
                # dialog.setOption(QAbstractPrintDialog.PrintDialogOption.PrintSelection)
                # dialog.setOption(QAbstractPrintDialog.PrintDialogOption.PrintToFile)
                # dialog.setOption(QAbstractPrintDialog.PrintDialogOption.PrintCollateCopies)
                # preview =QPrintPreviewWidget(printer)
                # preview.paintRequested.connect()
                # printer.newPage()

                if dialog.exec():
                    # buffer = plot_canvas.canvas.print_to_buffer()
                    text_edit.print(printer)
            except Exception as e:
                print(e)

    def as_csv(self):
        """
        Future, to output data as csv.
        """
        pass