cd ./YYdlp_GUI
pyinstaller ./YYdlp_GUI.spec -y
for %%f in (./*.py) do copy "%%f" "dist\YYdlp_GUI\%%f"
