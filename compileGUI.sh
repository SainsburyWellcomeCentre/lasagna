#!/usr/bin/env bash
pyuic5 ./designerFiles/lasagna_mainWindow.ui > ./lasagna_mainWindow.py
pyrcc5 ./designerFiles/mainWindow.qrc >  ./mainWindow_rc.py
pyuic5 ./designerFiles/alert.ui > ./alert_UI.py
