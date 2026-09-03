(function () {
  const disorderChips = document.querySelectorAll("#disorderChips .chip");
  const regionChips = document.querySelectorAll("#regionChips .chip");
  const retrieveBtn = document.getElementById("retrieveBtn");
  const retrieveStatus = document.getElementById("retrieveStatus");
  const resultsWrap = document.getElementById("resultsWrap");
  const emptyState = document.getElementById("emptyState");
  const warningsWrap = document.getElementById("warningsWrap");
  const analysisTableBody = document.getElementById("analysisTableBody");
  const comparisonSummary = document.getElementById("comparisonSummary");

  let mainChart = null;
  let lastResult = null;
  let lastParams = null;

  // Preselect a disorder passed via ?disorder=<id>
  const presetId = new URLSearchParams(location.search).get("disorder");
  if (presetId) {
    disorderChips.forEach((chip) => {
      if (chip.dataset.id === presetId) chip.classList.add("active");
    });
  }

  function toggleChip(chip) {
    chip.classList.toggle("active");
  }
  disorderChips.forEach((chip) => chip.addEventListener("click", () => toggleChip(chip)));
  regionChips.forEach((chip) => chip.addEventListener("click", () => toggleChip(chip)));

  function selectedDisorderIds() {
    return [...disorderChips].filter((c) => c.classList.contains("active")).map((c) => c.dataset.id);
  }
  function selectedRegionCodes() {
    const active = [...regionChips].filter((c) => c.classList.contains("active")).map((c) => c.dataset.code);
    return active.length ? active : [regionChips[0]?.dataset.code || "GB"];
  }

  function directionBadge(direction) {
    return `<span class="direction-badge direction-${direction}">${direction}</span>`;
  }

  function renderWarnings(warnings) {
    warningsWrap.innerHTML = "";
    warnings.forEach((w) => {
      const div = document.createElement("div");
      div.className = "alert alert-warning py-2 px-3 mb-2";
      div.innerHTML = `<i class="bi bi-exclamation-triangle me-2"></i>${w}`;
      warningsWrap.appendChild(div);
    });
  }

  function renderResults(result) {
    lastResult = result;
    resultsWrap.classList.remove("d-none");
    emptyState.classList.add("d-none");

    renderWarnings(result.warnings || []);

    if (mainChart) mainChart.destroy();
    mainChart = MT.lineChart(document.getElementById("mainChart"), result.series);

    comparisonSummary.textContent = result.comparison.summary || "";

    analysisTableBody.innerHTML = "";
    result.comparison.analyses.forEach((a) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td class="fw-semibold">${a.label}</td>
        <td>${a.average}</td>
        <td>${a.start_value} → ${a.end_value}</td>
        <td>${a.change_pct > 0 ? "+" : ""}${a.change_pct}%</td>
        <td>${a.peak_value} <span class="text-muted small">(${a.peak_date || "—"})</span></td>
        <td>${directionBadge(a.direction)}</td>
      `;
      analysisTableBody.appendChild(tr);
    });
  }

  async function retrieve() {
    const disorder_ids = selectedDisorderIds();
    if (!disorder_ids.length) {
      retrieveStatus.textContent = "Please select at least one disorder.";
      retrieveStatus.classList.add("text-danger");
      return;
    }
    retrieveStatus.classList.remove("text-danger");
    retrieveStatus.textContent = "Retrieving…";
    retrieveBtn.disabled = true;

    const params = {
      disorder_ids,
      regions: selectedRegionCodes(),
      timeframe: document.getElementById("timeframeSelect").value,
      category: parseInt(document.getElementById("categorySelect").value, 10),
    };
    lastParams = params;

    try {
      const res = await fetch("/dashboard/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(params),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Retrieval failed.");
      renderResults(data);
      retrieveStatus.textContent = `Retrieved ${data.series.length} series.`;
    } catch (err) {
      retrieveStatus.textContent = err.message;
      retrieveStatus.classList.add("text-danger");
    } finally {
      retrieveBtn.disabled = false;
    }
  }
  retrieveBtn.addEventListener("click", retrieve);

  // ---- Save ----
  const saveModalEl = document.getElementById("saveModal");
  const saveModal = new bootstrap.Modal(saveModalEl);
  document.getElementById("saveBtn").addEventListener("click", () => saveModal.show());

  document.getElementById("confirmSaveBtn").addEventListener("click", async () => {
    const title = document.getElementById("analysisTitle").value.trim() || "Untitled analysis";
    await fetch("/dashboard/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title,
        params: lastParams,
        summary: { leader: lastResult.comparison.leader, summary: lastResult.comparison.summary },
      }),
    });
    saveModal.hide();
    retrieveStatus.textContent = "Analysis saved.";
  });

  // ---- Export ----
  async function download(url, body, filename) {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const blob = await res.blob();
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
  }

  document.getElementById("exportCsvBtn").addEventListener("click", () => {
    download("/dashboard/export/csv", { series: lastResult.series }, "mindtrends_export.csv");
  });

  document.getElementById("exportPdfBtn").addEventListener("click", () => {
    download(
      "/dashboard/export/pdf",
      { series: lastResult.series, params: lastParams, analyses: lastResult.comparison.analyses },
      "mindtrends_report.pdf"
    );
  });
})();
