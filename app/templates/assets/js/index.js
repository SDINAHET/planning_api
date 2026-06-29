    function toggleTheme() {
      const html = document.documentElement;
      const icon = document.getElementById("theme-icon");
      const next = html.dataset.theme === "dark" ? "light" : "dark";

      html.dataset.theme = next;
      localStorage.setItem("theme", next);

      icon.className = next === "dark"
        ? "fa-regular fa-lightbulb"
        : "fa-regular fa-moon";
    }

    function initTheme() {
      const saved = localStorage.getItem("theme") || "dark";
      const icon = document.getElementById("theme-icon");

      document.documentElement.dataset.theme = saved;

      icon.className = saved === "dark"
        ? "fa-regular fa-lightbulb"
        : "fa-regular fa-moon";
    }

    const searchInput = document.getElementById("searchInput");
    const cards = document.querySelectorAll(".person-card");
    const noResult = document.getElementById("noResult");
    const personSelect = document.getElementById("personSelect");

    function normalizeText(text) {
      return text
        .toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "");
    }

    searchInput.addEventListener("input", () => {
      const query = normalizeText(searchInput.value.trim());
      let visibleCount = 0;

      cards.forEach(card => {
        const name = normalizeText(card.dataset.name);

        if (name.includes(query)) {
          card.style.display = "flex";
          visibleCount++;
        } else {
          card.style.display = "none";
        }
      });

      noResult.style.display = visibleCount === 0 ? "block" : "none";
    });

    personSelect.addEventListener("change", () => {
      if (personSelect.value) {
        window.location.href = personSelect.value;
      }
    });

    initTheme();
