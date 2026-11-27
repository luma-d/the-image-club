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

/* Workshop photo carousel (scroll direction follows the language) */
const carTrack = document.querySelector(".car-track");
const carDir = () => (carTrack && getComputedStyle(carTrack).direction === "rtl" ? -1 : 1);
document.querySelector(".car-prev")?.addEventListener("click", () =>
  carTrack?.scrollBy({ left: -carDir() * carTrack.clientWidth * 0.9, behavior: "smooth" }));
document.querySelector(".car-next")?.addEventListener("click", () =>
  carTrack?.scrollBy({ left: carDir() * carTrack.clientWidth * 0.9, behavior: "smooth" }));

/* Baraa Salih popup modal (shared, opened by [data-curator] triggers) */
const popup = document.getElementById("curatorPopup");
let popupTrigger = null;
function popupOpen() {
  if (!popup) return;
  popup.hidden = false;
  document.body.style.overflow = "hidden";
  popup.querySelector(".popup-close")?.focus();
}
function popupClose() {
  if (!popup) return;
  popup.hidden = true;
  document.body.style.overflow = "";
  if (popupTrigger) popupTrigger.focus();
  popupTrigger = null;
}
document.querySelectorAll("[data-curator]").forEach((el) => {
  el.addEventListener("click", (e) => {
    e.preventDefault();
    popupTrigger = el;
    popupOpen();
  });
});
if (popup) {
  popup.querySelector(".popup-close")?.addEventListener("click", popupClose);
  popup.addEventListener("click", (e) => { if (e.target === popup) popupClose(); });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !popup.hidden) popupClose();
  });
}
