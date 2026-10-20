"use strict";
(() => {
  const status = document.getElementById("expense-status"), section = document.getElementById("main");
  const amount = value => "NPR " + Number(value).toLocaleString("en-NP", {minimumFractionDigits: 2, maximumFractionDigits: 2});
  function render(data) {
    document.getElementById("expense-month").textContent = data.month;
    const summary = document.getElementById("budget-summary"); summary.replaceChildren(MyBud.element("p", "Spent: " + amount(data.total)));
    if (data.budget !== null) { summary.append(MyBud.element("p", "Budget: " + amount(data.budget)), MyBud.element("p", (data.exceeded ? "Over budget by: " : "Remaining: ") + amount(Math.abs(Number(data.remaining))), data.exceeded ? "is-error" : "")); }
    else summary.append(MyBud.element("p", "Set a budget to see your remaining balance."));
    const list = document.getElementById("expense-list"); list.replaceChildren();
    if (!data.expenses.length) { const row = MyBud.element("tr"), cell = MyBud.element("td", "No expenses this month."); cell.colSpan = 3; row.append(cell); list.append(row); }
    data.expenses.forEach(item => { const row = MyBud.element("tr"), action = MyBud.element("td"), button = MyBud.element("button", "Remove", "btn"); button.type = "button"; button.setAttribute("aria-label", "Remove " + item.category); button.addEventListener("click", () => save({action: "delete", id: item.id})); action.append(button); row.append(MyBud.element("td", item.category), MyBud.element("td", amount(item.amount)), action); list.append(row); });
    const categories = document.getElementById("expense-categories"); categories.replaceChildren();
    data.categories.forEach(item => { const row = MyBud.element("div", undefined, "category-total"); row.append(MyBud.element("p", item.category + ": " + amount(item.amount))); const bar = MyBud.element("div", undefined, "category-bar"); bar.style.width = (Number(data.total) ? Math.max(1, Number(item.amount) / Number(data.total) * 100) : 0) + "%"; row.append(bar); categories.append(row); });
  }
  async function save(payload) { await MyBud.busy(section, status, async () => { const data = await MyBud.request("/api/expenses/", payload); render(data); if (payload.action === "add") document.getElementById("expense-form").reset(); }); }
  document.getElementById("budget-form").addEventListener("submit", event => { event.preventDefault(); save({action: "budget", amount: document.getElementById("budget-input").value}); });
  document.getElementById("expense-form").addEventListener("submit", event => { event.preventDefault(); save({action: "add", category: document.getElementById("category-input").value, amount: document.getElementById("amount-input").value}); });
  document.getElementById("expense-reset").addEventListener("click", () => { if (confirm("Remove all expenses and the budget for this month in this browser?")) save({action: "reset"}); });
  MyBud.busy(section, status, async () => render(await MyBud.request("/api/expenses/")));
})();
