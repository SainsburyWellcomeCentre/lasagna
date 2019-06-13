#!/usr/bin/env bash
pyuic5 elastix_plugin.ui > elastix_plugin_UI.py
pyrcc5 ./elastix_plugin.qrc >  ./elastix_plugin_rc.py
pyuic5 transformix_plugin.ui > transformix_plugin_UI.py
pyuic5 reorder_stack.ui > reorder_stack_UI.py
pyuic5 selectstack.ui > selectstack_UI.py
