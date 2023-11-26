const loremIpsum = document.getElementById("lorem-ipsum");
fetch("https://baconipsum.com/api/?type=all-meat&paras=200&format=html")
  .then((response) => response.text())
  .then((result) => (loremIpsum.innerHTML = result));
const closeBtn = modal.querySelector(".close-area");
closeBtn.addEventListener("click", (e) => {
  modal.style.display = "none";
});
modal.addEventListener("click", (e) => {
  const evTarget = e.target;
  if (evTarget.classList.contains("modal-overlay")) {
    modal.style.display = "none";
  }
});
window.addEventListener("keyup", (e) => {
  if (modal.style.display === "flex" && e.key === "Escape") {
    modal.style.display = "none";
  }
});
