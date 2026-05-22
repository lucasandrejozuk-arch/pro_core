    const apiBase = "/api/v1/customer-portal";
    const statusMap = {
      open: "Aberta",
      assigned: "Atribuida",
      pending_tech: "Aguardando tecnico",
      diagnosis: "Em diagnostico",
      pending_quote: "Pendente de orcamento",
      quote_sent: "Orcamento enviado",
      pending_approval: "Pendente de aprovacao",
      approved: "Aprovada",
      in_progress: "Em execucao",
      ready_dispatch: "Pronto para expedicao",
      completed: "Concluida",
      rejected: "Reprovada",
      closed: "Encerrada",
    };
    const priorityMap = {
      low: "Baixa",
      normal: "Normal",
      high: "Alta",
      urgent: "Urgente",
    };
    const state = {
      token: "",
      order: null,
      appearance: { primary: customerPortalDefaultPrimary, theme: "light" },
    };
    const byId = id => document.getElementById(id);
    const formatMoney = value => new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(Number(value || 0));
    const formatDateTime = value => {
      if (!value) return "-";
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) return "-";
      return new Intl.DateTimeFormat("pt-BR", { dateStyle: "short", timeStyle: "short" }).format(date);
    };
    const safeText = value => {
      const span = document.createElement("span");
      span.textContent = String(value ?? "");
      return span.innerHTML;
    };
    const defaultHeaders = () => ({ "Authorization": `Bearer ${state.token}`, "Content-Type": "application/json" });
    function showMessage(elementId, kind, message) {
      const element = byId(elementId);
      if (!element) return;
      element.className = `message ${kind} show`;
      element.textContent = message;
    }
    function hideMessage(elementId) {
      const element = byId(elementId);
      if (!element) return;
      element.className = "message";
      element.textContent = "";
    }
    function setPending(buttonId, pending, pendingText) {
      const button = byId(buttonId);
      if (!button) return;
      if (!button.dataset.idleText) button.dataset.idleText = button.textContent;
      button.disabled = pending;
      button.textContent = pending ? pendingText : button.dataset.idleText;
    }
    function localizeStatus(status) {
      return statusMap[String(status || "")] || String(status || "-");
    }
    function localizePriority(priority) {
      return priorityMap[String(priority || "")] || String(priority || "-");
    }
    function applyStatusPill(status) {
      const pill = byId("order-status-pill");
      const normalized = String(status || "");
      pill.className = "label-pill";
      if (normalized === "pending_approval") pill.classList.add("status-awaiting");
      if (normalized === "approved") pill.classList.add("status-approved");
      if (["rejected", "closed"].includes(normalized)) pill.classList.add("status-rejected");
      pill.textContent = `Status: ${localizeStatus(normalized)}`;
    }
    function professionalOrderId(order) {
      const code = String(order?.code || "").replace(/[^A-Za-z0-9]/g, "").toUpperCase();
      const compact = code.slice(0, 10) || String(order?.id || "").replace(/[^A-Za-z0-9]/g, "").toUpperCase().slice(0, 10);
      return compact ? `OS-${compact}` : "OS-SEMID";
    }
    function renderBudgetItems(items) {
      const body = byId("budget-items");
      if (!Array.isArray(items) || items.length === 0) {
        body.innerHTML = "<tr><td colspan='4'>Nenhum item de orcamento registrado.</td></tr>";
        return;
      }
      body.innerHTML = items.map(item => {
        const totalLine = Number(item.quantity || 0) * Number(item.unit_price || 0);
        const desc = safeText(item.description || "-");
        return `<tr><td>${safeText(localizeStatus(item.item_type).replace("Pendente de ", ""))}</td><td>${desc}</td><td>${safeText(item.quantity || "0")}</td><td>${formatMoney(totalLine)}</td></tr>`;
      }).join("");
    }
    function renderEvents(events) {
      const host = byId("timeline-events");
      if (!Array.isArray(events) || events.length === 0) {
        host.innerHTML = "<div class='timeline-item'><strong>Sem eventos</strong><span>Aguarde as proximas atualizacoes da assistencia.</span></div>";
        return;
      }
      host.innerHTML = events.map(event => `
        <article class="timeline-item">
          <strong>${safeText(event.event_type || "Evento")}</strong>
          <div>${safeText(event.message || "-")}</div>
          <time>${safeText(formatDateTime(event.created_at))}</time>
        </article>
      `).join("");
    }
    function renderOrder(order) {
      state.order = order;
      byId("login-panel").classList.add("hidden");
      byId("order-panel").classList.remove("hidden");
      byId("order-title").textContent = `Ordem ${order.code || "-"}`;
      byId("order-id").textContent = professionalOrderId(order);
      byId("customer-name").textContent = order.customer_name || "-";
      byId("equipment-name").textContent = order.equipment || "-";
      byId("quoted-total").textContent = formatMoney(order.quoted_total);
      byId("priority-label").textContent = localizePriority(order.priority);
      byId("sla-due").textContent = formatDateTime(order.sla_due_at);
      byId("quote-sent-at").textContent = formatDateTime(order.quote_sent_at);
      byId("decision-at").textContent = formatDateTime(order.approved_at || order.closed_at);
      byId("diagnosis").textContent = order.technical_diagnosis || order.problem_description || "Sem diagnostico detalhado.";
      applyStatusPill(order.status);
      renderBudgetItems(order.budget_items);
      renderEvents(order.events);
      const canDecide = String(order.status) === "pending_approval";
      byId("approve-button").disabled = !canDecide;
      byId("show-reject-button").disabled = !canDecide;
      if (!canDecide) {
        showMessage("action-feedback", "info", "Esta ordem nao esta em etapa de aprovacao do cliente.");
      } else {
        hideMessage("action-feedback");
      }
    }
    async function requestJson(path, options = {}) {
      const response = await fetch(`${apiBase}${path}`, options);
      let data = null;
      try {
        data = await response.json();
      } catch {
        data = null;
      }
      return { response, data };
    }
    async function loadAppearance() {
      if (!state.token) return;
      try {
        const { response, data } = await requestJson("/appearance", { headers: { "Authorization": `Bearer ${state.token}` } });
        if (!response.ok || !data) return;
        if (data.brand_name) byId("brand").textContent = data.brand_name;
        if (data.brand_subtitle) byId("subtitle").textContent = data.brand_subtitle;
        state.appearance.primary = customerPortalIsHexColor(data.primary_color) ? data.primary_color : customerPortalDefaultPrimary;
        state.appearance.theme = String(data.theme || "light") === "dark" ? "dark" : "light";
        applyCustomerPortalTheme(state.appearance.theme, state.appearance.primary);
      } catch {
      }
    }
    async function login() {
      hideMessage("login-error");
      setPending("login-button", true, "Entrando...");
      try {
        const { response, data } = await requestJson("/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            service_order_code: byId("code").value,
            email: byId("email").value,
          }),
        });
        if (!response.ok || !data?.access_token || !data?.service_order) {
          showMessage("login-error", "error", "Nao foi possivel localizar a ordem com os dados informados.");
          return;
        }
        state.token = data.access_token;
        renderOrder(data.service_order);
        await loadAppearance();
      } catch {
        showMessage("login-error", "error", "Falha de conexao com o servidor. Tente novamente.");
      } finally {
        setPending("login-button", false, "Entrar no portal");
      }
    }
    async function refreshOrder() {
      if (!state.token) return;
      setPending("refresh-button", true, "Atualizando...");
      try {
        const { response, data } = await requestJson("/service-order", { headers: defaultHeaders() });
        if (!response.ok || !data) {
          showMessage("action-feedback", "error", "Nao foi possivel atualizar a ordem neste momento.");
          return;
        }
        renderOrder(data);
        showMessage("action-feedback", "ok", "Dados da ordem atualizados com sucesso.");
      } catch {
        showMessage("action-feedback", "error", "Falha ao sincronizar com o servidor.");
      } finally {
        setPending("refresh-button", false, "Atualizar situacao");
      }
    }
    async function approveOrder() {
      if (!state.token) return;
      setPending("approve-button", true, "Registrando...");
      try {
        const { response, data } = await requestJson("/approve", {
          method: "POST",
          headers: defaultHeaders(),
          body: JSON.stringify({ decision_name: byId("decision-name").value || null }),
        });
        if (!response.ok || !data) {
          showMessage("action-feedback", "error", "Nao foi possivel registrar a aprovacao.");
          return;
        }
        renderOrder(data);
        showMessage("action-feedback", "ok", "Orcamento aprovado com sucesso.");
      } catch {
        showMessage("action-feedback", "error", "Falha ao registrar aprovacao.");
      } finally {
        setPending("approve-button", false, "Aprovar orcamento");
      }
    }
    async function rejectOrder() {
      hideMessage("reject-error");
      const rejectionReason = byId("rejection-reason").value.trim();
      if (!rejectionReason) {
        showMessage("reject-error", "error", "Informe o motivo da reprovacao.");
        return;
      }
      setPending("confirm-reject-button", true, "Registrando...");
      try {
        const { response, data } = await requestJson("/reject", {
          method: "POST",
          headers: defaultHeaders(),
          body: JSON.stringify({
            decision_name: byId("decision-name").value || null,
            rejection_reason: rejectionReason,
          }),
        });
        if (!response.ok || !data) {
          showMessage("reject-error", "error", "Nao foi possivel registrar a reprovacao.");
          return;
        }
        byId("reject-panel").classList.add("hidden");
        renderOrder(data);
        showMessage("action-feedback", "ok", "Reprovacao registrada com sucesso.");
      } catch {
        showMessage("reject-error", "error", "Falha ao enviar reprovacao.");
      } finally {
        setPending("confirm-reject-button", false, "Confirmar reprovacao");
      }
    }
    async function downloadPdf(event) {
      event.preventDefault();
      if (!state.token) return;
      try {
        const response = await fetch(`${apiBase}/quote.pdf`, {
          headers: { "Authorization": `Bearer ${state.token}` },
        });
        if (!response.ok) {
          showMessage("action-feedback", "error", "Nao foi possivel baixar o PDF do orcamento.");
          return;
        }
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `${state.order?.code || "orcamento"}.pdf`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(url);
      } catch {
        showMessage("action-feedback", "error", "Falha ao gerar o arquivo PDF.");
      }
    }
    function attachListeners() {
      byId("login-button").addEventListener("click", login);
      byId("refresh-button").addEventListener("click", refreshOrder);
      byId("approve-button").addEventListener("click", approveOrder);
      byId("show-reject-button").addEventListener("click", () => {
        byId("reject-panel").classList.remove("hidden");
        hideMessage("reject-error");
      });
      byId("cancel-reject-button").addEventListener("click", () => {
        byId("reject-panel").classList.add("hidden");
        hideMessage("reject-error");
      });
      byId("confirm-reject-button").addEventListener("click", rejectOrder);
      byId("pdf-link").addEventListener("click", downloadPdf);
      byId("theme-toggle").addEventListener("click", () => {
        state.appearance.theme = state.appearance.theme === "dark" ? "light" : "dark";
        applyCustomerPortalTheme(state.appearance.theme, state.appearance.primary);
      });
      byId("email").addEventListener("keydown", event => {
        if (event.key === "Enter") login();
      });
      byId("code").addEventListener("keydown", event => {
        if (event.key === "Enter") login();
      });
    }
    function bootstrapSkeleton() {
      byId("order-id").innerHTML = "<span class='skeleton'></span>";
      byId("customer-name").innerHTML = "<span class='skeleton'></span>";
      byId("equipment-name").innerHTML = "<span class='skeleton'></span>";
      byId("quoted-total").innerHTML = "<span class='skeleton'></span>";
      byId("priority-label").innerHTML = "<span class='skeleton'></span>";
      byId("sla-due").innerHTML = "<span class='skeleton'></span>";
      byId("quote-sent-at").innerHTML = "<span class='skeleton'></span>";
      byId("decision-at").innerHTML = "<span class='skeleton'></span>";
    }
    applyCustomerPortalTheme(state.appearance.theme, state.appearance.primary);
    bootstrapSkeleton();
    attachListeners();
