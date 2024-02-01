from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QStyleFactory


def style(app):
    # app.setStyle("Fusion")
    app.setStyle(QStyleFactory.create("Fusion"))

    # app.setStyleSheet("QTreeWidgetItem {margin: 20px}")
    # app.setStyleSheet("QTreeWidget {margin: 5px}")

    # Palette to switch to dark colors:
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    # palette.setColor(QPalette.ToolTipBase, Qt.black)
    palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
    # palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    palette.setColor(QPalette.Disabled, QPalette.Window, palette.window().color().lighter())
    palette.setColor(QPalette.Disabled, QPalette.WindowText, palette.windowText().color().lighter())
    palette.setColor(QPalette.Disabled, QPalette.Base, palette.base().color().lighter())
    palette.setColor(QPalette.Disabled, QPalette.AlternateBase, palette.alternateBase().color().lighter())
    palette.setColor(QPalette.Disabled, QPalette.ToolTipBase, palette.toolTipBase().color().lighter())
    palette.setColor(QPalette.Disabled, QPalette.ToolTipText, palette.toolTipText().color().lighter())
    palette.setColor(QPalette.Disabled, QPalette.Text, palette.text().color().lighter())
    palette.setColor(QPalette.Disabled, QPalette.Button, palette.button().color().lighter())
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, palette.buttonText().color().lighter())
    palette.setColor(QPalette.Disabled, QPalette.BrightText, palette.brightText().color().lighter())
    palette.setColor(QPalette.Disabled, QPalette.Link, palette.link().color().lighter())
    palette.setColor(QPalette.Disabled, QPalette.Highlight, palette.highlight().color().lighter())
    palette.setColor(QPalette.Disabled, QPalette.HighlightedText, palette.highlightedText().color().lighter())
    app.setPalette(palette)

    # Set the tooltip stylesheet (needed in PySide6...)
    tooltip_style = "QToolTip { color: #ffffff; background-color: #000000; border: none; }"
    app.setStyleSheet(tooltip_style)


def select_icon(dir_, slash, extension):
    if extension in ["png", "PNG", "jpeg", "JPEG", "jpg", "JPG", "bmp", "BMP"]:
        icon = dir_ + slash + "icon" + slash + "image.png"
    elif extension in ["docx", "DOCX", "odt", "ODT"]:
        icon = dir_ + slash + "icon" + slash + "document-word.png"
    elif extension in ["pdf", "PDF"]:
        icon = dir_ + slash + "icon" + slash + "document-pdf.png"
    elif extension in ["xlsx", "XSLX", "ods", "ODS", "csv", "CSV"]:
        icon = dir_ + slash + "icon" + slash + "document-excel.png"
    elif extension in ["ino", "INO", "py", "PY", "pyw", "PYW", "cpp", "CPP", "h", "H", "o", "O", "c", "C", "js", "JS",
                       "class", "CLASS", "html", "HTML", "htm", "HTM", "xml", "XML", "yaml", "YAML", "yml", "YML",
                       "json", "JSON", "conf", "CONF"]:
        icon = dir_ + slash + "icon" + slash + "document-code.png"
    else:
        icon = dir_ + slash + "icon" + slash + "document--arrow.png"

    return icon
