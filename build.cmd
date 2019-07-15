mkdir dist\adif-files
pyinstaller -F --add-data "app\templates;app\templates" mamadif.py