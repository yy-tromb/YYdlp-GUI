pyinstaller ./YYdlp_GUI/YYdlp_GUI.spec -y
for %%f in (./YYdlp_GUI/*.py) do copy "YYdlp_GUI\%%f" "YYdlp_GUI\dist\YYdlp_GUI\%%f"
