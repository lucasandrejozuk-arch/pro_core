from __future__ import annotations


def normalize_language(language: str | None) -> str:
    return str(language or "pt-BR").strip() or "pt-BR"


def translate_ui_text(message: str, language: str | None = "pt-BR") -> str:
    normalized_language = normalize_language(language)
    text = str(message or "")
    if not text:
        return ""

    if normalized_language == "pt-BR":
        return _translate_pt_br(text)

    return text


def _translate_pt_br(text: str) -> str:
    translations = {
        "Document not found.": "Documento nao encontrado.",
        "Document file not found.": "Arquivo do documento nao encontrado.",
        "Inventory item not found.": "Item de estoque nao encontrado.",
        "Service order not found.": "Ordem de servico nao encontrada.",
        "Customer not found.": "Cliente nao encontrado.",
        "Equipment not found.": "Equipamento nao encontrado.",
        "At least one document target must be provided.": "Informe ao menos um destino para o anexo.",
        "Document file type is not allowed.": "Tipo de arquivo nao permitido.",
        "No such file or directory": "Arquivo ou pasta nao encontrado.",
        "Permission denied": "Permissao negada.",
    }
    if text in translations:
        return translations[text]
    return text
