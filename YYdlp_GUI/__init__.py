from . import view, mycontrols, state, yt_dlp_wrapper
from .state import State, ReactiveState, Store, StateRefs


def main():
    v = view.View()
    v.run()
