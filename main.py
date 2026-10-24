import sys
import ui

def main():
    app = ui.QApplication(sys.argv)
    if ui.os.path.exists(ui.UI_FILE):
        with open(ui.UI_FILE, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    try:
        fenetre = ui.SorWindow()
    except RuntimeError as e:
        ui.QMessageBox.critical(None, "UI mismatch", str(e))
        sys.exit(1)
    fenetre.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()