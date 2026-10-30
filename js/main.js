/* js/main.js — vanilla, no build step */
const IG_HANDLE = "theimageclub";
const IG_URL = "https://www.instagram.com/" + IG_HANDLE;

document.querySelector(".hamburger")?.addEventListener("click", () => {
  const btn = document.querySelector(".hamburger");
  const open = btn.getAttribute("aria-expanded") === "true";
  btn.setAttribute("aria-expanded", String(!open));
  document.querySelector(".nav-links")?.classList.toggle("open");
});

document.querySelectorAll('a[href^="#"]').forEach((a) => {
  a.addEventListener("click", (e) => {
    const id = a.getAttribute("href").slice(1);
    if (!id) return;
    const target = document.getElementById(id);
    if (!target) return;
    e.preventDefault();
    target.scrollIntoView({ behavior: "smooth", block: "start" });
  });
});

/* Scroll reveal is handled by CSS scroll-driven animations (see style.css). */
