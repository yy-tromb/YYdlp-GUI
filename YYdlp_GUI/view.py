import flet as ft
from .mycontrols import MyAppBar
import abc
from .wrap_ytdlp import MediaInfo, MediaDownLoad


def __init__():
    pass


class IMyView(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, page: ft.Page) -> None:
        raise NotImplementedError()

    view: ft.View


class MainView(IMyView):
    def __init__(self, page: ft.Page) -> None:
        self.page: ft.Page = page  # for page button
        self.title = "YYdlp-GUI v0.1"
        self.view: ft.View = ft.View(
            route="/main",
            appbar=MyAppBar(
                title="YYdlp-GUI v0.1",
                on_settings_button_click=lambda _: page.go("/settings"),
            ),
            controls=[
                ft.Text(value="hoge", text_align=ft.TextAlign.CENTER),
                ft.TextField(),
            ],
        )


class SettingsView(IMyView):
    def __init__(self, page: ft.Page) -> None:
        self.page: ft.Page = page  # for page button
        self.view: ft.View = ft.View(
            route="/settings",
            appbar=ft.AppBar(
                title=ft.Text("YYdlp-GUI v0.1 Settings"),
                color=ft.colors.WHITE,
                bgcolor=ft.colors.ORANGE_700,
            ),
            controls=[
                ft.Text(
                    value="Settings is now developping.You can't available now",
                ),
                ft.TextField(),
            ],
        )

    def on_changed_page(self) -> None:
        dialog: ft.AlertDialog = ft.AlertDialog(
            title=ft.Row(
                controls=[
                    ft.Text("Settings is now developping.You can't available now")
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                expand=1,
            ),
            open=True
            # on_dismiss=lambda _:print("dissmissed")
        )
        self.page.dialog = dialog
        self.page.update()


class View:
    def __init__(
        self,
        mainView: type[IMyView] = MainView,
        settingsView: type[IMyView] = SettingsView,
    ) -> None:
        self.views = ["main", "setting"]
        self.mainViewClass=mainView
        self.settingsViewClass=settingsView

    def run(self) -> None:
        ft.app(target=self.main)

    def main(
        self,
        page: ft.Page
    ) -> None:
        self.page: ft.Page = page
        page.title = "YYdlp-GUI v0.1"
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        # page.add(ft.Text(value="hoge",text_align=ft.TextAlign.CENTER))
        # ↑ code for not multiview (memo)
        self.mainView: IMyView = self.mainViewClass(page)
        self.settingsView: IMyView = self.settingsViewClass(page)

        page.on_route_change = self.__on_route_change
        page.on_view_pop = self.__on_pop_view

        page.views.clear()
        page.go("/main")

    def __on_route_change(self, handler):
        # troupe = ft.TemplateRoute(handler.route)
        self.page.views.clear()
        self.page.views.append(self.mainView.view)
        if self.page.route == "/settings":
            self.page.views.append(self.settingsView.view)
            self.settingsView.on_changed_page()
        elif self.page.route == "/main":
            pass
        #    self.page.views.append(MainView(self.page).view)
        # "/main" has already appended
        else:
            print(self.page.route)
        self.page.update()

    def __on_pop_view(self, handler):
        self.page.views.pop()
        if len(self.page.views) > 1:
            self.page.update()
        else:
            self.page.go("/main")  # for all page not deleted
