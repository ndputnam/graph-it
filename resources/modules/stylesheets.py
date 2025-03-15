"""
Style Sheets for GUI Widgets.
"""

button = """
    QPushButton {
        background-color: grey;
        color: black;
        border: 1px solid white;
        border-radius: 12px;
        font-size: 16px;
        padding: 2px 5px 3px 5px 
    }
    QPushButton:hover {
        background-color: cadetblue;
    }
    QPushButton:pressed {
        background-color: yellow;
    }
"""

combobox = """
    QComboBox::indicator{
        background-color:transparent;
        selection-background-color:transparent;
        color:transparent;
        selection-color:transparent;
    }
    QComboBox:item {
        padding-left: 20px;  /* move text right to make room for tick mark */
    }
    QComboBox:item:selected {
        padding-left: 20px;  /* move text right to make room for tick mark */
        border: 2px solid black;
    }
    QComboBox:item:checked {
        padding-left: 20px;  /* move text right to make room for tick mark */
        font-weight: bold;
    }
"""

tabs = """
    QTabBar::tab:left:selected {
        background-color: blue;
        color: yellow;
        margin-right: 5px;
    }
    QTabBar::tab:left:!selected {
        background_color: orange;
        color: magenta;
        margin-right: 2px;
    }
    QTabBar::tab:left {
        min-height: 15ex;
        margin: -25px 15px 5px 5px;
        padding: 5px -1px 10px 5px;
    }
"""