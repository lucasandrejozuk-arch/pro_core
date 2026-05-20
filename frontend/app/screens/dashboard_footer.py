from __future__ import annotations

from PySide6.QtCore import QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QMenuBar, QMessageBox, QVBoxLayout


def build_dashboard_footer(self, scroll_area) -> None:
    self.session_footer = QFrame()
    self.session_footer.setObjectName("sessionFooter")
    session_footer_layout = QHBoxLayout(self.session_footer)
    session_footer_layout.setContentsMargins(10, 4, 10, 4)
    session_footer_layout.setSpacing(8)
    self.session_footer_label = QLabel("Sessao: -")
    self.session_footer_label.setObjectName("sessionFooterText")
    self.backend_status_dot = QLabel("●")
    self.backend_status_dot.setObjectName("footerStatusDot")
    self.backend_status_dot.setProperty("level", "error")
    self.backend_status_text = QLabel("Backend: desconectado")
    self.backend_status_text.setObjectName("sessionFooterText")
    self.internal_server_status_dot = QLabel("●")
    self.internal_server_status_dot.setObjectName("footerStatusDot")
    self.internal_server_status_dot.setProperty("level", "warning")
    self.internal_server_status_text = QLabel("Servidor interno: pendente")
    self.internal_server_status_text.setObjectName("sessionFooterText")
    self.footer_message_label = QLabel("")
    self.footer_message_label.setObjectName("footerMessage")
    self.footer_message_label.setProperty("level", "info")
    self.session_module_label = QLabel("Painel Principal")
    self.session_module_label.setObjectName("sessionFooterModule")
    session_footer_layout.addWidget(self.session_footer_label)
    session_footer_layout.addStretch()
    session_footer_layout.addWidget(self.footer_message_label, 1)
    session_footer_layout.addWidget(self.backend_status_dot)
    session_footer_layout.addWidget(self.backend_status_text)
    session_footer_layout.addWidget(self.internal_server_status_dot)
    session_footer_layout.addWidget(self.internal_server_status_text)
    session_footer_layout.addWidget(self.session_module_label)

    self.session_timer = QTimer(self)
    self.session_timer.setInterval(1000)
    self.session_timer.timeout.connect(self._refresh_session_footer)
    self.session_timer.start()

    main_area = QFrame()
    main_area.setObjectName("mainArea")
    main_area_layout = QHBoxLayout(main_area)
    main_area_layout.setContentsMargins(0, 0, 0, 0)
    main_area_layout.setSpacing(0)
    main_area_layout.addWidget(self.sidebar)
    main_area_layout.addWidget(scroll_area, 1)

    self.menu_bar = QMenuBar()
    file_menu = self.menu_bar.addMenu("Arquivo")
    settings_action = QAction("Configuracoes", self)
    settings_action.triggered.connect(lambda: self.module_selected.emit("settings"))
    file_menu.addAction(settings_action)
    file_menu.addSeparator()
    logout_action = QAction("Sair", self)
    logout_action.triggered.connect(self.logout_requested.emit)
    file_menu.addAction(logout_action)

    edit_menu = self.menu_bar.addMenu("Editar")
    details_action = QAction("Dados completos", self)
    details_action.triggered.connect(self._open_record_details)
    edit_menu.addAction(details_action)
    editor_action = QAction("Editor de registro", self)
    editor_action.triggered.connect(self._open_record_editor)
    edit_menu.addAction(editor_action)

    selection_menu = self.menu_bar.addMenu("Selecao")
    clear_selection_action = QAction("Limpar selecao", self)
    clear_selection_action.triggered.connect(self._clear_current_selection)
    selection_menu.addAction(clear_selection_action)

    about_menu = self.menu_bar.addMenu("Sobre")
    about_action = QAction("Sobre o Pro Core", self)
    about_action.triggered.connect(
        lambda: QMessageBox.information(
            self,
            "Sobre",
            "PRO CORE\nSistema de gestao operacional.",
        )
    )
    about_menu.addAction(about_action)

    layout = QVBoxLayout(self)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    layout.addWidget(self.menu_bar)
    layout.addWidget(main_area, 1)
    layout.addWidget(self.session_footer)
