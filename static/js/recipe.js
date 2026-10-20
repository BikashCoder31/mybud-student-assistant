"use strict";
(() => {
  const form = document.getElementById("recipe-form"), output = document.getElementById("recipe-results"), status = document.getElementById("recipe-status");
  let stream;
  function details(item) {
    output.append(MyBud.element("h3", item.name || item.dish_name), MyBud.element("p", item.description));
    if (item.time) output.append(MyBud.element("p", item.time + " · Servings: " + item.servings));
    if (item.ingredients.length) { output.append(MyBud.element("h4", "Ingredients")); const list = MyBud.element("div"); MyBud.list(list, item.ingredients); output.append(list); }
    if (item.instructions.length) { output.append(MyBud.element("h4", "Instructions")); const list = MyBud.element("div"); MyBud.list(list, item.instructions); output.append(list); }
  }
  form.addEventListener("submit", event => { event.preventDefault();
    MyBud.busy(form, status, async () => {
      const ingredients = document.getElementById("ingredients").value.split(",").map(x => x.trim()).filter(Boolean);
      const data = await MyBud.request("/api/recipes/", {ingredients}); output.replaceChildren(); data.recipes.forEach(details);
    });
  });
  async function identify(image) { const data = await MyBud.request("/api/detect-food/", {image}); output.replaceChildren(); details(data.dish); }
  const upload = document.getElementById("image-file");
  upload.addEventListener("change", () => {
    const file = upload.files[0]; if (!file) return;
    MyBud.busy(document.getElementById("main"), status, async () => {
      if (file.size > 5 * 1024 * 1024) throw new Error("Use an image up to 5 MB.");
      const image = await new Promise((resolve, reject) => { const reader = new FileReader(); reader.onload = () => resolve(reader.result); reader.onerror = () => reject(new Error("Unable to read this file.")); reader.readAsDataURL(file); });
      await identify(image);
    });
  });
  function stop() { if (stream) stream.getTracks().forEach(track => track.stop()); stream = null; document.getElementById("camera-area").hidden = true; }
  document.getElementById("camera-start").addEventListener("click", () => MyBud.busy(form, status, async () => {
    stop(); if (!navigator.mediaDevices?.getUserMedia) throw new Error("Camera requires a supported browser and localhost or HTTPS. You can upload a photo instead.");
    stream = await navigator.mediaDevices.getUserMedia({video: {facingMode: "environment"}, audio: false});
    document.getElementById("camera-video").srcObject = stream; document.getElementById("camera-area").hidden = false;
  }));
  document.getElementById("camera-stop").addEventListener("click", stop);
  document.getElementById("camera-capture").addEventListener("click", () => MyBud.busy(document.getElementById("main"), status, async () => {
    const video = document.getElementById("camera-video"); if (!video.videoWidth) throw new Error("Wait for the camera preview.");
    const canvas = document.createElement("canvas"); canvas.width = video.videoWidth; canvas.height = video.videoHeight; canvas.getContext("2d").drawImage(video, 0, 0); const image = canvas.toDataURL("image/jpeg"); stop(); await identify(image);
  }));
  window.addEventListener("pagehide", stop);
})();
