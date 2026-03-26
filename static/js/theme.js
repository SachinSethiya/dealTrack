document.addEventListener("DOMContentLoaded", function () {
    const toggleBtn = document.getElementById("theme-toggle");
    const icon = document.getElementById("theme-icon");

    // If button not found, stop (prevents errors)
    if (!toggleBtn) return;

    // =========================
    // LOAD SAVED THEME
    // =========================
    const savedTheme = localStorage.getItem("theme");

    if (savedTheme === "dark") {
        document.body.classList.add("dark-mode");
        if (icon) icon.classList.replace("bi-moon", "bi-sun");
    } else {
        document.body.classList.remove("dark-mode");
        if (icon) icon.classList.replace("bi-sun", "bi-moon");
    }

    // =========================
    // TOGGLE THEME
    // =========================
    toggleBtn.addEventListener("click", function () {
        document.body.classList.toggle("dark-mode");

        const isDark = document.body.classList.contains("dark-mode");

        if (isDark) {
            localStorage.setItem("theme", "dark");
            if (icon) icon.classList.replace("bi-moon", "bi-sun");
        } else {
            localStorage.setItem("theme", "light");
            if (icon) icon.classList.replace("bi-sun", "bi-moon");
        }
    });

    // =========================
    // OPTIONAL: SYSTEM THEME (first visit only)
    // =========================
    if (!savedTheme) {
        const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;

        if (prefersDark) {
            document.body.classList.add("dark-mode");
            localStorage.setItem("theme", "dark");
            if (icon) icon.classList.replace("bi-moon", "bi-sun");
        }
    }
});