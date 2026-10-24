import sys
import ui

def main():
    app = ui.QApplication(sys.argv)
    fenetre = ui.SorWindow()
    fenetre.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()