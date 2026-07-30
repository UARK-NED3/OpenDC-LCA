import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const tables = path.join(root, "paper", "tables");
const output = path.join(root, "paper", "OpenDC-LCA_integrated_evidence.xlsx");
const previewDir = path.join(root, "paper", "workbook-previews");

async function csvValues(filename) {
  const text = await fs.readFile(path.join(tables, filename), "utf8");
  const book = await Workbook.fromCSV(text, { sheetName: "Imported" });
  return book.worksheets.getItem("Imported").getUsedRange(true).values;
}

function writeMatrix(sheet, address, values) {
  const anchor = sheet.getRange(address);
  const range = anchor.resize(values.length, values[0].length);
  range.values = values;
  return range;
}

function styleDataSheet(sheet, usedRange, widths = {}) {
  sheet.showGridLines = false;
  sheet.freezePanes.freezeRows(1);
  usedRange.format = {
    font: { name: "Aptos", size: 10, color: "#17212B" },
    verticalAlignment: "center",
  };
  usedRange.getRow(0).format = {
    fill: "#17324D",
    font: { name: "Aptos", size: 10, bold: true, color: "#FFFFFF" },
    wrapText: true,
    verticalAlignment: "center",
  };
  usedRange.getRow(0).format.rowHeight = 34;
  usedRange.format.borders = {
    insideHorizontal: { style: "thin", color: "#DCE3EA" },
    bottom: { style: "thin", color: "#A8B5C2" },
  };
  for (const [column, width] of Object.entries(widths)) {
    sheet.getRange(`${column}:${column}`).format.columnWidth = width;
  }
}

const workbook = Workbook.create();
workbook.comments.setSelf({ displayName: "OpenDC-LCA" });

const readme = workbook.worksheets.add("Read Me");
readme.showGridLines = false;
readme.getRange("A1:H1").merge();
readme.getRange("A1").values = [["OpenDC-LCA integrated evidence workbook"]];
readme.getRange("A1:H1").format = {
  fill: "#17324D",
  font: { name: "Aptos Display", size: 20, bold: true, color: "#FFFFFF" },
  verticalAlignment: "center",
};
readme.getRange("A1:H1").format.rowHeight = 42;
readme.getRange("A3:B12").values = [
  ["Purpose", "Auditable synthesis of downloaded public and released evidence used in the manuscript."],
  ["Evidence boundary", "Released Microsoft/WSP results are reconstructed; eGRID re-basing is a screening scenario; Boavizta is a cross-product PCF synthesis; ÖKOBAUDAT comparisons are unit-process levers."],
  ["Functional unit", "Microsoft-derived results retain kg CO2e per Vcore-year. Server EPDs remain kg CO2e per server. Material factors remain per kg product. These units are not combined."],
  ["Microsoft/WSP", "https://doi.org/10.1038/s41586-025-08832-3"],
  ["Released model", "https://doi.org/10.5281/zenodo.14268168"],
  ["EPA eGRID 2023", "https://www.epa.gov/egrid/detailed-data"],
  ["Boavizta", "https://github.com/Boavizta/boaviztapi/tree/main/boaviztapi/data"],
  ["ÖKOBAUDAT", "https://www.oekobaudat.de/en/database/database-browser.html"],
  ["NOAA TMY", "https://www.ncei.noaa.gov/access/typical-meteorological-year/"],
  ["Important limitation", "GLAD/USLCI inventories and USGS watershed boundaries are catalogued but not converted into LCIA results without provider linking, impact methods, and water-scarcity characterization factors."],
];
readme.getRange("A3:A12").format = {
  fill: "#DCEAF4",
  font: { bold: true, color: "#17324D" },
  wrapText: true,
};
readme.getRange("B3:B12").format = { wrapText: true };
readme.getRange("A3:B12").format.borders = {
  insideHorizontal: { style: "thin", color: "#DCE3EA" },
  outside: { style: "thin", color: "#A8B5C2" },
};
readme.getRange("A:A").format.columnWidth = 24;
readme.getRange("B:B").format.columnWidth = 92;
readme.getRange("A3:B12").format.autofitRows();

const stateValues = await csvValues("table6_state_rebased_ghg.csv");
const states = workbook.worksheets.add("State Scenarios");
const stateRange = writeMatrix(states, "A1", stateValues);
styleDataSheet(states, stateRange, {
  A: 9, B: 12, C: 20, D: 18, E: 18, F: 18, G: 17, H: 19, I: 19, J: 18, K: 18, L: 48,
});
states.getRange(`D2:K${stateValues.length}`).format.numberFormat = "0.00";
states.getRange(`L2:L${stateValues.length}`).format.wrapText = true;
states.tables.add(`A1:L${stateValues.length}`, true, "StateScenarioTable").style =
  "TableStyleMedium2";

const crossoverValues = await csvValues("table8_crossover_thresholds.csv");
const crossover = workbook.worksheets.add("Crossovers");
const crossoverRange = writeMatrix(crossover, "A1", crossoverValues);
styleDataSheet(crossover, crossoverRange, {
  A: 18, B: 18, C: 18, D: 22, E: 22, F: 68,
});
crossover.getRange(`C2:D${crossoverValues.length}`).format.numberFormat = "0.00";
crossover.getRange(`F2:F${crossoverValues.length}`).format.wrapText = true;

const serverValues = await csvValues("table9_boavizta_server_records.csv");
const servers = workbook.worksheets.add("Server EPD Records");
const serverRange = writeMatrix(servers, "A1", serverValues);
styleDataSheet(servers, serverRange, {
  A: 15, B: 32, C: 15, D: 14, E: 17, F: 20, G: 20, H: 23, I: 55, J: 24,
});
servers.getRange(`D2:H${serverValues.length}`).format.numberFormat = "0.00";
servers.getRange(`I2:I${serverValues.length}`).format.wrapText = true;
servers.tables.add(`A1:J${serverValues.length}`, true, "ServerEPDTable").style =
  "TableStyleMedium4";

const materialValues = await csvValues("table11_material_decarbonization_levers.csv");
const materials = workbook.worksheets.add("Material Levers");
const materialRange = writeMatrix(materials, "A1", materialValues);
styleDataSheet(materials, materialRange, {
  A: 20, B: 30, C: 18, D: 45, E: 16, F: 45, G: 16, H: 16, I: 38, J: 38, K: 32, L: 65,
});
materials.getRange(`E2:H${materialValues.length}`).format.numberFormat = "0.00";
materials.getRange(`D2:D${materialValues.length}`).format.wrapText = true;
materials.getRange(`F2:F${materialValues.length}`).format.wrapText = true;
materials.getRange(`L2:L${materialValues.length}`).format.wrapText = true;

const pedigreeValues = await csvValues("table12_microsoft_pedigree_scores.csv");
const pedigree = workbook.worksheets.add("Pedigree Matrix");
const pedigreeRange = writeMatrix(pedigree, "A1", pedigreeValues);
styleDataSheet(pedigree, pedigreeRange, { A: 24, B: 24, C: 18, D: 40, E: 105 });
pedigree.getRange(`E2:E${pedigreeValues.length}`).format.wrapText = true;
pedigree.tables.add(`A1:E${pedigreeValues.length}`, true, "PedigreeTable").style =
  "TableStyleMedium2";

const priorityValues = await csvValues("table13_data_improvement_priority.csv");
const priorities = workbook.worksheets.add("Evidence Priorities");
const priorityRange = writeMatrix(priorities, "A1", priorityValues);
styleDataSheet(priorities, priorityRange, {
  A: 24, B: 20, C: 22, D: 23, E: 20, F: 25, G: 65,
});
priorities.getRange(`C2:F${priorityValues.length}`).format.numberFormat = "0.000";
priorities.getRange(`G2:G${priorityValues.length}`).format.wrapText = true;

const summary = workbook.worksheets.add("Key Results");
summary.showGridLines = false;
summary.getRange("A1:H1").merge();
summary.getRange("A1").values = [["What the integrated evidence changes"]];
summary.getRange("A1:H1").format = {
  fill: "#17324D",
  font: { name: "Aptos Display", size: 20, bold: true, color: "#FFFFFF" },
};
summary.getRange("A3:D3").values = [["Result", "Value", "Unit", "Interpretation"]];
summary.getRange("A4:D8").values = [
  ["Cold plate / one-phase crossover", crossoverValues[1][3], "kg CO2e/MWh", "Below this grid intensity, the released model favors cold plate; above it, one-phase immersion."],
  ["Observed eGRID state range", "23.70–893.08", "kg CO2e/MWh", "The crossover lies inside the observed 2023 U.S. state range."],
  ["Boavizta server manufacturing median", (await csvValues("table10_boavizta_server_summary.csv"))[1][5], "kg CO2e/server", "Public server PCFs vary substantially, making server inventory selection consequential."],
  ["EAF/high-scrap steel GWP reduction", materialValues[1][7], "%", "A large unit-process lever that cannot be propagated without facility quantities."],
  ["CEM III cement GWP reduction", materialValues[4][7], "%", "A second construction lever requiring a bill of materials."],
];
summary.getRange("A3:D3").format = {
  fill: "#17324D",
  font: { bold: true, color: "#FFFFFF" },
};
summary.getRange("A4:A8").format = { fill: "#DCEAF4", font: { bold: true } };
summary.getRange("A3:D8").format.borders = {
  insideHorizontal: { style: "thin", color: "#DCE3EA" },
  outside: { style: "thin", color: "#A8B5C2" },
};
summary.getRange("A:A").format.columnWidth = 35;
summary.getRange("B:B").format.columnWidth = 18;
summary.getRange("C:C").format.columnWidth = 18;
summary.getRange("D:D").format.columnWidth = 72;
summary.getRange("A3:D8").format.wrapText = true;
summary.getRange("A3:D8").format.autofitRows();
summary.getRange("B4:B8").format.numberFormat = "0.0";
const chartRows = [["Component", "Priority index (%)"]].concat(
  priorityValues.slice(1).map((row) => [row[0], 100 * Number(row[5])]),
);
writeMatrix(summary, "F3", chartRows);
summary.getRange(`F3:G${chartRows.length + 2}`).format = {
  font: { name: "Aptos", size: 9 },
};
summary.getRange("F3:G3").format = {
  fill: "#DCEAF4",
  font: { bold: true, color: "#17324D" },
};
summary.getRange(`G4:G${chartRows.length + 2}`).format.numberFormat = "0.0";
const priorityChart = summary.charts.add(
  "bar",
  summary.getRange(`F3:G${chartRows.length + 2}`),
);
priorityChart.title = "Highest-value evidence improvements";
priorityChart.hasLegend = false;
priorityChart.xAxis = { numberFormatCode: "0.0" };
priorityChart.setPosition("I2", "P20");

await fs.mkdir(previewDir, { recursive: true });
for (const sheetName of ["Read Me", "Key Results", "Evidence Priorities"]) {
  const preview = await workbook.render({
    sheetName,
    autoCrop: "all",
    scale: 1.5,
    format: "png",
  });
  await fs.writeFile(
    path.join(previewDir, `${sheetName.replaceAll(" ", "-").toLowerCase()}.png`),
    new Uint8Array(await preview.arrayBuffer()),
  );
}

const check = await workbook.inspect({
  kind: "table",
  range: "Key Results!A1:D8",
  include: "values,formulas",
  tableMaxRows: 10,
  tableMaxCols: 6,
});
console.log(check.ndjson);
const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
  summary: "final formula error scan",
});
console.log(errors.ndjson);
const blob = await SpreadsheetFile.exportXlsx(workbook);
await blob.save(output);
console.log(output);
