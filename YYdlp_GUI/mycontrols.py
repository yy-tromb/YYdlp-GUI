import flet as ft
from typing import Callable

class MyAppBar(ft.UserControl):
    """MyAppBar
    Flutter AppBar + Setting Button

    Args:None
    """

    def __init__(self,title: str,on_settings_button_click: Callable):
        super().__init__()
        self.on_settings_button_click: Callable=on_settings_button_click
        self.title: str = title

    def build(self):
        return ft.Container(
            ft.Row(
                controls=[
                    ft.Text(value=self.title, color=ft.colors.WHITE, size=30),
                    ft.IconButton(
                        ft.icons.SETTINGS,
                        on_click=self.on_settings_button_click,
                        icon_color=ft.colors.WHITE,
                        bgcolor=ft.colors.BLUE_900,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                expand=1,
            ),
            bgcolor=ft.colors.ORANGE_700,
        )
