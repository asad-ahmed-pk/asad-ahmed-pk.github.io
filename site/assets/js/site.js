// Progressive enhancement only: the page works fully without JS.
document.documentElement.classList.add("js");

document.addEventListener("DOMContentLoaded", () => {
  // Print / Save as PDF (uses the print stylesheet in src/input.css)
  for (const b of document.querySelectorAll("[data-print]")) {
    b.addEventListener("click", () => window.print());
  }

  // Highlight the nav link of the section in view
  const links = new Map(
    [...document.querySelectorAll('.nav-links a[href^="/#"]')].map((a) => [a.hash.slice(1), a])
  );
  const sections = [...links.keys()].map((id) => document.getElementById(id)).filter(Boolean);
  if (!sections.length || !("IntersectionObserver" in window)) return;
  const io = new IntersectionObserver(
    (entries) => {
      for (const e of entries) {
        if (!e.isIntersecting) continue;
        for (const a of links.values()) a.removeAttribute("aria-current");
        links.get(e.target.id)?.setAttribute("aria-current", "true");
      }
    },
    { rootMargin: "-45% 0px -50% 0px" }
  );
  sections.forEach((s) => io.observe(s));
});
