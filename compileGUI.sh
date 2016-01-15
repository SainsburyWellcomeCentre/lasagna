#!/usr/bin/env bash
pyuic4 ./designerFiles/lasagna_mainWindow.ui > ./lasagna_mainWindow.py
# ./modifyUIfile.pl # useful to add lasagna viewbox but that hsouldn't be needed anymore
pyrcc4 ./designerFiles/mainWindow.qrc >  ./mainWindow_rc.py
pyuic4 ./designerFiles/alert.ui > ./alert_UI.py
