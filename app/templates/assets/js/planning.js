    function toggleTheme() {
      const html = document.documentElement;
      const icon = document.getElementById("theme-icon");
      const next = html.dataset.theme === "dark" ? "light" : "dark";
      html.dataset.theme = next;
      localStorage.setItem("theme", next);
      icon.className = next === "dark" ? "fa-regular fa-lightbulb" : "fa-regular fa-moon";
    }

    function initTheme() {
      const saved = localStorage.getItem("theme") || "dark";
      document.documentElement.dataset.theme = saved;
      document.getElementById("theme-icon").className =
        saved === "dark" ? "fa-regular fa-lightbulb" : "fa-regular fa-moon";
    }

    function updateDayCounts() {
      document.querySelectorAll(".day-card").forEach(dayCard => {
        const visibleSlots = Array.from(dayCard.querySelectorAll(".slot-card"))
          .filter(slot => slot.style.display !== "none");

        const count = visibleSlots.length;
        const badge = dayCard.querySelector(".count");

        if (badge) {
          badge.textContent = count > 1 ? `${count} créneaux` : `${count} créneau`;
        }

        dayCard.style.display = count === 0 ? "none" : "";
      });
    }

    function parseTimeRange(horaire) {
      const normalized = horaire.replace(/\s/g, "").replace(/–/g, "-").replace(/—/g, "-");

      function parsePart(value) {
        const match = value.match(/^(\d{1,2})h(?:(\d{2}))?$/i);
        if (!match) return null;
        return {
          hour: Number(match[1]),
          minute: match[2] ? Number(match[2]) : 0
        };
      }

      const parts = normalized.split("-");
      const start = parsePart(parts[0]);
      if (!start) return null;

      let end = parts.length >= 2 ? parsePart(parts[1]) : null;

      if (!end) {
        const temp = new Date();
        temp.setHours(start.hour, start.minute + 30, 0, 0);
        end = { hour: temp.getHours(), minute: temp.getMinutes() };
      }

      return { start, end };
    }

    function updateSlotsState() {
      const now = new Date();

      document.querySelectorAll(".slot-card").forEach(card => {
        const date = card.dataset.date;
        const range = parseTimeRange(card.dataset.horaire || "");
        const badgeText = card.querySelector(".badge-text");
        const fill = card.querySelector(".progress-fill");

        card.classList.remove("past", "current");
        badgeText.textContent = "À venir";
        fill.style.width = "0%";

        if (!date || !range) return;

        const startDate = new Date(
          `${date}T${String(range.start.hour).padStart(2, "0")}:${String(range.start.minute).padStart(2, "0")}:00`
        );

        const endDate = new Date(
          `${date}T${String(range.end.hour).padStart(2, "0")}:${String(range.end.minute).padStart(2, "0")}:00`
        );

        if (now > endDate) {
          card.classList.add("past");
          badgeText.textContent = "Passé";
          return;
        }

        if (now >= startDate && now <= endDate) {
          card.classList.add("current");
          badgeText.textContent = "En cours";
          const percent = ((now - startDate) / (endDate - startDate)) * 100;
          fill.style.width = Math.max(0, Math.min(100, percent)) + "%";
        }
      });
    }

    function initSearch() {
      const input = document.getElementById("searchInput");
      const emptySearch = document.getElementById("emptySearch");

      if (!input) return;

      input.addEventListener("input", () => {
        const query = input.value.trim().toLowerCase();
        let visibleCount = 0;

        document.querySelectorAll(".slot-card").forEach(card => {
          const content = (card.dataset.search || "").toLowerCase();
          const visible = content.includes(query);
          card.style.display = visible ? "" : "none";
          if (visible) visibleCount++;
        });

        updateDayCounts();
        emptySearch.style.display = visibleCount === 0 ? "" : "none";

        try {
          sessionStorage.setItem("planningSearch", query);
        } catch (e) {}
      });

      try {
        const saved = sessionStorage.getItem("planningSearch") || "";
        input.value = saved;
        if (saved) input.dispatchEvent(new Event("input"));
      } catch (e) {}
    }

    function toggleBurgerMenu() {
      document.body.classList.toggle("menu-open");
    }

    function initScrollMenu() {
      window.addEventListener("scroll", () => {
        if (window.scrollY > 90) {
          document.body.classList.add("scrolled");
        } else {
          document.body.classList.remove("scrolled");
          document.body.classList.remove("menu-open");
        }
      });
    }

    function toggleSummary(event, button) {
      event.preventDefault();
      event.stopPropagation();

      const wrapper = button.closest(".talk-summary-wrapper");
      if (!wrapper) return;

      const isOpen = wrapper.classList.toggle("open");
      button.textContent = isOpen ? "Voir moins" : "Voir plus";
    }

    document.addEventListener("click", function (event) {
      if (event.target.closest(".talk-summary-wrapper")) {
        event.stopPropagation();
      }
    });

    initTheme();
    initScrollMenu();
    updateSlotsState();
    updateDayCounts();
    initSearch();
    setInterval(updateSlotsState, 60000);
