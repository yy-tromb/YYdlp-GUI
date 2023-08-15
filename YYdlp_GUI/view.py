import flet as ft
import mycontrols as myctls


def __init__():
    pass


class View:
    def __init__(self) -> None:
        self.views = ["main", "setting"]
        ft.app(target=self.main)

    def run(self) -> None:
        ft.app(target=self.main)

    def main(self, page: ft.Page) -> None:
        self.page = page
        page.title = "YYdlp-GUI v0.1"
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.MainAxisAlignment.CENTER
        # page.add(ft.Text(value="hoge",text_align=ft.TextAlign.CENTER))
        # ↑ code for not multiview (memo)
        self.mainView = MainView(page)
        self.settingsView = SettingsView(page)

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


class MainView:
    def __init__(self, page: ft.Page) -> None:
        self.page = page  # for page button
        self.view = ft.View(
            route="/main",
            appbar=myctls.MyAppBar(page=page, title="YYdlp-GUI v0.1"),
            controls=[
                ft.Text(value="hoge", text_align=ft.TextAlign.CENTER),
                ft.TextField(),
                ft.Image(
                    src="../resources/settings_FILL0_wght400_GRAD0_opsz48.png",
                    color=ft.colors.WHITE,
                ),
            ],
        )


class SettingsView:
    def __init__(self, page: ft.Page) -> None:
        self.page = page  # for page button
        self.view = ft.View(
            route="/settings",
            appbar=ft.AppBar(
                title=ft.Text("YYdlp-GUI v0.1 Settings"),
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
        dialog = ft.AlertDialog(
            title=ft.Row(
                controls=[
                    ft.Text("Settings is now developping.You can't available now")
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.MainAxisAlignment.CENTER,
            ),
            open=True
            # on_dismiss=lambda _:print("dissmissed")
        )
        self.page.dialog = dialog
        self.page.update()
