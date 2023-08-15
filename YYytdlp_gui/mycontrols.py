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
                    ft.Text(value=self.title,
                            color=ft.colors.WHITE,
                            size=30),
                    ft.ElevatedButton(
                        text="Settings",
                        on_click=lambda _: self.page.go("/settings"),
                        color=ft.colors.WHITE,
                        bgcolor=ft.colors.BLUE_900,
                    ),
                    ft.Image(src=f"../resources/settings_FILL0_wght400_GRAD0_opsz48.svg",
                             width=50,height=50,
                             fit=ft.ImageFit.CONTAIN,)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.MainAxisAlignment.CENTER,
            ),bgcolor=ft.colors.ORANGE_700,
        )
