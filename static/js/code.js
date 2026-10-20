"use strict";
(() => {
  const form = document.getElementById("code-form");
  form.addEventListener("submit", event => { event.preventDefault();
    MyBud.busy(form, document.getElementById("code-status"), async () => {
      const data = await MyBud.request("/api/code/", {code: document.getElementById("code-input").value, language: document.getElementById("language").value});
      for (const key of ["bugs", "suggestions", "explanations"]) MyBud.list(document.getElementById(key + "-list"), data.analysis[key], key === "bugs" ? "No syntax findings in this check. This does not establish correctness." : "No items returned.");
    });
  });
})();
