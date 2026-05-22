    const customerPortalDefaultPrimary = "#0e7490";
    const customerPortalRoot = document.documentElement;
    function customerPortalIsHexColor(value) {
      return /^#[0-9a-fA-F]{6}$/.test(String(value || ""));
    }
    function customerPortalHexToRgb(value) {
      return [1, 3, 5].map(index => parseInt(value.slice(index, index + 2), 16));
    }
    function customerPortalToHex(channels) {
      return `#${channels.map(channel => Math.max(0, Math.min(Math.round(channel), 255)).toString(16).padStart(2, "0")).join("")}`;
    }
    function customerPortalMix(a, b, bWeight) {
      const aRgb = customerPortalHexToRgb(a);
      const bRgb = customerPortalHexToRgb(b);
      return customerPortalToHex(aRgb.map((channel, index) => channel * (1 - bWeight) + bRgb[index] * bWeight));
    }
    function updateCustomerPortalThemeToggle(theme) {
      const button = document.getElementById("theme-toggle");
      if (!button) return;
      button.textContent = theme === "dark" ? "Usar claro" : "Usar escuro";
      button.setAttribute("aria-pressed", String(theme === "dark"));
    }
    function applyCustomerPortalTheme(theme, primary) {
      const accent = customerPortalIsHexColor(primary) ? primary : customerPortalDefaultPrimary;
      const dark = theme === "dark";
      const palette = dark
        ? {
            "--accent": accent,
            "--accent-hover": customerPortalMix(accent, "#ffffff", 0.16),
            "--accent-soft": customerPortalMix(accent, "#0f172a", 0.52),
            "--accent-ink": "#0f172a",
            "--bg": customerPortalMix(accent, "#020617", 0.85),
            "--bg-gradient-a": customerPortalMix(accent, "#0f172a", 0.74),
            "--bg-gradient-b": customerPortalMix(accent, "#1e293b", 0.76),
            "--panel": customerPortalMix(accent, "#0f172a", 0.82),
            "--panel-soft": customerPortalMix(accent, "#1e293b", 0.76),
            "--line": customerPortalMix(accent, "#334155", 0.74),
            "--text": "#f8fafc",
            "--muted": customerPortalMix(accent, "#cbd5e1", 0.74),
            "--timeline": "#64748b",
            "--shadow": "0 22px 42px -24px rgba(0, 0, 0, 0.66)",
          }
        : {
            "--accent": accent,
            "--accent-hover": customerPortalMix(accent, "#000000", 0.16),
            "--accent-soft": customerPortalMix(accent, "#ffffff", 0.84),
            "--accent-ink": "#f8fafc",
            "--bg": customerPortalMix(accent, "#ffffff", 0.90),
            "--bg-gradient-a": customerPortalMix(accent, "#f0f9ff", 0.72),
            "--bg-gradient-b": customerPortalMix(accent, "#ecfeff", 0.72),
            "--panel": "#ffffff",
            "--panel-soft": customerPortalMix(accent, "#f1f5f9", 0.68),
            "--line": customerPortalMix(accent, "#cbd5e1", 0.72),
            "--text": "#0f172a",
            "--muted": customerPortalMix(accent, "#475569", 0.36),
            "--timeline": "#94a3b8",
            "--shadow": "0 20px 40px -26px rgba(2, 6, 23, 0.48)",
          };
      Object.entries(palette).forEach(([key, value]) => customerPortalRoot.style.setProperty(key, value));
      customerPortalRoot.style.setProperty("color-scheme", dark ? "dark" : "light");
      document.body.dataset.theme = theme;
      updateCustomerPortalThemeToggle(theme);
    }