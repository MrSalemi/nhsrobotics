// The robotics project worksheet — one sheet per project, filled in by hand and
// shown with the running robot. V01
//
//   node worksheet.js                       -> Robotics_Project_Worksheet.pdf
//   node worksheet.js "Some Other Name.pdf"
//
// This script is the source. The PDF is output and there is no editable copy of
// the sheet anywhere, for the same reason no guide has one: an edit that is not
// here cannot survive the next run. Listed in extras.txt so build-all.sh remakes
// and deploys it with the guides.
//
// It is not built by ../builder — that makes guides, and this is a form: ruled
// write-on lines, checkbox glyphs, and answer space measured in blank lines.
// It borrows the builder's topdf.js to reach a PDF, and the builder's copy of
// the `docx` package rather than keeping a second one -- which is why the
// require below has a fallback.
//
// The wording and the boxes match what the worksheet has always said. The three
// Part B questions are deliberately the same on every project — being able to
// explain your code is how you show it is really yours. The scoring matches
// course.js: work 19, flex 20, late × 0.9, and a redo is 0 until it is complete.

const fs = require('fs');
const path = require('path');

let d;
try {
  d = require('docx');
} catch (e) {
  try {
    d = require(path.resolve(__dirname, '../shared/node_modules/docx'));
  } catch (e2) {
    console.error("cannot find the 'docx' package.");
    console.error("it comes with the builder:  ( cd ../shared && npm install )");
    process.exit(1);
  }
}

const {Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
       WidthType, AlignmentType, BorderStyle, ShadingType, VerticalAlign} = d;

const OUT = process.argv[2] || "Robotics_Project_Worksheet.pdf";

const PAGE_W = 12240, PAGE_H = 15840, MARGIN = 1080;
const W = PAGE_W - 2 * MARGIN;                    // 10080 dxa

const HAIR = {style: BorderStyle.SINGLE, size: 4, color: "808080"};
const EDGE = {style: BorderStyle.SINGLE, size: 8, color: "000000"};
const RULE = {style: BorderStyle.SINGLE, size: 6, color: "000000"};
const NONE = {style: BorderStyle.NONE, size: 0, color: "FFFFFF"};

const t = (text, o = {}) => new Paragraph({
  alignment: o.align || AlignmentType.LEFT,
  spacing: {before: o.before ?? 0, after: o.after ?? 0},
  children: [new TextRun({text, bold: !!o.bold, italics: !!o.italics,
                          size: o.size || 21, color: o.color || "000000"})],
});

// Lines for the student to write on.
//
// These are table rows, not bordered paragraphs. Word treats a run of adjacent
// paragraphs with identical borders as ONE bordered block and draws the rule
// once around the whole group, so four ruled paragraphs came out as a single
// line with a lot of space above it. Table rows cannot merge that way.
const answerLines = n => new Table({
  columnWidths: [W],
  width: {size: W, type: WidthType.DXA},
  borders: {top: NONE, bottom: NONE, left: NONE, right: NONE,
            insideHorizontal: NONE, insideVertical: NONE},
  rows: Array(n).fill(0).map(() => new TableRow({
    children: [new TableCell({
      width: {size: W, type: WidthType.DXA},
      borders: {top: NONE, left: NONE, right: NONE, bottom: RULE},
      margins: {top: 0, bottom: 0, left: 0, right: 0},
      children: [new Paragraph({
        spacing: {before: 170, after: 40},
        children: [new TextRun({text: "", size: 21})],
      })],
    })],
  })),
});

function cell(children, width, o = {}) {
  return new TableCell({
    width: {size: width, type: WidthType.DXA},
    verticalAlign: o.valign || VerticalAlign.CENTER,
    margins: {top: 80, bottom: 80, left: 130, right: 130},
    borders: o.borders || {top: HAIR, bottom: HAIR, left: EDGE, right: EDGE},
    ...(o.shade ? {shading: {type: ShadingType.CLEAR, fill: o.shade}} : {}),
    ...(o.span ? {columnSpan: o.span} : {}),
    children,
  });
}

const table = (widths, rows) => new Table({
  columnWidths: widths,
  width: {size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA},
  borders: {top: EDGE, bottom: EDGE, left: EDGE, right: EDGE,
            insideHorizontal: HAIR, insideVertical: HAIR},
  rows,
});

// A banner row: PART A / PART B.
const banner = label => table([W], [new TableRow({children: [
  cell([t(label, {bold: true, size: 24})], W, {shade: "D9D9D9"}),
]})]);

// A box to write code in. Four blank lines of monospace room.
const codeBox = () => table([W], [new TableRow({children: [
  cell([
    t("Code:", {size: 18, color: "595959"}),
    ...Array(4).fill(0).map(() => new Paragraph({
      spacing: {before: 120, after: 0},
      children: [new TextRun({text: "", font: "Roboto Mono", size: 20})],
    })),
  ], W, {valign: VerticalAlign.TOP}),
]})]);

// A fill-in line inside a borderless table, so the label and its rule sit on
// one row and the rule stops where the next label starts.
const fields = pairs => {
  const widths = pairs.map(p => p[1]);
  return new Table({
    columnWidths: widths,
    width: {size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA},
    borders: {top: NONE, bottom: NONE, left: NONE, right: NONE,
              insideHorizontal: NONE, insideVertical: NONE},
    rows: [new TableRow({children: pairs.map(([label, width]) => new TableCell({
      width: {size: width, type: WidthType.DXA},
      borders: {top: NONE, left: NONE, right: NONE, bottom: RULE},
      margins: {top: 60, bottom: 60, left: 0, right: 240},
      children: [t(label, {size: 22})],
    }))})],
  });
};

// One teacher-use column: the mark, and what it is worth.
const teacherCol = (mark, worth, width) => cell([
  new Paragraph({
    spacing: {after: 40},
    children: [new TextRun({text: "◇  ", size: 26}),
               new TextRun({text: mark, bold: true, size: 21})],
  }),
  t(worth, {size: 18, color: "404040"}),
], width);

// The two gates. In the sheet this came from they sat underneath the four score
// columns, which read as though "Explanations OK" belonged to Late and Redo.
// They are conditions on the whole sheet, so they get their own row.
const gate = (label, width) => cell([
  new Paragraph({
    children: [new TextRun({text: label + ":  ", size: 20}),
               new TextRun({text: "☐ yes    ☐ redo", size: 22})],
  }),
], width, {span: 2});

const doc = new Document({
  styles: {default: {document: {run: {font: "Calibri", size: 22}}}},
  sections: [{
    properties: {page: {size: {width: PAGE_W, height: PAGE_H},
                        margin: {top: MARGIN, bottom: MARGIN,
                                 left: MARGIN, right: MARGIN}}},
    children: [
      new Paragraph({
        spacing: {after: 60},
        children: [new TextRun({text: "🤖 NHS Robotics — Project Worksheet 🤖",
                                bold: true, size: 34})],
      }),
      t("Fill this out as you work. Show it with your running robot to get " +
        "checked off. One sheet per project.",
        {size: 21, color: "404040", after: 220}),

      fields([["Name", 6300], ["Class period", 3780]]),
      new Paragraph({text: "", spacing: {after: 80}}),
      fields([["Project #", 2100], ["Project name", 5040], ["Date", 2940]]),
      new Paragraph({text: "", spacing: {after: 240}}),

      // --- Teacher use ---------------------------------------------------
      table([W], [new TableRow({children: [
        cell([t("TEACHER USE ONLY", {bold: true, size: 19,
                                    align: AlignmentType.CENTER})],
             W, {shade: "D9D9D9"}),
      ]})]),
      table([2520, 2520, 2520, 2520], [
        new TableRow({children: [
          teacherCol("Flex", "20 pts (A+)", 2520),
          teacherCol("All Work", "19 pts (A)", 2520),
          teacherCol("Late", "grade × 0.9", 2520),
          teacherCol("Redo", "0 — not complete", 2520),
        ]}),
        new TableRow({children: [
          gate("Robot works", 5040),
          gate("Explanations OK", 5040),
        ]}),
      ]),
      new Paragraph({text: "", spacing: {after: 260}}),

      // --- Part A --------------------------------------------------------
      banner("PART A — YOUR CODE"),
      t("For each # WORK task, write the key line or lines of code that do the " +
        "real job, then explain in one sentence what the rest of that block " +
        "does. Add your flex code (plus a one-sentence explanation) if you " +
        "flexed. Keep going on the back if you need more room.",
        {size: 20, color: "404040", before: 160, after: 160}),

      ...["WORK 1", "WORK 2", "WORK 3"].flatMap(label => [
        t(label, {bold: true, size: 22, before: 160, after: 80}),
        codeBox(),
      ]),
      t("FLEX", {bold: true, size: 22, before: 160, after: 80}),
      codeBox(),

      // --- Part B --------------------------------------------------------
      new Paragraph({children: [], spacing: {before: 300}}),
      banner("PART B — EXPLAIN YOUR CODE"),
      t("Answer in your own words — full sentences. These are the same three " +
        "questions on every project, because being able to explain your code " +
        "is how you show it is really yours.",
        {size: 20, color: "404040", before: 160, after: 120}),

      t("1.  Pick one line from your code. What does it do, and why is it needed?",
        {bold: true, size: 21, before: 140}),
      answerLines(4),

      t("2.  Explain one decision you made — a value you chose, an if vs. elif, " +
        "a number you tuned — and why you made it.",
        {bold: true, size: 21, before: 260}),
      answerLines(4),

      t("3.  What was the hardest bug or problem you ran into, and how did you " +
        "fix it?",
        {bold: true, size: 21, before: 260}),
      answerLines(4),
    ],
  }],
});

// A PDF, not a Word file. The .docx is an intermediate in a temp folder and is
// deleted -- nothing an editor can open is left behind, so a typo fixed by hand
// cannot survive the next build. Same rule as the guides.
const {writePdf} = require(path.resolve(__dirname, '../shared/topdf.js'));
writePdf(doc, OUT, Packer);
