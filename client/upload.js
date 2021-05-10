document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("uploadButton").addEventListener("click", (e) => {
    e.preventDefault();
    const data = new FormData();
    data.append("audio", document.getElementById("audio").files[0]);
    console.log(document.getElementById("audio").files[0]);
    fetch("https://compute.gaida.link", {
      method: "POST",
      body: data,
    })
      .then((response) => response.blob())
      .then((blob) => {
        var file = window.URL.createObjectURL(blob);
        window.location.assign(file);
      });
  });
});
