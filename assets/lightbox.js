/* Picture viewer for db9v12.co.uk.
   Tap a photo to open it full screen, then swipe (or use the arrows / arrow keys) through the photos in the same
   group: one log entry, one Friends date, or every photo on a reference page. Esc, the close button or the
   phone's back button closes it. Slides are a native scroll-snap strip, so swiping feels like a phone's photo app.
   Tapping the photo itself opens it in assets/view.html in a new tab, at 100%, where it can be dragged and zoomed.
   window.lbOpen(urls, i) is kept for the home-page hero rotator. Classes use "pv" (the site already uses .lb). */
(function () {
  var root = new URL("..", document.currentScript ? document.currentScript.src : location.href);
  var IMG = /\.(jpe?g|png|webp)$/i;
  function viewer(u) {  // assets/view.html (drag + zoom) for this site's own photos/diagrams, else the file itself
    var abs = new URL(u, location.href);
    if (abs.origin !== root.origin || abs.pathname.indexOf(root.pathname) !== 0) return abs.href;
    var rel = decodeURIComponent(abs.pathname.slice(root.pathname.length));
    if (!/^(photos|diagrams)\//.test(rel)) return abs.href;
    return new URL("assets/view.html?src=" + encodeURIComponent(rel), root).href;
  }

  // ---- collect the clickable photos, grouped -------------------------------------------------------------------
  var nodes = Array.prototype.slice.call(document.querySelectorAll(
    ".photo-strip a, a.lb, .gallery a, .figs a, figure a, figure > img"));
  var seen = [], groups = [], byKey = new Map();
  nodes.forEach(function (el) {
    var link = el.tagName === "A" ? el : null, img = link ? link.querySelector("img") : el;
    if (link && !IMG.test(link.getAttribute("href") || "")) return;
    if (!link && el.closest("a")) return;                       // handled through its link
    if (seen.indexOf(el) >= 0) return; seen.push(el);
    var key = el.closest(".entry, .date-group") || document.body;
    if (!byKey.has(key)) { var g = { els: [], items: [] }; byKey.set(key, g); groups.push(g); }
    byKey.get(key).els.push(el);
  });
  groups.forEach(function (g) {
    g.els.sort(function (a, b) { return b.hasAttribute("data-lb-first") - a.hasAttribute("data-lb-first"); });
    g.items = g.els.map(function (el) {
      var link = el.tagName === "A" ? el : null, img = link ? link.querySelector("img") : el;
      var fig = el.closest("figure"), cap = fig && fig.querySelector("figcaption"), gcap = link && link.querySelector(".g-cap");
      var src = link ? link.getAttribute("href") : (img.currentSrc || img.src);
      return { src: src, full: (img && img.getAttribute("data-full")) || src, alt: img ? img.alt : "",
               cap: cap ? cap.innerHTML : gcap ? gcap.textContent : "" };
    });
  });

  // ---- the viewer --------------------------------------------------------------------------------------------
  var box = document.createElement("div");
  box.className = "pv"; box.hidden = true;
  box.setAttribute("role", "dialog"); box.setAttribute("aria-modal", "true"); box.setAttribute("aria-label", "Photo viewer");
  box.innerHTML = '<div class="pv__track"></div>' +
    '<button class="pv__btn pv__close" aria-label="Close">&times;</button>' +
    '<button class="pv__btn pv__prev" aria-label="Previous photo">&lsaquo;</button>' +
    '<button class="pv__btn pv__next" aria-label="Next photo">&rsaquo;</button>' +
    '<p class="pv__count" aria-live="polite"></p>';
  document.body.appendChild(box);
  var track = box.querySelector(".pv__track"), count = box.querySelector(".pv__count");
  var items = [], els = null, cur = 0, opener = null;

  function build(list) {
    track.textContent = "";
    list.forEach(function (it) {
      var s = document.createElement("figure");
      s.className = "pv__slide";
      s.innerHTML = '<a class="pv__full" target="_blank" rel="noopener"><img alt="" decoding="async"></a><figcaption></figcaption>';
      var a = s.querySelector("a");
      a.href = viewer(it.full);
      a.title = "Open the photo in a new tab (drag and zoom)";
      s.querySelector("img").alt = it.alt;
      s.querySelector("figcaption").innerHTML = it.cap;
      track.appendChild(s);
    });
  }
  function load(i) {  // only fetch the photo being viewed and the ones either side
    for (var j = i - 1; j <= i + 1; j++) {
      var im = track.children[j] && track.children[j].querySelector("img");
      if (im && !im.getAttribute("src")) im.src = items[j].src;
    }
  }
  function show(i) {
    cur = Math.max(0, Math.min(items.length - 1, i));
    load(cur);
    count.textContent = (cur + 1) + " / " + items.length;
    box.querySelector(".pv__prev").hidden = cur === 0;
    box.querySelector(".pv__next").hidden = cur === items.length - 1;
  }
  function go(i) {
    i = Math.max(0, Math.min(items.length - 1, i));
    track.scrollTo({ left: i * track.clientWidth, behavior: "smooth" });
  }
  function open(list, elList, i) {
    items = list; els = elList; opener = document.activeElement;
    build(items);
    box.hidden = false;
    document.documentElement.classList.add("pv-open");
    track.scrollLeft = i * track.clientWidth;
    show(i);
    box.querySelector(".pv__close").focus();
    history.pushState({ pv: 1 }, "");
  }
  function close(fromHistory) {
    if (box.hidden) return;
    box.hidden = true;
    document.documentElement.classList.remove("pv-open");
    if (els && els[cur]) els[cur].scrollIntoView({ block: "center" });
    if (opener && opener.focus) opener.focus({ preventScroll: true });
    if (!fromHistory && history.state && history.state.pv) history.back();
  }

  groups.forEach(function (g) {
    g.els.forEach(function (el, i) {
      var img = el.tagName === "A" ? el.querySelector("img") : el;
      if (el.tagName !== "A") { el.tabIndex = 0; el.setAttribute("role", "button"); }
      if (img) img.style.cursor = "zoom-in";
      el.addEventListener("click", function (e) { e.preventDefault(); open(g.items, g.els, i); });
      el.addEventListener("keydown", function (e) {
        if (el.tagName !== "A" && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); open(g.items, g.els, i); }
      });
    });
  });
  window.lbOpen = function (urls, i) {  // used by the home-page hero rotator
    open(urls.map(function (u) { return { src: u, full: u, alt: "", cap: "" }; }), null, i || 0);
  };

  var t;
  track.addEventListener("scroll", function () {
    clearTimeout(t);
    t = setTimeout(function () { show(Math.round(track.scrollLeft / track.clientWidth)); }, 60);
  });
  window.addEventListener("resize", function () { if (!box.hidden) track.scrollLeft = cur * track.clientWidth; });
  box.querySelector(".pv__close").addEventListener("click", function () { close(false); });
  box.querySelector(".pv__prev").addEventListener("click", function () { go(cur - 1); });
  box.querySelector(".pv__next").addEventListener("click", function () { go(cur + 1); });
  track.addEventListener("click", function (e) { if (e.target === track || e.target.classList.contains("pv__slide")) close(false); });
  window.addEventListener("popstate", function () { close(true); });
  document.addEventListener("keydown", function (e) {
    if (box.hidden) return;
    if (e.key === "Escape") close(false);
    else if (e.key === "ArrowRight") go(cur + 1);
    else if (e.key === "ArrowLeft") go(cur - 1);
    else if (e.key === "Tab") {  // keep focus inside the viewer
      var b = Array.prototype.filter.call(box.querySelectorAll("button"), function (x) { return !x.hidden; });
      var k = b.indexOf(document.activeElement);
      e.preventDefault();
      b[(k + (e.shiftKey ? -1 : 1) + b.length) % b.length].focus();
    }
  });
})();
