from __future__ import annotations

STOCK_GROUP_OPTIONS: tuple[tuple[str, str], ...] = (
    ("components", "Componentes"),
    ("tools", "Ferramentas"),
    ("software", "Softwares"),
)

CATEGORY_OPTIONS_BY_GROUP: dict[str, tuple[str, ...]] = {
    "components": (
        "Resistores",
        "Capacitores",
        "Indutores",
        "Conectores",
        "Cabos",
        "Fios",
        "Placas",
        "Placas de Prototipagem",
        "Transformadores",
        "Diodos",
    ),
    "tools": (
        "Multimetros",
        "Estacoes de Solda",
        "Fontes de Bancada",
        "Osciloscopios",
        "Alicates",
        "Chaves",
        "Crimpadores",
        "Impressoras de Etiqueta",
        "Microscopios",
        "Outros",
    ),
    "software": (
        "Licencas CAD",
        "Firmware",
        "Sistemas Embarcados",
        "Diagnostico",
        "Automacao",
        "ERP",
        "Monitoramento",
        "Backup",
        "Seguranca",
        "Outros",
    ),
}

DEFAULT_TECHNICAL_FIELDS: tuple[tuple[str, str], ...] = (
    ("manufacturer", "Fabricante"),
    ("model", "Modelo / Part Number"),
    ("package", "Encapsulamento"),
    ("main_spec", "Especificacao principal"),
    ("secondary_spec", "Especificacao secundaria"),
    ("tolerance", "Tolerancia"),
    ("voltage", "Tensao nominal"),
    ("current", "Corrente nominal"),
    ("power", "Potencia / Dissipacao"),
    ("temperature", "Faixa de temperatura"),
)

TECHNICAL_FIELDS_BY_CATEGORY: dict[str, tuple[tuple[str, str], ...]] = {
    "Transformadores": (
        ("manufacturer", "Fabricante"),
        ("model", "Modelo / Part Number"),
        ("core_type", "Tipo de nucleo"),
        ("primary_voltage", "Tensao primaria"),
        ("secondary_voltage", "Tensao secundaria"),
        ("current", "Corrente nominal"),
        ("power", "Potencia (VA)"),
        ("frequency", "Frequencia"),
        ("isolation", "Classe de isolamento"),
        ("mounting", "Montagem"),
    ),
    "Resistores": (
        ("manufacturer", "Fabricante"),
        ("model", "Modelo / Part Number"),
        ("resistance", "Resistencia"),
        ("tolerance", "Tolerancia"),
        ("power", "Potencia"),
        ("technology", "Tecnologia"),
        ("package", "Encapsulamento"),
        ("temperature", "Coeficiente termico"),
        ("voltage", "Tensao maxima"),
        ("mounting", "Montagem"),
    ),
    "Capacitores": (
        ("manufacturer", "Fabricante"),
        ("model", "Modelo / Part Number"),
        ("capacitance", "Capacitancia"),
        ("voltage", "Tensao nominal"),
        ("tolerance", "Tolerancia"),
        ("dielectric", "Dieletrico"),
        ("esr", "ESR"),
        ("package", "Encapsulamento"),
        ("temperature", "Faixa de temperatura"),
        ("lifetime", "Vida util"),
    ),
    "Diodos": (
        ("manufacturer", "Fabricante"),
        ("model", "Modelo / Part Number"),
        ("diode_type", "Tipo de diodo"),
        ("voltage", "Tensao reversa"),
        ("current", "Corrente direta"),
        ("vf", "Queda de tensao (Vf)"),
        ("recovery", "Tempo de recuperacao"),
        ("package", "Encapsulamento"),
        ("temperature", "Faixa de temperatura"),
        ("mounting", "Montagem"),
    ),
}

REQUIRED_FIELDS_BY_CATEGORY: dict[str, tuple[str, ...]] = {
    "Transformadores": (
        "primary_voltage",
        "secondary_voltage",
        "power",
    ),
}


def categories_for_group(stock_group: str) -> tuple[str, ...]:
    return CATEGORY_OPTIONS_BY_GROUP.get(stock_group, CATEGORY_OPTIONS_BY_GROUP["components"])


def technical_fields_for_category(category: str) -> tuple[tuple[str, str], ...]:
    return TECHNICAL_FIELDS_BY_CATEGORY.get(category, DEFAULT_TECHNICAL_FIELDS)


def technical_field_labels_for_category(category: str) -> dict[str, str]:
    return {key: label for key, label in technical_fields_for_category(category)}


def required_field_keys_for_category(category: str) -> tuple[str, ...]:
    return REQUIRED_FIELDS_BY_CATEGORY.get(category, ())
