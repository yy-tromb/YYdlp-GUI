PYINSTALLER = python -m PyInstaller
ENTRYPOINT = YYdlp_GUI/__main__.py
OUTPUTTYPE = --onedir
OPTIONS = --noconfirm
RELEASEOPTIONS = -w
DEBUGOPTIONS = --debug all

NAME = YYdlp-GUI

RM = del
RD = rd /s /q

debug:
	poetry -v run $(PYINSTALLER) $(ENTRYPOINT) $(OUTPUTTYPE) $(OPTIONS) $(DEBUGOPTIONS) -n $(NAME)

release:
	poetry -v run $(PYINSTALLER) $(ENTRYPOINT) $(OUTPUTTYPE) $(OPTIONS) $(RELEASEOPTIONS) -n $(NAME)

onefile:
	poetry -v run $(PYINSTALLER) $(ENTRYPOINT) --onefile $(OPTIONS) $(RELEASEOPTIONS) -n $(NAME)_onefile


clean:
	$(RM) $(NAME).spec
	$(RD) build dist

re:
	make clean
	make
