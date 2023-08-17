import flet as ft


class MyAppBar(ft.UserControl):
    """MyAppBar
    Flutter AppBar + Setting Button

    Args:None
    """

    def __init__(self, page: ft.Page, title: str):
        super().__init__()
        self.page = page
        self.title = title

    def build(self):
        return ft.Container(
            ft.Row(
                controls=[
                    ft.Text(value=self.title, color=ft.colors.WHITE, size=30),
                    ft.IconButton(
                        ft.icons.SETTINGS,
                        on_click=lambda _: self.page.go("/settings"),
                        icon_color=ft.colors.WHITE,
                        bgcolor=ft.colors.BLUE_900,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.MainAxisAlignment.CENTER,
                expand=1,
                spacing=""
            ),
            bgcolor=ft.colors.ORANGE_700,
        )
