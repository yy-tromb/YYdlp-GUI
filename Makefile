PYINSTALLER = pyinstaller
ENTRYPOINT = YYdlp_GUI/__main__.py
OUTPUTTYPE = --onedir
OPTIONS = --noconfirm
RELEASEOPTIONS = -w
DEBUGOPTIONS = --debug all

NAME = YYdlp-GUI

RM = del
RD = rd

debug:
	poetry shell
	$(PYINSTALLER) $(ENTRYPOINT) $(OUTPUTTYPE) $(OPTIONS) $(DEBUGOPTIONS) -n $(NAME)

release:
	poetry shell
	$(PYINSTALLER) $(ENTRYPOINT) $(OUTPUTTYPE) $(OPTIONS) $(RELEASEOPTIONS) -n $(NAME)


clean:
	$(RM) $(NAME).spec
	$(RD) build dist

re:
	make clean
	make
