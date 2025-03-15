from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6 import QtPrintSupport


class Printer(QtCore.QObject):
    def __init__(self, view, parent=None):
        """
        Method for calling the default system printer display,
         to print out renderings of the current plot map graph.
        :param view: Object to view renderings.
        :param parent: Output window.
        """
        super().__init__(parent)
        self._view = view
        self._view.printRequested.connect(self.preview)
        self._view.printFinished.connect(self.handleFinished)
        self._printing = False
        self._loop = QtCore.QEventLoop(self)

    def print(self):
        """
        Calls default printer options display.
        :return: None
        """
        printer = QtPrintSupport.QPrinter(
            QtPrintSupport.QPrinter.PrinterMode.HighResolution)
        dialog = QtPrintSupport.QPrintDialog(printer, self._view)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.render(printer)
        dialog.deleteLater()

    def preview(self):
        """
        Calls default printer preview display.
        :return: None
        """
        if not self._printing:
            self._printing = True
            printer = QtPrintSupport.QPrinter()
            printer.setResolution(300)
            dialog = QtPrintSupport.QPrintPreviewDialog(printer, self._view)
            dialog.paintRequested.connect(self.render)
            dialog.exec()
            dialog.deleteLater()
            self._printing = False

    def render(self, printer):
        """
        Renders graph to the printer preview.
        :param printer: Printer object.
        :return: None
        """
        QtWidgets.QApplication.setOverrideCursor(
            QtCore.Qt.CursorShape.WaitCursor)
        self._view.print(printer)
        self._loop.exec(
            QtCore.QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)

    def handleFinished(self, success):
        """
        Update if printed successfully.
        :param success: True if printed.
        :return: None
        """
        if not success:
            painter = QtGui.QPainter()
            if painter.begin(self._printer):
                font = QtGui.QFont(painter.font())
                font.setPixelSize(20)
                painter.setFont(font)
                painter.drawText(
                    QtCore.QPointF(10, 25),
                    'Could not generate print preview')
                painter.end()
        self._loop.quit()
        QtWidgets.QApplication.restoreOverrideCursor()