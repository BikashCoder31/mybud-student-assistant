"use strict";
(() => {
  const form = document.getElementById("travel-form"), output = document.getElementById("travel-results");
  form.addEventListener("submit", event => { event.preventDefault();
    MyBud.busy(form, document.getElementById("travel-status"), async () => {
      const data = await MyBud.request("/api/travel/", {destination: document.getElementById("destination-input").value, duration: Number(document.getElementById("duration-input").value)});
      output.replaceChildren(MyBud.element("h3", data.data.destination), MyBud.element("p", data.data.info));
      data.data.itinerary.forEach(day => { output.append(MyBud.element("h4", day.title)); const section = MyBud.element("div"); MyBud.list(section, day.activities); output.append(section); });
    });
  });
})();
