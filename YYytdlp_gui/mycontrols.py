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
        return ft.Row(
            controls=[
                ft.Text(value=self.title),
                ft.ElevatedButton(
                    text="Settings", on_click=lambda _: self.page.go("/settings")
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
