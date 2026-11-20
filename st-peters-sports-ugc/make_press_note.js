// Builds the press note for the 180th Annual Sports Meet as a Word document.
// usage: node make_press_note.js out.docx
const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, AlignmentType,
  BorderStyle, ShadingType } = require('docx');

const FONT = 'Calibri';
const NAVY = '1F2A4A', MAROON = '8C2226';

// text helper: segments are strings, {b:'bold'}, {i:'italic'} or {blank:'label'} (yellow fill-in)
function runs(parts) {
  return parts.map(p => {
    if (typeof p === 'string') return new TextRun(p);
    if (p.b) return new TextRun({ text: p.b, bold: true });
    if (p.i) return new TextRun({ text: p.i, italics: true });
    if (p.blank) return new TextRun({ text: `[${p.blank}]`, highlight: 'yellow' });
  });
}
const para = (parts, opts = {}) => new Paragraph({ children: runs(parts), alignment: AlignmentType.JUSTIFIED,
  spacing: { after: 160, line: 300 }, ...opts });
const sub = t => new Paragraph({ children: [new TextRun({ text: t, bold: true, color: NAVY, size: 24 })],
  spacing: { before: 200, after: 80 }, keepNext: true });

const B = { style: BorderStyle.SINGLE, size: 4, color: 'BFC5D2' };
const borders = { top: B, bottom: B, left: B, right: B };
function cell(text, w, head = false, blank = false) {
  return new TableCell({ width: { size: w, type: WidthType.DXA }, borders,
    shading: head ? { type: ShadingType.CLEAR, color: 'auto', fill: 'E8ECF4' } : undefined,
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    children: [new Paragraph({ children: blank ? [new TextRun({ text: '[name / House]', highlight: 'yellow' })]
      : [new TextRun({ text, bold: head })] })] });
}
const widths = [2426, 2200, 2200, 2200]; // 9026 total
function resultsTable(rows) {
  return new Table({ width: { size: 9026, type: WidthType.DXA }, columnWidths: widths, rows: [
    new TableRow({ tableHeader: true, children: ['Event', '1st', '2nd', '3rd'].map((h, i) => cell(h, widths[i], true)) }),
    ...rows.map(r => new TableRow({ children: [cell(r[0], widths[0]), ...[1, 2, 3].map(i =>
      r[i] === '-' ? cell('–', widths[i]) : cell('', widths[i], false, true))] })),
  ] });
}

const children = [
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240 },
    children: [new TextRun({ text: 'PRESS NOTE', bold: true, size: 30, color: MAROON, characterSpacing: 60 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 },
    children: [new TextRun({ text: "St. Peter's College, Agra Celebrates its 180th Annual Sports Meet, ‘INDIANA – The Symphony of Panchtatva’",
      bold: true, size: 32, color: NAVY })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 300 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: MAROON, space: 8 } },
    children: [new TextRun({ text: 'Former Indian cricketer Mr. Praveen Kumar graces the occasion as Chief Guest', italics: true, size: 24 })] }),

  para([{ b: 'Agra, November 21, 2026: ' }, "St. Peter's College, Agra celebrated its 180th Annual Sports Meet, ‘INDIANA – The Symphony of Panchtatva’, on Saturday, November 21, 2026, at the college ground. Inspired by the five elements of nature (earth, water, fire, air and space), the afternoon wove together keenly fought athletic contests, spirited drills and vibrant cultural performances in a grand celebration of sport, discipline and Indian heritage."]),
  para(['The Meet was presided over by the Most Rev. Dr. Raphy Manjaly, Archbishop of Agra and Patron of the College. The Chief Guest was Mr. Praveen Kumar, former Indian cricketer, and the Guest of Honour was the Most Rev. Dr. Albert D’Souza, Archbishop Emeritus of Agra. They were joined by the Manager, Rev. Fr. Ignatius Miranda; the Principal, Rev. Fr. (Dr.) Alwyn Pinto; the Vice-Principals, Rev. Fr. Louis Xess and Rev. Fr. Kulkant; and members of staff, parents and students.']),
  para(['The dignitaries were led in by the college band, ‘The Legacy’. The programme opened with a warm welcome, followed by the watering of a plant by the dignitaries, a symbol of growth and care for nature in keeping with the theme of the Meet. A graceful prayer dance invoked blessings on the day, after which the welcome speech was delivered. Master Daksh Tandon extended a formal welcome to the President, the Chief Guest and the Guest of Honour. Master Zain Goyal introduced the President, the Most Rev. Dr. Raphy Manjaly, and Rev. Fr. Ignatius Miranda welcomed His Grace with a sapling. Master Arihaan Tomar introduced the Chief Guest, Mr. Praveen Kumar, and the Principal, Rev. Fr. (Dr.) Alwyn Pinto, presented him with a bouquet as a token of respect and appreciation. Master Vardan Mark Walker introduced the Guest of Honour, the Most Rev. Dr. Albert D’Souza, and Rev. Fr. Louis Xess welcomed him with a sapling.']),
  para(['The ceremonial torch was carried in by Master Labib Khan, winner of the cross-country race, along with Master Niken Samuel (Junior winner) and Master Ivaan Gandhi (Primary winner), and the Meet Flame was lit. The Principal presented the flags to the College Sports Captain and the Captains of the four Houses. A well-coordinated March Past by the four Houses was followed by a Parade of students in the uniforms of the Navy, Boy Scouts, Rapid Action Force and NCC. The Principal administered the oath to all participants, and the Chief Guest declared the Meet open with the release of balloons to the music of the college band.']),
  para(['The track events (the 110 m hurdles, the 100 m, 200 m and 400 m races and the 4 × 100 m relay) were keenly contested across all divisions, with the young athletes displaying remarkable speed, stamina and determination. The hurdle race ‘Reach for the Stars’, by students of Classes I to V, was a star attraction of the afternoon.']),
  para(['The cultural presentation by the Primary Section, ‘Tattvam: The Five Elements’, brought the theme of Panchtatva vividly to life, while the Mass P.T. display was a fine showcase of the discipline and coordination of the students.']),
  para(['In his Presidential Address, the Most Rev. Dr. Raphy Manjaly ', { blank: 'summary of the Presidential Address' }, '. He was felicitated with a sash and a memento by Rev. Fr. Ignatius Miranda (Manager). The Guest of Honour was felicitated with a sash and a memento by Rev. Fr. Kulkant (Vice-Principal).']),
  para(['Addressing the gathering, the Chief Guest, Mr. Praveen Kumar, lauded the spirit of sportsmanship on display and congratulated the participants. ', { blank: 'optional: one line from his speech' }, ' He was felicitated with a sash and a memento by Rev. Fr. (Dr.) Alwyn Pinto (Principal).']),
  para(['The winners were honoured at the prize distribution, and the coveted Overall Championship Trophy was won by ', { blank: 'House name' }, ' House.']),

  sub('Results'),
  resultsTable([
    ['110 m Hurdles – Division A'], ['110 m Hurdles – Division B'], ['4 × 100 m Relay'],
    ['Cycle Race', '', '-', '-'], ["Old Boys' Race"], ['Tug-of-War', '', '-', '-'],
  ]),
  new Paragraph({ spacing: { after: 160 }, children: [] }),

  para(['The Vote of Thanks was followed by the Grand Finale dance, ‘Mission Courage’, a stirring tribute that brought the audience to its feet. The Meet concluded with the National Anthem.']),
  para(["The successful organisation of the event was made possible by the dedicated efforts of the Sports Department, the teachers and the students of St. Peter's College."]),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 240 }, children: [new TextRun({ text: '###', bold: true })] }),
];

const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: 23 } } } },
  sections: [{ properties: { page: { margin: { top: 1300, bottom: 1300, left: 1440, right: 1440 } } }, children }],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync(process.argv[2], b); console.log('ok'); });
