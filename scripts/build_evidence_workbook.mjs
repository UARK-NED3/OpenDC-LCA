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
  ["Evidence boundary", "Released Microsoft/WSP results are reconstructed; eGRID is used only as a numerical intensity index across non-equivalent lifecycle boundaries; Boavizta is a cross-product PCF synthesis; ÖKOBAUDAT comparisons are unit-process levers."],
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
  A: 9, B: 12, C: 12, D: 18, E: 18, F: 18, G: 17, H: 27, I: 42, J: 17, K: 18, L: 18, M: 18, N: 18, O: 18, P: 58,
});
states.getRange(`D2:G${stateValues.length}`).format.numberFormat = "0.00";
states.getRange(`K2:O${stateValues.length}`).format.numberFormat = "0.00";
states.getRange(`H2:I${stateValues.length}`).format.wrapText = true;
states.getRange(`P2:P${stateValues.length}`).format.wrapText = true;
states.tables.add(`A1:P${stateValues.length}`, true, "StateScenarioTable").style =
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

const historicalValues = await csvValues("table15_egrid_historical_national_factors.csv");
const historical = workbook.worksheets.add("Historical eGRID");
const historicalRange = writeMatrix(historical, "A1", historicalValues);
styleDataSheet(historical, historicalRange, {
  A: 10, B: 14, C: 20, D: 22, E: 22, F: 22, G: 22, H: 22, I: 32,
  J: 22, K: 22, L: 20, M: 20, N: 28, O: 70, P: 18, Q: 18, R: 18,
});
historical.getRange(`C2:G${historicalValues.length}`).format.numberFormat = "0.00";
historical.getRange(`J2:M${historicalValues.length}`).format.numberFormat = "0.00";
historical.getRange(`P2:R${historicalValues.length}`).format.numberFormat = "0.00";
historical.getRange(`H2:I${historicalValues.length}`).format.wrapText = true;
historical.getRange(`N2:O${historicalValues.length}`).format.wrapText = true;
historical.tables.add(`A1:R${historicalValues.length}`, true, "HistoricalEgridTable").style =
  "TableStyleMedium2";

const anchorValues = await csvValues("table21_anchor_extrapolation_diagnostic.csv");
const anchors = workbook.worksheets.add("Anchor Coverage");
const anchorRange = writeMatrix(anchors, "A1", anchorValues);
styleDataSheet(anchors, anchorRange, {
  A: 18, B: 12, C: 19, D: 20, E: 19, F: 18, G: 18, H: 23, I: 23, J: 75,
});
anchors.getRange(`B2:I${anchorValues.length}`).format.numberFormat = "0.00";
anchors.getRange(`J2:J${anchorValues.length}`).format.wrapText = true;
anchors.tables.add(`A1:J${anchorValues.length}`, true, "AnchorCoverageTable").style =
  "TableStyleMedium2";

const boundaryValues = await csvValues("table22_boundary_mismatch_stress.csv");
const boundary = workbook.worksheets.add("Boundary Stress");
const boundaryRange = writeMatrix(boundary, "A1", boundaryValues);
styleDataSheet(boundary, boundaryRange, {
  A: 24, B: 16, C: 22, D: 22, E: 20, F: 18, G: 20, H: 20, I: 22, J: 75,
});
boundary.getRange(`A2:I${boundaryValues.length}`).format.numberFormat = "0.00";
boundary.getRange(`J2:J${boundaryValues.length}`).format.wrapText = true;
boundary.tables.add(`A1:J${boundaryValues.length}`, true, "BoundaryStressTable").style =
  "TableStyleMedium4";

const jointValues = await csvValues("table23_joint_assumption_stress.csv");
const joint = workbook.worksheets.add("Joint Stress");
const jointRange = writeMatrix(joint, "A1", jointValues);
styleDataSheet(joint, jointRange, {
  A: 24, B: 21, C: 15, D: 14, E: 18, F: 20, G: 20, H: 23, I: 18,
  J: 21, K: 26, L: 24, M: 14, N: 76,
});
joint.getRange(`B2:M${jointValues.length}`).format.numberFormat = "0.00";
joint.getRange(`D2:D${jointValues.length}`).format.numberFormat = "#,##0";
joint.getRange(`M2:M${jointValues.length}`).format.numberFormat = "0";
joint.getRange(`N2:N${jointValues.length}`).format.wrapText = true;
joint.tables.add(`A1:N${jointValues.length}`, true, "JointStressTable").style =
  "TableStyleMedium4";

const functionalValues = await csvValues("table24_functional_unit_sensitivity.csv");
const functional = workbook.worksheets.add("Functional Unit");
const functionalRange = writeMatrix(functional, "A1", functionalValues);
styleDataSheet(functional, functionalRange, {
  A: 18, B: 12, C: 25, D: 25, E: 25, F: 25, G: 25, H: 80,
});
functional.getRange(`B2:G${functionalValues.length}`).format.numberFormat = "0.00";
functional.getRange(`H2:H${functionalValues.length}`).format.wrapText = true;
functional.tables.add(`A1:H${functionalValues.length}`, true, "FunctionalUnitTable").style =
  "TableStyleMedium2";

const priorityRobustnessValues = await csvValues("table25_priority_index_sensitivity.csv");
const priorityRobustness = workbook.worksheets.add("Priority Robustness");
const priorityRobustnessRange = writeMatrix(priorityRobustness, "A1", priorityRobustnessValues);
styleDataSheet(priorityRobustness, priorityRobustnessRange, {
  A: 22, B: 20, C: 20, D: 18, E: 14, F: 14, G: 14, H: 80,
});
priorityRobustness.getRange(`B2:G${priorityRobustnessValues.length}`).format.numberFormat =
  "0.00";
priorityRobustness.getRange(`H2:H${priorityRobustnessValues.length}`).format.wrapText = true;
priorityRobustness.tables.add(
  `A1:H${priorityRobustnessValues.length}`,
  true,
  "PriorityRobustnessTable",
).style = "TableStyleMedium2";

const summary = workbook.worksheets.add("Key Results");
summary.showGridLines = false;
summary.getRange("A1:H1").merge();
summary.getRange("A1").values = [["What the integrated evidence changes"]];
summary.getRange("A1:H1").format = {
  fill: "#17324D",
  font: { name: "Aptos Display", size: 20, bold: true, color: "#FFFFFF" },
};
summary.getRange("A3:D3").values = [["Result", "Value", "Unit", "Interpretation"]];
const serverSummaryValues = await csvValues("table10_boavizta_server_summary.csv");
const stateFactors = stateValues.slice(1).map((row) => Number(row[4]));
const us2012 = historicalValues.find((row) => Number(row[0]) === 2012);
const us2023 = historicalValues.find((row) => Number(row[0]) === 2023);
const gridDeclinePct =
  (100 * (Number(us2012[3]) - Number(us2023[3]))) / Number(us2012[3]);
const allAnchorRow = anchorValues.find((row) => row[0] === "all state-years");
const usNarrowTwoPhase = jointValues.find(
  (row) =>
    row[0] === "2023 U.S. generation" &&
    row[2] === "narrow" &&
    row[8] === "Two-phase",
);
const usWideTwoPhase = jointValues.find(
  (row) =>
    row[0] === "2023 U.S. generation" &&
    row[2] === "wide" &&
    row[8] === "Two-phase",
);
const fu2023 = functionalValues.find((row) => row[0] === "2023 states/DC");
const steelLever = materialValues.find((row) => row[0] === "Steel route");
const cementLever = materialValues.find((row) => row[0] === "Cement chemistry");
summary.getRange("A4:D13").values = [
  ["Cold plate / one-phase crossover", crossoverValues[1][3], "kg CO2e/MWh", "A conditional decision boundary in the numerical intensity-index screen, not a state-specific process LCA."],
  ["Observed 2023 state/DC range", `${Math.min(...stateFactors).toFixed(2)}–${Math.max(...stateFactors).toFixed(2)}`, "kg CO2e/MWh", "The crossover lies inside the annual production-factor range, but boundary mismatch constrains interpretation."],
  ["Harmonized U.S. grid decline, 2012–2023", gridDeclinePct, "%", "Direct CO2, CH4 and N2O reconstruction on one AR5 basis avoids mixing provider GWP conventions."],
  ["State-years outside released anchors", allAnchorRow[6], "%", "Extrapolation is explicit: 137 of 459 state-year factors lie outside the two released electricity endpoints."],
  ["Two-phase first rank, narrow stress", usNarrowTwoPhase[9], "% of trials", "Seeded assumption-stress frequency; not a fitted probability."],
  ["Two-phase first rank, wide stress", usWideTwoPhase[9], "% of trials", "The nominal ranking becomes conditional under broad joint perturbations."],
  ["Two-phase adverse service correction", fu2023[4], "%", "Median increase in impact per equivalent useful computation needed to lose first rank in 2023."],
  ["Boavizta server manufacturing median", serverSummaryValues[1][5], "kg CO2e/server", "Public server PCFs vary substantially, making server inventory selection consequential."],
  ["EAF/high-scrap steel GWP reduction", steelLever[7], "%", "A large unit-process lever that cannot be propagated without facility quantities."],
  ["Cement chemistry GWP reduction", cementLever[7], "%", "A construction-material lever requiring a disclosed bill of materials."],
];
summary.getRange("A3:D3").format = {
  fill: "#17324D",
  font: { bold: true, color: "#FFFFFF" },
};
summary.getRange("A4:A13").format = { fill: "#DCEAF4", font: { bold: true } };
summary.getRange("A3:D13").format.borders = {
  insideHorizontal: { style: "thin", color: "#DCE3EA" },
  outside: { style: "thin", color: "#A8B5C2" },
};
summary.getRange("A:A").format.columnWidth = 35;
summary.getRange("B:B").format.columnWidth = 18;
summary.getRange("C:C").format.columnWidth = 18;
summary.getRange("D:D").format.columnWidth = 72;
summary.getRange("A3:D13").format.wrapText = true;
summary.getRange("A3:D13").format.autofitRows();
summary.getRange("B4:B13").format.numberFormat = "0.0";
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
summary.getRange("F:F").format.columnWidth = 24;
summary.getRange("G:G").format.columnWidth = 18;
const priorityChart = summary.charts.add(
  "bar",
  summary.getRange(`F3:G${chartRows.length + 2}`),
);
priorityChart.title = "Highest-value evidence improvements";
priorityChart.hasLegend = false;
priorityChart.xAxis = { numberFormatCode: "0.0" };
priorityChart.setPosition("I2", "P22");

await fs.mkdir(previewDir, { recursive: true });
for (const sheetName of [
  "Read Me",
  "State Scenarios",
  "Crossovers",
  "Server EPD Records",
  "Material Levers",
  "Pedigree Matrix",
  "Evidence Priorities",
  "Historical eGRID",
  "Anchor Coverage",
  "Boundary Stress",
  "Joint Stress",
  "Functional Unit",
  "Priority Robustness",
  "Key Results",
]) {
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
  range: "Key Results!A1:D13",
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
