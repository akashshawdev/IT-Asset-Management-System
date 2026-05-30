function toggleModal(id) {
  const el = document.getElementById(id);
  el.classList.toggle("hidden");
}

document.addEventListener("keydown", function(e) {
  if (e.key === "Escape") {
    document.querySelectorAll(".modal-overlay").forEach(m => m.classList.add("hidden"));
  }
});
