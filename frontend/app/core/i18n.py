from __future__ import annotations

import re

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QComboBox, QGroupBox, QTableWidget, QTabWidget, QWidget

from frontend.app.core.i18n_catalog import (
    PHRASE_EN_TO_PT,
    PHRASE_PT_TO_EN,
    SOURCE_COMBO_TEXTS_PROP,
    SOURCE_HEADER_TEXTS_PROP,
    SOURCE_PLACEHOLDER_PROP,
    SOURCE_TAB_TEXTS_PROP,
    SOURCE_TEXT_PROP,
    SOURCE_TITLE_PROP,
    SOURCE_TOOLTIP_PROP,
    SOURCE_WINDOW_TITLE_PROP,
    TOKEN_EN_TO_PT,
    TOKEN_PT_TO_EN,
)


def normalize_language(language: str | None) -> str:
    normalized = str(language or "pt-BR").strip() or "pt-BR"
    if normalized not in {"pt-BR", "en-US"}:
        return "pt-BR"
    return normalized


def current_ui_language() -> str:
    return normalize_language(
        str(QSettings("PRO CORE", "PRO CORE").value("appearance/language", "pt-BR") or "pt-BR")
    )


def translate_ui_text(message: str, language: str | None = "pt-BR") -> str:
    normalized_language = normalize_language(language)
    text = str(message or "")
    if not text:
        return ""
    if normalized_language == "pt-BR":
        return _translate_to_pt_br(text)
    return _translate_to_en_us(text)


def apply_language_to_widgets(language: str | None, *roots: QWidget | None) -> None:
    normalized_language = normalize_language(language)
    for root in roots:
        if root is None:
            continue
        _apply_language_to_widget(root, normalized_language)
        for child in root.findChildren(QWidget):
            _apply_language_to_widget(child, normalized_language)


def _apply_language_to_widget(widget: QWidget, language: str) -> None:
    _translate_text_property(widget, language)
    _translate_placeholder_property(widget, language)
    _translate_tooltip_property(widget, language)
    _translate_window_title_property(widget, language)
    _translate_title_property(widget, language)
    _translate_tab_widget(widget, language)
    _translate_combo_widget(widget, language)
    _translate_table_headers(widget, language)


def _translate_text_property(widget: QWidget, language: str) -> None:
    text_getter = getattr(widget, "text", None)
    text_setter = getattr(widget, "setText", None)
    if not callable(text_getter) or not callable(text_setter):
        return
    source = widget.property(SOURCE_TEXT_PROP)
    if source is None:
        source = str(text_getter() or "")
        widget.setProperty(SOURCE_TEXT_PROP, source)
    text_setter(translate_ui_text(str(source), language))


def _translate_placeholder_property(widget: QWidget, language: str) -> None:
    placeholder_getter = getattr(widget, "placeholderText", None)
    placeholder_setter = getattr(widget, "setPlaceholderText", None)
    if not callable(placeholder_getter) or not callable(placeholder_setter):
        return
    source = widget.property(SOURCE_PLACEHOLDER_PROP)
    if source is None:
        source = str(placeholder_getter() or "")
        widget.setProperty(SOURCE_PLACEHOLDER_PROP, source)
    placeholder_setter(translate_ui_text(str(source), language))


def _translate_tooltip_property(widget: QWidget, language: str) -> None:
    source = widget.property(SOURCE_TOOLTIP_PROP)
    if source is None:
        source = str(widget.toolTip() or "")
        widget.setProperty(SOURCE_TOOLTIP_PROP, source)
    widget.setToolTip(translate_ui_text(str(source), language))


def _translate_window_title_property(widget: QWidget, language: str) -> None:
    title_getter = getattr(widget, "windowTitle", None)
    title_setter = getattr(widget, "setWindowTitle", None)
    if not callable(title_getter) or not callable(title_setter):
        return
    source = widget.property(SOURCE_WINDOW_TITLE_PROP)
    if source is None:
        source = str(title_getter() or "")
        widget.setProperty(SOURCE_WINDOW_TITLE_PROP, source)
    title_setter(translate_ui_text(str(source), language))


def _translate_title_property(widget: QWidget, language: str) -> None:
    if not isinstance(widget, QGroupBox):
        return
    source = widget.property(SOURCE_TITLE_PROP)
    if source is None:
        source = str(widget.title() or "")
        widget.setProperty(SOURCE_TITLE_PROP, source)
    widget.setTitle(translate_ui_text(str(source), language))


def _translate_tab_widget(widget: QWidget, language: str) -> None:
    if not isinstance(widget, QTabWidget):
        return
    source_tabs = widget.property(SOURCE_TAB_TEXTS_PROP)
    if not isinstance(source_tabs, list) or len(source_tabs) != widget.count():
        source_tabs = [widget.tabText(index) for index in range(widget.count())]
        widget.setProperty(SOURCE_TAB_TEXTS_PROP, source_tabs)
    for index, source_text in enumerate(source_tabs):
        widget.setTabText(index, translate_ui_text(str(source_text), language))


def _translate_combo_widget(widget: QWidget, language: str) -> None:
    if not isinstance(widget, QComboBox):
        return
    source_items = widget.property(SOURCE_COMBO_TEXTS_PROP)
    if not isinstance(source_items, list) or len(source_items) != widget.count():
        source_items = [widget.itemText(index) for index in range(widget.count())]
        widget.setProperty(SOURCE_COMBO_TEXTS_PROP, source_items)
    for index, source_text in enumerate(source_items):
        widget.setItemText(index, translate_ui_text(str(source_text), language))


def _translate_table_headers(widget: QWidget, language: str) -> None:
    if not isinstance(widget, QTableWidget):
        return
    source_headers = widget.property(SOURCE_HEADER_TEXTS_PROP)
    if not isinstance(source_headers, list) or len(source_headers) != widget.columnCount():
        source_headers = []
        for column in range(widget.columnCount()):
            item = widget.horizontalHeaderItem(column)
            source_headers.append(item.text() if item else "")
        widget.setProperty(SOURCE_HEADER_TEXTS_PROP, source_headers)
    for column, source_text in enumerate(source_headers):
        item = widget.horizontalHeaderItem(column)
        if item is None:
            continue
        item.setText(translate_ui_text(str(source_text), language))


def _translate_to_pt_br(text: str) -> str:
    direct = PHRASE_EN_TO_PT.get(text)
    if direct:
        return direct
    return _apply_token_translation(text, TOKEN_EN_TO_PT)


def _translate_to_en_us(text: str) -> str:
    direct = PHRASE_PT_TO_EN.get(text)
    if direct:
        return direct
    return _apply_token_translation(text, TOKEN_PT_TO_EN)


def _apply_token_translation(text: str, token_map: dict[str, str]) -> str:
    if not text.strip():
        return text
    translated = text
    # Preserve separators and translate token by token.
    tokens = re.split(r"(\W+)", translated, flags=re.UNICODE)
    output: list[str] = []
    for token in tokens:
        if not token or re.fullmatch(r"\W+", token, flags=re.UNICODE):
            output.append(token)
            continue
        mapped = token_map.get(token.lower())
        if not mapped:
            output.append(token)
            continue
        output.append(_apply_case(mapped, token))
    return "".join(output)


def _apply_case(target: str, source: str) -> str:
    if source.isupper():
        return target.upper()
    if source.istitle():
        return target.title()
    return target
