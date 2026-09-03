/* Shared Chart.js helpers for MindTrends UK. */
window.MT = window.MT || {};

MT.palette = ["#22d3ee", "#a78bfa", "#f472b6", "#34d399", "#fbbf24", "#60a5fa", "#fb7185"];

MT.colorFor = function (index) {
  return MT.palette[index % MT.palette.length];
};

Chart.defaults.color = "#b9c0d4";
Chart.defaults.borderColor = "rgba(255,255,255,0.08)";
Chart.defaults.font.family = "'Manrope', system-ui, sans-serif";

MT.lineChart = function (canvas, seriesList, opts) {
  opts = opts || {};
  const ctx = canvas.getContext("2d");
  const datasets = seriesList.map((s, i) => {
    const color = MT.colorFor(i);
    const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height || 320);
    gradient.addColorStop(0, color + "55");
    gradient.addColorStop(1, color + "00");
    return {
      label: s.label,
      data: s.values,
      borderColor: color,
      backgroundColor: gradient,
      borderWidth: 2.5,
      pointRadius: 0,
      pointHoverRadius: 5,
      pointHoverBackgroundColor: color,
      tension: 0.35,
      fill: seriesList.length <= 3,
    };
  });

  const labels = seriesList.length ? seriesList[0].dates : [];

  return new Chart(ctx, {
    type: "line",
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { display: seriesList.length > 1, position: "bottom", labels: { boxWidth: 10, boxHeight: 10, usePointStyle: true } },
        tooltip: {
          backgroundColor: "#111529",
          borderColor: "rgba(255,255,255,0.12)",
          borderWidth: 1,
          padding: 10,
          titleColor: "#f4f6fb",
          bodyColor: "#b9c0d4",
        },
      },
      scales: {
        x: { grid: { display: false }, ticks: { maxTicksLimit: 8 } },
        y: { min: 0, max: 100, grid: { color: "rgba(255,255,255,0.06)" }, ticks: { stepSize: 25 } },
      },
      ...opts,
    },
  });
};

MT.barChart = function (canvas, labels, values, opts) {
  opts = opts || {};
  const ctx = canvas.getContext("2d");
  const colors = labels.map((_, i) => MT.colorFor(i));
  return new Chart(ctx, {
    type: "bar",
    data: { labels, datasets: [{ data: values, backgroundColor: colors, borderRadius: 8, maxBarThickness: 46 }] },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false } },
        y: { min: 0, max: 100, grid: { color: "rgba(255,255,255,0.06)" } },
      },
      ...opts,
    },
  });
};
