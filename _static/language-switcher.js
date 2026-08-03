// Progressive enhancement: preserve the current URL hash across language
// switches. The switcher links are server-rendered with real hrefs, so they
// work without JavaScript. This script appends the page's current hash to
// each link so that, e.g. switching language on `/application/#diagram`
// lands on `/pl/application/#diagram` rather than dropping the anchor.
(function () {
  function updateLinks() {
    var search = window.location.search || "";
    var hash = window.location.hash || "";
    document.querySelectorAll(".language-switcher a").forEach(function (link) {
      var href = link.getAttribute("href");
      if (!href) {
        return;
      }
      var path = href.split("?")[0].split("#")[0];
      link.setAttribute("href", path + search + hash);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", updateLinks);
  } else {
    updateLinks();
  }
  window.addEventListener("hashchange", updateLinks);
  window.addEventListener("popstate", updateLinks);
})();
