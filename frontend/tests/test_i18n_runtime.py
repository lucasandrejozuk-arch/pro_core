from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QWidget,
)

from frontend.app.core.i18n import apply_language_to_widgets, translate_ui_text


def test_translate_ui_text_supports_bidirectional_common_phrases() -> None:
    assert translate_ui_text("Entrar", "en-US") == "Sign In"
    assert translate_ui_text("Sign In", "pt-BR") == "Entrar"


def test_apply_language_to_widgets_translates_visible_texts(qtbot) -> None:
    root = QWidget()
    qtbot.addWidget(root)

    label = QLabel("Alterar senha", root)
    button = QPushButton("Salvar configuracoes", root)
    input_field = QLineEdit(root)
    input_field.setPlaceholderText("Senha atual")
    combo = QComboBox(root)
    combo.addItem("Portugues brasileiro", "pt-BR")
    combo.addItem("English (United States)", "en-US")
    tabs = QTabWidget(root)
    tabs.addTab(QWidget(), "Empresa")
    tabs.addTab(QWidget(), "Backup")

    apply_language_to_widgets("en-US", root)

    assert label.text() == "Change password"
    assert button.text() == "Save settings"
    assert input_field.placeholderText() == "Current password"
    assert combo.itemText(0) == "Brazilian Portuguese"
    assert tabs.tabText(0) == "Company"
    assert tabs.tabText(1) == "Backup"

    apply_language_to_widgets("pt-BR", root)

    assert label.text() == "Alterar senha"
    assert button.text() == "Salvar configuracoes"
    assert input_field.placeholderText() == "Senha atual"
    assert combo.itemText(0) == "Portugues brasileiro"
    assert tabs.tabText(0) == "Empresa"
