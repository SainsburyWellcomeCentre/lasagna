#!/usr/bin/env bash
pyuic4 elastix_plugin.ui > elastix_plugin_UI.py
pyrcc4 -py3 ./elastix_plugin.qrc >  ./elastix_plugin_rc.py
pyuic4 transformix_plugin.ui > transformix_plugin_UI.py
pyuic4 reorder_stack.ui > reorder_stack_UI.py
pyuic4 selectstack.ui > selectstack_UI.py
