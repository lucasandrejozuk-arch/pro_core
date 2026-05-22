from __future__ import annotations

from datetime import datetime

from frontend.app.core.api_client import ApiError


class ProCoreDataMixin:
    def _module_allowed(self, module_key: str) -> bool:
        role = str(self.session.user.get("role") or "")
        resource_access = {
            str(item) for item in (self.session.user.get("resource_access") or []) if str(item)
        }

        if resource_access:
            if module_key not in resource_access:
                return False

        if module_key == "customers":
            return role in {"admin", "manager"}
        if module_key == "admin_area":
            return role in {"admin", "manager"}
        if module_key in {"settings", "audit_logs"}:
            return role == "admin"
        if module_key in {"sectors", "users", "resource_access", "password_resets"}:
            return role in {"admin", "manager"}
        return True

    @staticmethod
    def _dependencies_from_service_orders(
        rows: list[dict],
    ) -> tuple[list[dict], list[dict], list[dict]]:
        customers: dict[str, dict] = {}
        equipment: dict[str, dict] = {}
        for row in rows:
            customer_id = str(row.get("customer_id") or "")
            if customer_id:
                customers[customer_id] = {
                    "id": customer_id,
                    "name": row.get("customer_name") or customer_id,
                    "email": row.get("customer_email") or "",
                }
            equipment_id = str(row.get("equipment_id") or "")
            if equipment_id:
                equipment[equipment_id] = {
                    "id": equipment_id,
                    "category": row.get("equipment_label") or equipment_id,
                    "brand": "",
                    "model": "",
                    "special_number": "",
                    "serial_number": "",
                }
        return list(customers.values()), list(equipment.values()), []

    def _load_module_rows(self, module_key: str, access_token: str) -> list[dict]:
        if module_key == "customers":
            return self.api_client.list_customers(access_token)
        if module_key == "equipment":
            return self.api_client.list_equipment(access_token)
        if module_key == "inventory":
            rows = self.api_client.list_inventory(access_token)
            try:
                documents = self.api_client.list_documents(access_token)
            except ApiError:
                documents = []
            documents_by_item_id: dict[str, list[dict]] = {}
            for document in documents:
                inventory_item_id = str(document.get("inventory_item_id") or "")
                if not inventory_item_id:
                    continue
                documents_by_item_id.setdefault(inventory_item_id, []).append(document)
            for row in rows:
                item_documents = documents_by_item_id.get(str(row.get("id")), [])
                row["documents"] = item_documents
                row["documents_count"] = len(item_documents)
            return rows
        if module_key == "users":
            return self.api_client.list_users(access_token)
        if module_key == "resource_access":
            rows = self.api_client.list_user_resource_access(access_token)
            for row in rows:
                resources = row.get("allowed_resources") if isinstance(row, dict) else []
                if isinstance(resources, list):
                    row["allowed_resources_text"] = ", ".join(str(item) for item in resources)
                else:
                    row["allowed_resources_text"] = ""
            return rows
        if module_key == "password_resets":
            return self.api_client.list_password_reset_requests(access_token)
        if module_key == "sectors":
            return self.api_client.list_sectors(access_token)
        if module_key == "audit_logs":
            return self.api_client.list_audit_logs(access_token)
        return self.api_client.list_service_orders(access_token)

    def _build_dashboard_summary(self, access_token: str) -> dict:
        alerts: list[dict[str, str]] = []

        def safe_list(label: str, loader) -> list[dict]:
            try:
                return loader()
            except ApiError as exc:
                alerts.append(
                    {
                        "message": f"Nao foi possivel carregar {label}: {exc.display_message}",
                        "level": "warning",
                    }
                )
                return []

        service_orders = safe_list(
            "ordens de serviço",
            lambda: self.api_client.list_service_orders(access_token),
        )
        role = str(self.session.user.get("role") or "")
        customers = (
            safe_list("clientes", lambda: self.api_client.list_customers(access_token))
            if role in {"admin", "manager"}
            else []
        )
        equipment = safe_list("equipamentos", lambda: self.api_client.list_equipment(access_token))
        inventory = safe_list("estoque", lambda: self.api_client.list_inventory(access_token))

        users: list[dict] = []
        password_requests: list[dict] = []
        if role in {"admin", "manager"}:
            users = safe_list("usuarios", lambda: self.api_client.list_users(access_token))
            password_requests = safe_list(
                "solicitacoes de senha",
                lambda: self.api_client.list_password_reset_requests(access_token),
            )

        open_statuses = {
            "open",
            "assigned",
            "pending_quote",
            "quote_sent",
            "pending_approval",
            "approved",
            "in_progress",
        }
        service_orders_open = [
            order for order in service_orders if str(order.get("status") or "") in open_statuses
        ]
        service_orders_pending = [
            order
            for order in service_orders
            if str(order.get("status") or "") == "pending_approval"
        ]
        inventory_low = [
            item
            for item in inventory
            if self._to_decimal(item.get("quantity"))
            <= self._to_decimal(item.get("minimum_quantity"))
            and self._to_decimal(item.get("minimum_quantity")) > 0
        ]
        active_customers = [customer for customer in customers if customer.get("is_active", True)]
        active_users = [user for user in users if user.get("is_active", True)]
        pending_password_requests = [
            request
            for request in password_requests
            if str(request.get("status") or "") == "pending"
        ]

        if service_orders_pending:
            alerts.append(
                {
                    "message": (
                        f"{len(service_orders_pending)} O.S. aguardando aprovação " "do cliente."
                    ),
                    "level": "warning",
                }
            )
        if inventory_low:
            alerts.append(
                {
                    "message": f"{len(inventory_low)} item(ns) com estoque critico.",
                    "level": "error",
                }
            )
        if pending_password_requests:
            alerts.append(
                {
                    "message": (
                        f"{len(pending_password_requests)} solicitacao(oes) de senha "
                        "pendente(s)."
                    ),
                    "level": "warning",
                }
            )

        pending_count = (
            len(service_orders_pending) + len(inventory_low) + len(pending_password_requests)
        )
        return {
            "greeting": self._dashboard_greeting(),
            "last_refresh": f"Atualizado: {datetime.now().strftime('%H:%M:%S')}",
            "cards": {
                "service_orders_open": len(service_orders_open),
                "service_orders_pending": len(service_orders_pending),
                "inventory_total": len(inventory),
                "inventory_low": len(inventory_low),
                "customers_total": len(active_customers),
                "equipment_total": len(equipment),
                "users_total": len(active_users),
                "system_health": pending_count,
            },
            "alerts": alerts,
        }

    def _dashboard_greeting(self) -> str:
        full_name = str(self.session.user.get("full_name") or "usuario")
        hour = datetime.now().hour
        greeting = "Bom dia" if hour < 12 else "Boa tarde" if hour < 18 else "Boa noite"
        return f"{greeting}, {full_name}. Acompanhe os indicadores operacionais do dia."

    @staticmethod
    def _to_decimal(value) -> float:
        try:
            return float(value or 0)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _module_columns(module_key: str) -> tuple[str, list[tuple[str, str]]]:
        if module_key == "customers":
            return (
                "Clientes",
                [
                    ("Nome", "name"),
                    ("Email", "email"),
                    ("Telefone", "phone"),
                    ("Ativo", "is_active"),
                ],
            )

        if module_key == "equipment":
            return (
                "Equipamentos",
                [
                    ("Categoria", "category"),
                    ("Marca", "brand"),
                    ("Modelo", "model"),
                    ("N especial", "special_number"),
                    ("Serie", "serial_number"),
                ],
            )

        if module_key == "inventory":
            return (
                "Estoque",
                [
                    ("Submodulo", "stock_group"),
                    ("Categoria", "category"),
                    ("SKU", "sku"),
                    ("Nome", "name"),
                    ("Localizacao", "location"),
                    ("Quantidade", "quantity"),
                    ("Minimo", "minimum_quantity"),
                    ("Anexos", "documents_count"),
                    ("Custo", "unit_cost"),
                ],
            )

        if module_key == "users":
            return (
                "Usuarios",
                [
                    ("Nome", "full_name"),
                    ("Email", "email"),
                    ("Perfil", "role"),
                    ("Setor", "sector_name"),
                    ("Ativo", "is_active"),
                    ("Troca senha", "must_change_password"),
                ],
            )

        if module_key == "resource_access":
            return (
                "Acessos de Recursos",
                [
                    ("Nome", "full_name"),
                    ("Email", "email"),
                    ("Perfil", "role"),
                    ("Setor", "sector_name"),
                    ("Recursos liberados", "allowed_resources_text"),
                ],
            )

        if module_key == "sectors":
            return (
                "Setores",
                [
                    ("Nome", "name"),
                    ("Descricao", "description"),
                    ("Criado em", "created_at"),
                ],
            )

        if module_key == "password_resets":
            return (
                "Solicitacoes de Senha",
                [
                    ("Solicitante", "requester_full_name"),
                    ("Email", "requester_email"),
                    ("Perfil", "requester_role"),
                    ("Status", "status"),
                    ("Criada em", "created_at"),
                ],
            )

        if module_key == "audit_logs":
            return (
                "Logs/Auditoria",
                [
                    ("Acao", "action"),
                    ("Entidade", "entity_type"),
                    ("Resumo", "summary"),
                    ("Criado em", "created_at"),
                ],
            )

        if module_key == "settings":
            return ("Configuracoes", [])
        if module_key == "admin_area":
            return ("Area Administrativa", [])
        if module_key == "tools":
            return ("Ferramentas", [])
        if module_key == "dashboard":
            return ("Dashboard", [])

        return (
            "Ordens de Serviço",
            [
                ("Código", "code"),
                ("Status", "status"),
                ("Prioridade", "priority"),
                ("Defeito Informado", "problem_description"),
                ("Total", "quoted_total"),
                ("SLA", "sla_due_at"),
                ("Criada em", "created_at"),
            ],
        )
