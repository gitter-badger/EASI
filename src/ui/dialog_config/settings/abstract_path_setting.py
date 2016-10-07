import os

import abc

from src.qt import QMenu, QAction, QToolButton

from src.low.custom_path import Path
from src.ui.dialog_browse.dialog import BrowseDialog
from src.ui.dialog_config.settings.abstract_config import AbstractConfigSetting


class AbstractPathSetting(AbstractConfigSetting):
    def __init__(self, dialog, value_name):
        AbstractConfigSetting.__init__(self, dialog, value_name)
        self.menu = QMenu(self.dialog)
        self.q_action_browse = QAction('Change location', self.dialog)
        self.q_action_show = QAction('Show in explorer', self.dialog)

    def dialog_has_changed_methods(self) -> list:
        return [self.qt_object.textChanged]

    def browse_for_dir(self):
        init_dir = self.value
        if init_dir is None:
            init_dir = 'c:/users'
        path = BrowseDialog.get_directory(
            parent=self.dialog,
            title='Select your {} directory'.format(self.dir_name()),
            init_dir=init_dir
        )
        if path:
            self.qt_object.setText(str(path.abspath()))

    def show_in_explorer(self):
        os.startfile(self.value)

    def setup(self):
        self.menu.addAction(self.q_action_browse)
        self.menu.addAction(self.q_action_show)
        self.qt_menu_btn.setMenu(self.menu)
        # noinspection PyUnresolvedReferences
        self.q_action_browse.triggered.connect(self.browse_for_dir)
        # noinspection PyUnresolvedReferences
        self.q_action_show.triggered.connect(self.show_in_explorer)

    def get_value_from_dialog(self):
        return self.qt_object.text()

    def validate_dialog_value(self) -> bool:
        p = Path(self.get_value_from_dialog())
        if not p.exists():
            self.show_tooltip('Directory does not exist')
        elif not p.isdir():
            self.show_tooltip('Not a directory')
        else:
            return True

    def set_dialog_value(self, value: str):
        self.qt_object.setText(str(value))

    @abc.abstractmethod
    def dir_name(self) -> str:
        """"""

    @property
    @abc.abstractproperty
    def qt_menu_btn(self) -> QToolButton:
        """"""