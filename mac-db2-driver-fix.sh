#!/bin/zsh
# Only need to execute this when running on mac
cd venv/lib/python3.7/site-packages/ || exit
install_name_tool -change libdb2.dylib $(pwd)/libdb2.dylib ibm_db.cpython-37m-darwin.so
if test -f "$PWD/libdb2.dylib"; then
  rm libdb2.dylib
fi
ln -s /usr/local/lib/python3.7/site-packages/clidriver/lib/libdb2.dylib libdb2.dylib
