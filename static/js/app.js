"use strict";
window.MyBud = {
  token() { return document.querySelector('meta[name="csrf-token"]').content; },
  async request(path, payload) {
    const options = payload === undefined ? {} : {method: "POST", headers: {"Content-Type": "application/json", "X-CSRFToken": this.token()}, body: JSON.stringify(payload)};
    const response = await fetch(path, options);
    const type = response.headers.get("content-type") || "";
    if (!type.includes("application/json")) throw new Error("Request could not be completed. Refresh the page and try again.");
    const data = await response.json();
    if (!response.ok || !data.success) throw new Error(data.error || "Request failed.");
    return data;
  },
  element(tag, text, className) { const node = document.createElement(tag); if (text !== undefined) node.textContent = String(text); if (className) node.className = className; return node; },
  list(parent, items, empty = "No findings returned.") {
    parent.replaceChildren();
    if (!items.length) { parent.append(this.element("p", empty)); return; }
    const list = this.element("ul"); items.forEach(item => list.append(this.element("li", item))); parent.append(list);
  },
  async busy(form, status, action) {
    const buttons = [...form.querySelectorAll("button")]; buttons.forEach(button => button.disabled = true);
    status.textContent = "Working…"; status.classList.remove("is-error");
    try { await action(); status.textContent = "Complete."; }
    catch (error) { status.textContent = error.message; status.classList.add("is-error"); }
    finally { buttons.forEach(button => button.disabled = false); }
  }
};
