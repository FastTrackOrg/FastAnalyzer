pyside2-rcc src/resources.qrc -o src/rc_ressources.py
pyside2-uic src/main.ui > src/ui_main.py
pyside2-uic src/plot.ui > src/ui_plot.py
pyside2-uic src/plot_settings.ui > src/ui_plot_settings.py
python src/main.py
