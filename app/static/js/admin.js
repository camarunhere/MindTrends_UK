document.addEventListener("DOMContentLoaded", function () {
  const rowsWrap = document.getElementById("categoryRows");
  const addBtn = document.getElementById("addRowBtn");
  if (!rowsWrap || !addBtn) return;

  addBtn.addEventListener("click", function () {
    const row = document.createElement("div");
    row.className = "row g-2 mb-2 category-row";
    row.innerHTML = `
      <div class="col-7"><input type="text" name="category_name" class="form-control" placeholder="Category name"></div>
      <div class="col-3"><input type="number" name="category_gtrends_id" class="form-control" placeholder="Trends ID"></div>
      <div class="col-2"><button type="button" class="btn btn-danger-soft w-100 remove-row">✕</button></div>
    `;
    rowsWrap.appendChild(row);
  });

  rowsWrap.addEventListener("click", function (e) {
    if (e.target.classList.contains("remove-row")) {
      e.target.closest(".category-row").remove();
    }
  });
});
