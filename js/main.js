/* js/main.js — vanilla, no build step */
const IG_HANDLE = "the.image.club";
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

/* Language toggle: English default, persisted in localStorage */
const root = document.documentElement;
try {
  if (localStorage.getItem("tic-lang") === "ar") { root.classList.add("lang-ar"); root.lang = "ar"; }
} catch (e) { /* storage unavailable */ }
document.getElementById("langBtn")?.addEventListener("click", () => {
  const ar = !root.classList.contains("lang-ar");
  root.classList.toggle("lang-ar", ar);
  root.lang = ar ? "ar" : "en";
  try { localStorage.setItem("tic-lang", ar ? "ar" : "en"); } catch (e) { /* ignore */ }
});

/* Workshop photo carousel */
const carTrack = document.querySelector(".car-track");
document.querySelector(".car-prev")?.addEventListener("click", () =>
  carTrack?.scrollBy({ left: -carTrack.clientWidth * 0.9, behavior: "smooth" }));
document.querySelector(".car-next")?.addEventListener("click", () =>
  carTrack?.scrollBy({ left: carTrack.clientWidth * 0.9, behavior: "smooth" }));
