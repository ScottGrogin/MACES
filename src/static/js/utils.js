function log(msg) {
  const div = document.createElement("div");
  div.textContent = msg;
  div.className = "log";

  document.body.appendChild(div);

  setTimeout(() => {
    div.remove();
  }, 3000);
}
