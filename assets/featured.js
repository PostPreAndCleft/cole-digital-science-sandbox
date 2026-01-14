(() => {
  const root = document.getElementById("featured-carousel");
  if (!root) return;

  const image = root.querySelector("[data-carousel-image]");
  const title = root.querySelector("[data-carousel-title]");
  const takeaway = root.querySelector("[data-carousel-takeaway]");
  const year = root.querySelector("[data-carousel-year]");
  const links = root.querySelectorAll("[data-carousel-link]");
  const indicators = root.querySelector("[data-carousel-indicators]");
  const prevButton = root.querySelector("[data-carousel-prev]");
  const nextButton = root.querySelector("[data-carousel-next]");
  const pauseButton = root.querySelector("[data-carousel-pause]");

  if (!image || !title || !takeaway || !links.length || !indicators || !prevButton || !nextButton || !pauseButton) {
    return;
  }

  const prefersReducedMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches ?? false;
  const items = Array.isArray(window.FEATURED_PUBLICATIONS) ? window.FEATURED_PUBLICATIONS : [];
  if (!items.length) return;

  let index = 0;
  let timer = null;
  let paused = prefersReducedMotion;

  const escapeText = (value) => String(value ?? "");

  const setPauseLabel = () => {
    pauseButton.textContent = paused ? "Play" : "Pause";
    pauseButton.setAttribute("aria-pressed", paused ? "true" : "false");
  };

  const renderIndicators = () => {
    indicators.innerHTML = "";
    items.forEach((item, itemIndex) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "carousel-dot";
      button.setAttribute("aria-label", `Show publication ${itemIndex + 1}: ${escapeText(item.title)}`);
      button.setAttribute("aria-current", itemIndex === index ? "true" : "false");
      button.addEventListener("click", () => {
        index = itemIndex;
        update();
        restart();
      });
      indicators.appendChild(button);
    });
  };

  const update = () => {
    const item = items[index];
    image.src = item.figureSrc;
    image.alt = item.figureAlt || item.title || "Publication figure";
    title.textContent = item.title || "Publication highlight";
    takeaway.textContent = item.takeaway || "";
    if (year) year.textContent = item.year || "";
    links.forEach((anchor) => {
      anchor.href = item.link || "publications.html";
    });

    Array.from(indicators.querySelectorAll("button")).forEach((dot, dotIndex) => {
      dot.setAttribute("aria-current", dotIndex === index ? "true" : "false");
    });
  };

  const stop = () => {
    if (timer) {
      window.clearInterval(timer);
      timer = null;
    }
  };

  const start = () => {
    if (paused || prefersReducedMotion) return;
    stop();
    timer = window.setInterval(() => {
      index = (index + 1) % items.length;
      update();
    }, 9000);
  };

  const restart = () => {
    stop();
    start();
  };

  const go = (delta) => {
    index = (index + delta + items.length) % items.length;
    update();
    restart();
  };

  prevButton.addEventListener("click", () => go(-1));
  nextButton.addEventListener("click", () => go(1));
  pauseButton.addEventListener("click", () => {
    paused = !paused;
    setPauseLabel();
    restart();
  });

  root.addEventListener("mouseenter", () => {
    stop();
  });
  root.addEventListener("mouseleave", () => {
    start();
  });
  root.addEventListener("focusin", () => {
    stop();
  });
  root.addEventListener("focusout", () => {
    start();
  });

  renderIndicators();
  setPauseLabel();
  update();
  start();
})();
