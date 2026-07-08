(function () {
  function configuredLanguages() {
    return Array.prototype.map.call(
      document.querySelectorAll(".language-switcher a[data-language-code]"),
      function (link, index) {
        var code = link.getAttribute("data-language-code");
        return {
          code: code,
          prefix: index === 0 ? "" : code,
        };
      }
    );
  }

  var languages = configuredLanguages();

  function currentLanguageAndBasePath() {
    var path = window.location.pathname;
    var isFileUrl = window.location.protocol === "file:";

    if (isFileUrl) {
      for (var i = 0; i < languages.length; i += 1) {
        var language = languages[i];
        if (!language.prefix) {
          continue;
        }
        var marker = "/_build/html/" + language.prefix + "/";
        if (path.includes(marker)) {
          return {
            current: language.code,
            basePath: path.replace(marker, "/_build/html/"),
          };
        }
      }
      return { current: languages[0] ? languages[0].code : "", basePath: path };
    }

    for (var j = 0; j < languages.length; j += 1) {
      var lang = languages[j];
      if (!lang.prefix) {
        continue;
      }
      if (path === "/" + lang.prefix || path.startsWith("/" + lang.prefix + "/")) {
        return {
          current: lang.code,
          basePath: path.replace(new RegExp("^/" + lang.prefix + "(?=/|$)"), "") || "/",
        };
      }
    }

    return { current: languages[0] ? languages[0].code : "", basePath: path };
  }

  function urlFor(language, basePath) {
    var search = window.location.search || "";
    var hash = window.location.hash || "";
    var path = basePath || "/";
    var isFileUrl = window.location.protocol === "file:";

    if (!language.prefix) {
      return path + search + hash;
    }

    if (isFileUrl && path.includes("/_build/html/")) {
      return path.replace("/_build/html/", "/_build/html/" + language.prefix + "/") + search + hash;
    }

    if (path === "/") {
      return "/" + language.prefix + "/" + search + hash;
    }

    return "/" + language.prefix + path + search + hash;
  }

  function updateSwitcherLinks() {
    var state = currentLanguageAndBasePath();

    document.querySelectorAll(".language-switcher a[data-language-code]").forEach(function (link, index) {
      var language = languages[index];
      if (!language) {
        return;
      }

      link.href = urlFor(language, state.basePath);

      if (language.code === state.current) {
        link.setAttribute("aria-current", "page");
      } else {
        link.removeAttribute("aria-current");
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", updateSwitcherLinks);
  } else {
    updateSwitcherLinks();
  }
})();
