pyside2-rcc src/resources.qrc -o src/rc_ressources.py
pyside2-uic src/fastanalyzer.ui > src/ui_fastanalyzer.py
pyside2-uic src/plot.ui > src/ui_plot.py
pyside2-uic src/plot_settings.ui > src/ui_plot_settings.py
python src/fastanalyzer.py
