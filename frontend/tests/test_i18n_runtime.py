from __future__ import annotations

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import (
    QComboBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QWidget,
)

from frontend.app.core.i18n import apply_language_to_widgets, translate_ui_text
from frontend.app.screens.dashboard_dialogs_assets import EquipmentAssetDialog
from frontend.app.screens.dashboard_dialogs_defect_cases import DefectCaseEditDialog


def test_translate_ui_text_supports_bidirectional_common_phrases() -> None:
    assert translate_ui_text("Entrar", "en-US") == "Sign In"
    assert translate_ui_text("Sign In", "pt-BR") == "Entrar"
    assert translate_ui_text("Aparencia", "en-US") == "Appearance"
    assert translate_ui_text("Painel Principal", "en-US") == "Main Panel"
    assert translate_ui_text("Selecione um modulo para carregar dados.", "en-US") == (
        "Select a module to load data."
    )


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


def test_asset_dialog_uses_saved_language(qtbot) -> None:
    settings = QSettings("PRO CORE", "PRO CORE")
    settings.setValue("appearance/language", "en-US")
    dialog = EquipmentAssetDialog(
        "Dados completos",
        [{"key": "name", "label": "Titulo:", "required": True}],
    )
    qtbot.addWidget(dialog)

    assert dialog.windowTitle() == "Full details"
    button_texts = {button.text() for button in dialog.findChildren(QPushButton)}
    assert {"Save", "Cancel"}.issubset(button_texts)


def test_defect_case_dialog_uses_saved_language(qtbot) -> None:
    settings = QSettings("PRO CORE", "PRO CORE")
    settings.setValue("appearance/language", "en-US")
    dialog = DefectCaseEditDialog({"boards": []})
    qtbot.addWidget(dialog)

    assert dialog.windowTitle() == "NEW DEFECT CASE"
    button_texts = {button.text() for button in dialog.findChildren(QPushButton)}
    assert {"Save", "Cancel"}.issubset(button_texts)
