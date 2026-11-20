// Builds the press note for the 180th Annual Sports Meet as a Word document,
// following the layout of the college's own draft (plain, justified, blank spaces left to fill in).
// usage: node make_press_note.js out.docx
const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, AlignmentType, TabStopType } = require('docx');

const SIZE = 22; // 11 pt
const t = (text, o = {}) => new TextRun({ text, ...o });
const p = (children, o = {}) => new Paragraph({ children: typeof children === 'string' ? [t(children)] : children,
  alignment: AlignmentType.JUSTIFIED, spacing: { after: 160, line: 276 }, ...o });
const gap = n => Array.from({ length: n }, () => new Paragraph({ children: [] }));
const BLANK = '                              '; // space left to write in, as in the original
const sup = s => t(s, { superScript: true });
const place = (n, s) => [t(n), sup(s)];
// "1st ........ 1st" in two columns (Division B left, Division A right), like the original
const twoCol = (a, b) => new Paragraph({ tabStops: [{ type: TabStopType.LEFT, position: 4800 }],
  spacing: { after: 200 }, children: [...a, t('\t'), ...b] });
const oneCol = a => new Paragraph({ spacing: { after: 200 }, children: a });

const children = [
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 },
    children: [t('PRESS NOTE', { bold: true, underline: {} })] }),
  p("St. Peter’s College, Agra celebrates its 180th Annual Sports Meet – ‘INDIANA: The Symphony of Panchtatva’"),
  new Paragraph({ spacing: { after: 160 }, children: [t('Agra, November 21, 2026', { bold: true })] }),

  p("St. Peter’s College, Agra celebrated its 180th Annual Sports Meet, ‘INDIANA – The Symphony of Panchtatva’, on Saturday, November 21, 2026, at the college ground. Drawing inspiration from the five elements of nature – earth, water, fire, air and space – the afternoon brought together keenly fought athletic contests, spirited drills and vibrant cultural performances in a splendid celebration of sport, discipline and Indian heritage."),

  p("The Meet was presided over by the Most Rev. Dr. Raphy Manjaly, Archbishop of Agra and Patron of the College. The Chief Guest was Mr. Praveen Kumar, former Indian cricketer, and the Guest of Honour was the Most Rev. Dr. Albert D’Souza, Archbishop Emeritus of Agra. They were joined by the Manager, Rev. Fr. Ignatius Miranda; the Principal, Rev. Fr. (Dr.) Alwyn Pinto; the Vice-Principals, Rev. Fr. Louis Xess and Rev. Fr. Kulkant; members of the staff, parents and students."),

  p("The dignitaries were ceremonially led in by the college band, ‘The Legacy’. The programme commenced with a warm welcome of the guests, followed by the watering of a plant by the dignitaries – a symbol of growth and care for nature, in keeping with the theme of the Meet. A graceful prayer dance invoked blessings upon the day, after which the welcome speech was delivered. The President, the Chief Guest and the Guest of Honour were introduced and formally welcomed by Master Daksh Tandon. Master Zain Goyal introduced the President of the College, the Most Rev. Dr. Raphy Manjaly, and Rev. Fr. Ignatius Miranda welcomed His Grace with a sapling. Master Arihaan Tomar introduced the Chief Guest, Mr. Praveen Kumar, and the Principal, Rev. Fr. (Dr.) Alwyn Pinto, presented him with a bouquet as a token of love, respect and appreciation. Master Vardan Mark Walker introduced the Guest of Honour, the Most Rev. Dr. Albert D’Souza, and Rev. Fr. Louis Xess welcomed him with a sapling."),

  p("The ceremonial torch was borne by Master Labib Khan, winner of the cross-country race, accompanied by Master Niken Samuel, the Junior winner, and Master Ivaan Gandhi, the Primary winner. The College Principal presented the flags to the College Sports Captain and the Captains of the four Houses. A smart and well-coordinated March Past by the four Houses was followed by a Parade of students in the uniforms of the Navy, Boy Scouts, Rapid Action Force and NCC cadets. The Principal administered the oath to all the participants, and the Chief Guest declared the Meet open with the release of balloons to the music of the college band."),

  p("The track events – the 110 m hurdles, the 100 m, 200 m and 400 m races and the 4 × 100 m relay – were keenly contested across all divisions, with the young athletes displaying remarkable speed, stamina and determination. The hurdle race ‘Reach for the Stars’, presented by Classes I to V, proved to be a star attraction of the afternoon."),

  p("The cultural presentation by the Primary Section, ‘Tattvam: The Five Elements’, brought the theme of Panchtatva vividly to life, while the Mass P.T. display stood as a fine testament to the discipline and coordination of the students."),

  p("In his Presidential Address, the Most Rev. Dr. Raphy Manjaly –"),
  ...gap(7),
  p("He was felicitated with a sash and a memento by Rev. Fr. Ignatius Miranda (Manager). The Guest of Honour was felicitated with a sash and a memento by Rev. Fr. Kulkant (Vice-Principal)."),

  p("Addressing the gathering, the Chief Guest, Mr. Praveen Kumar, lauded the spirit of sportsmanship on display and congratulated the participants on their fine performances."),
  ...gap(4),
  p("He was felicitated with a sash and a memento by Rev. Fr. (Dr.) Alwyn Pinto (Principal)."),
  p(`The winners were honoured at the prize distribution, and the coveted Overall Championship Trophy was won by ${BLANK}House.`),

  p("The 110 m hurdles were contested in two divisions, B and A. The winners were:"),
  twoCol([t('Division B', { bold: true })], [t('Division A', { bold: true })]),
  twoCol(place('1', 'st'), place('1', 'st')),
  twoCol(place('2', 'nd'), place('2', 'nd')),
  twoCol(place('3', 'rd'), place('3', 'rd')),
  ...gap(1),
  p("In the 4 × 100 m relay race, the winners were:"),
  oneCol(place('1', 'st')), oneCol(place('2', 'nd')), oneCol(place('3', 'rd')),
  p(`In the cycle race, ${BLANK}${BLANK}stood first.`),
  p("In the Old Boys’ Race, the winners were:"),
  oneCol(place('1', 'st')), oneCol(place('2', 'nd')), oneCol(place('3', 'rd')),
  p(`${BLANK}${BLANK}won the Tug-of-War.`, { alignment: AlignmentType.LEFT }),

  p("The Vote of Thanks was followed by the Grand Finale dance, ‘Mission Courage’, a stirring tribute that brought the audience to its feet. The Meet concluded on a proud note with the National Anthem."),
  p("The successful organisation of the event was made possible through the dedicated efforts of the Sports Department, the teachers and the students of St. Peter’s College."),
];

const doc = new Document({
  styles: { default: { document: { run: { font: 'Calibri', size: SIZE } } } },
  sections: [{ properties: { page: { margin: { top: 1080, bottom: 1080, left: 1300, right: 1300 } } }, children }],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync(process.argv[2], b); console.log('ok'); });
