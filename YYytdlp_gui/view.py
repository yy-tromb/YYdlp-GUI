import flet

def __init__():
    pass

class View:
    def __init__(self) -> "View":
        flet.app(target=self.main)
        self
    
    def main(self,page :flet.Page):
        page.title="YYytdlp_gui v0.1"
        page.vertical_alignment = flet.MainAxisAlignment.CENTER
        page.horizontal_alignment = flet.MainAxisAlignment.CENTER
        # page.add(flet.Text(value="hoge",text_align=flet.TextAlign.CENTER))
        page.views.append(MainView().view)
        page.update()

class MainView:
    def __init__(self) -> "MainView":
        self.view=flet.View("/main",appbar=flet.AppBar(title="YYytdlp_gui v0.1",bgcolor=flet.colors.ORANGE),controls=[flet.Text(value="hoge",text_align=flet.TextAlign.CENTER)])
