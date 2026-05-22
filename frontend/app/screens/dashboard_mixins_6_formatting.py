from __future__ import annotations

from typing import Any

from frontend.app.core.id_system import professional_record_id


def confirm_destructive_action(*args: Any, **kwargs: Any) -> bool:
    from frontend.app.screens import dashboard

    return bool(dashboard.confirm_destructive_action(*args, **kwargs))


class DashboardFormattingMixin:
    def _format_professional_id(self, module_key: str, record: dict[str, Any]) -> str:
        display_id = self._format_value(record.get("display_id"))
        if display_id:
            return display_id
        return professional_record_id(module_key, record)

    @staticmethod
    def _format_value(value: Any) -> str:
        if value is None:
            return ""

        if isinstance(value, bool):
            return "Sim" if value else "Nao"

        labels = {
            "open": "Aberta",
            "assigned": "Atribuida",
            "pending_tech": "Aguardando tecnico",
            "diagnosis": "Em diagnostico tecnico",
            "pending_quote": "Pendente de orçamento",
            "quote_sent": "Orçamento enviado",
            "pending_approval": "Pendente de aprovação",
            "approved": "Aprovada",
            "in_progress": "Em execução",
            "ready_dispatch": "Pronto para expedicao",
            "completed": "Concluída",
            "rejected": "Reprovada",
            "closed": "Encerrada",
            "admin": "Administrador",
            "manager": "Gestor/Lider",
            "technician": "Técnico",
            "customer": "Cliente",
            "pending": "Pendente",
            "resolved": "Resolvida",
            "service": "Serviço",
            "part": "Peça",
            "other": "Outro",
            "light": "Claro",
            "dark": "Escuro",
            "low": "Baixa",
            "normal": "Normal",
            "high": "Alta",
            "urgent": "Urgente",
            "receivable": "A receber",
            "payable": "A pagar",
            "paid": "Pago",
            "canceled": "Cancelado",
            "overdue": "Vencido",
            "email": "Email",
            "whatsapp": "WhatsApp",
            "system": "Sistema",
            "sent": "Enviada",
            "failed": "Falhou",
            "service_orders": "Ordens de Serviço",
            "customers": "Clientes",
            "equipment": "Equipamentos",
            "inventory": "Estoque",
            "users": "Usuários",
            "audit_logs": "Logs/Auditoria",
            "components": "Componentes",
            "tools": "Ferramentas",
            "software": "Softwares",
        }
        if isinstance(value, str) and value in labels:
            return labels[value]

        return str(value)

    def _format_service_order_budget(self, service_order: dict[str, Any]) -> str:
        items = service_order.get("budget_items") or []
        total = self._format_value(service_order.get("quoted_total"))
        if not items:
            return f"Orçamento: nenhum item. Total: {total or '0'}"

        descriptions = []
        for item in items[:4]:
            item_type = self._format_value(item.get("item_type"))
            quantity = self._format_value(item.get("quantity"))
            unit_price = self._format_value(item.get("unit_price"))
            description = self._format_value(item.get("description"))
            descriptions.append(f"{item_type}: {description} ({quantity} x {unit_price})")

        remaining = len(items) - len(descriptions)
        suffix = f" + {remaining} item(ns)" if remaining > 0 else ""
        return f"Orçamento: {'; '.join(descriptions)}{suffix}. Total: {total}"

    def _format_service_order_documents(self, service_order: dict[str, Any]) -> str:
        documents = service_order.get("documents") or []
        if not documents:
            return "Anexos: nenhum arquivo."

        descriptions = []
        for document in documents[:4]:
            document_type = self._format_value(document.get("document_type"))
            file_name = self._format_value(document.get("file_name"))
            descriptions.append(f"{document_type}: {file_name}")

        remaining = len(documents) - len(descriptions)
        suffix = f" + {remaining} arquivo(s)" if remaining > 0 else ""
        return f"Anexos: {'; '.join(descriptions)}{suffix}."

    def _format_selected_record_summary(self, record: dict[str, Any]) -> str:
        formatters = {
            "customers": self._format_customer_full_summary,
            "equipment": self._format_equipment_full_summary,
            "inventory": self._format_inventory_full_summary,
            "service_orders": self._format_service_order_full_summary,
            "sectors": self._format_sector_summary,
            "users": self._format_user_summary,
            "resource_access": self._format_resource_access_summary,
            "password_resets": self._format_password_reset_summary,
            "audit_logs": self._format_audit_summary,
        }
        formatter = formatters.get(self.active_module_key)
        if formatter is not None:
            return formatter(record)
        lines = []
        for key, value in record.items():
            lines.append(f"{key}: {self._format_value(value) or '-'}")
        return "\n".join(lines) or "Nenhum item selecionado."

    def _format_service_order_full_summary(self, service_order: dict[str, Any]) -> str:
        customer_name = self._lookup_label(
            self.service_order_customers,
            service_order.get("customer_id"),
            "name",
            "Cliente nao identificado",
        )
        technician_name = self._lookup_label(
            self.service_order_technicians,
            service_order.get("assigned_technician_id"),
            "full_name",
            "Sem técnico",
        )
        equipment_label = self._lookup_equipment_label(service_order.get("equipment_id"))
        customer_approval = self._format_value(service_order.get("customer_approval"))
        budget_sent_at = self._format_value(service_order.get("budget_sent_at"))
        problem_description = self._format_value(service_order.get("problem_description"))
        technical_diagnosis = self._format_value(service_order.get("technical_diagnosis"))
        proposed_solution = self._format_value(service_order.get("proposed_solution"))
        proposed_actions = self._format_value(service_order.get("proposed_actions"))
        intake_checklist = self._format_value(service_order.get("intake_checklist"))
        workflow_history = self._format_value(service_order.get("workflow_history"))
        documents = self._format_service_order_documents(service_order).replace("Anexos: ", "")
        rejection_reason = self._format_value(service_order.get("rejection_reason"))
        lines = [
            f"Código: {self._format_value(service_order.get('code')) or '-'}",
            f"ID Profissional: {self._format_professional_id('service_orders', service_order)}",
            f"ID Personalizado: {self._format_value(service_order.get('custom_id')) or '-'}",
            f"Empresa: {customer_name}",
            f"Técnico Responsável: {technician_name}",
            f"Equipamento: {equipment_label}",
            f"Status: {self._format_value(service_order.get('status'))}",
            f"Prioridade: {self._format_value(service_order.get('priority')) or 'Normal'}",
            f"Tipo de Serviço: {self._format_value(service_order.get('service_type')) or '-'}",
            f"Nº Especial: {self._format_value(service_order.get('special_number')) or '-'}",
            f"Número de Série: {self._format_value(service_order.get('serial_number')) or '-'}",
            f"Aprovação do Cliente: {customer_approval or 'Pendente'}",
            f"Data de Entrada: {self._format_value(service_order.get('entry_date')) or '-'}",
            f"Entrega Prevista: {self._format_value(service_order.get('sla_due_at')) or '-'}",
            f"Data de Envio do Orçamento: {budget_sent_at or '-'}",
            "",
            f"Defeito Informado: {problem_description or '-'}",
            f"Defeito Encontrado: {technical_diagnosis or '-'}",
            f"Inspeção Visual: {self._format_value(service_order.get('inspection_visual')) or '-'}",
            f"Solução Proposta: {proposed_solution or '-'}",
            f"Execuções Necessárias: {proposed_actions or '-'}",
            "",
            f"Checklist de Entrada: {intake_checklist or '-'}",
            f"Objetos Vinculados: {self._format_value(service_order.get('linked_objects')) or '-'}",
            f"Componentes Utilizados: {self._format_value(service_order.get('parts_used')) or '-'}",
            f"Histórico de Workflow: {workflow_history or '-'}",
            f"Anexos / Evidências: {documents}",
            f"Notas: {self._format_value(service_order.get('notes')) or '-'}",
            f"Observação de Reprovação: {rejection_reason or '-'}",
            "",
            f"Total Orçado: {self._format_value(service_order.get('quoted_total')) or '0'}",
            f"Criada em: {self._format_value(service_order.get('created_at'))}",
        ]
        return "\n".join(lines)

    def _format_customer_full_summary(self, customer: dict[str, Any]) -> str:
        active = "Sim" if customer.get("is_active", True) else "Nao"
        lines = [
            f"ID Profissional: {self._format_professional_id('customers', customer)}",
            f"Nome: {self._format_value(customer.get('name')) or '-'}",
            f"Email: {self._format_value(customer.get('email')) or '-'}",
            f"Telefone: {self._format_value(customer.get('phone')) or '-'}",
            f"Endereco: {self._format_value(customer.get('address')) or '-'}",
            f"Ativo: {active}",
            f"Observacoes: {self._format_value(customer.get('notes')) or '-'}",
        ]
        return "\n".join(lines)

    def _format_equipment_full_summary(self, equipment: dict[str, Any]) -> str:
        boards = equipment.get("boards") or []
        components_count = sum(len(board.get("components") or []) for board in boards)
        lines = [
            f"ID Profissional: {self._format_professional_id('equipment', equipment)}",
            f"Tipo: {self._format_value(equipment.get('category')) or '-'}",
            f"Marca: {self._format_value(equipment.get('brand')) or '-'}",
            f"Modelo: {self._format_value(equipment.get('model')) or '-'}",
            f"N especial: {self._format_value(equipment.get('special_number')) or '-'}",
            f"Serie: {self._format_value(equipment.get('serial_number')) or '-'}",
            f"Valor unitario: R$ {self._format_value(equipment.get('unit_price')) or '0'}",
            f"Placas vinculadas: {len(boards)}",
            f"Componentes cadastrados: {components_count}",
            f"Notas: {self._format_value(equipment.get('description')) or '-'}",
        ]
        return "\n".join(lines)

    def _format_equipment_board_summary(self, board: dict[str, Any]) -> str:
        components = board.get("components") or []
        lines = [
            f"ID Profissional: {self._format_professional_id('equipment', board)}",
            f"Nome: {self._format_value(board.get('name')) or '-'}",
            f"N especial: {self._format_value(board.get('special_number')) or '-'}",
            f"Serie: {self._format_value(board.get('serial_number')) or '-'}",
            f"Modelo / Tipo: {self._format_value(board.get('model')) or '-'}",
            f"Revisao: {self._format_value(board.get('revision')) or '-'}",
            f"Valor unitario: R$ {self._format_value(board.get('unit_price')) or '0'}",
            f"Componentes vinculados: {len(components)}",
            f"Notas: {self._format_value(board.get('notes')) or '-'}",
        ]
        return "\n".join(lines)

    def _format_equipment_component_summary(self, component: dict[str, Any]) -> str:
        lines = [
            f"ID Profissional: {self._format_professional_id('equipment', component)}",
            f"Dados: {self._format_value(component.get('name')) or '-'}",
            f"Categoria: {self._format_value(component.get('category')) or '-'}",
            f"Modelo / Part Number: {self._format_value(component.get('part_number')) or '-'}",
            f"Localizacao: {self._format_value(component.get('location')) or '-'}",
            f"Quantidade: {self._format_value(component.get('quantity')) or '-'}",
            f"Valor unitario: R$ {self._format_value(component.get('unit_price')) or '0'}",
            f"Observacoes: {self._format_value(component.get('notes')) or '-'}",
        ]
        return "\n".join(lines)
