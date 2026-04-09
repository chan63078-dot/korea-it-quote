// build.js — 엑셀 템플릿을 base64로 인코딩해서 index.html에 주입
const fs = require('fs');
const path = require('path');

const templatePath = path.join(__dirname, '..', '견적서_양식.xlsx');
const htmlPath = path.join(__dirname, 'index.html');

if (!fs.existsSync(templatePath)) {
  console.error('견적서_양식.xlsx 파일을 찾을 수 없습니다:', templatePath);
  process.exit(1);
}

const b64 = fs.readFileSync(templatePath).toString('base64');
let html = fs.readFileSync(htmlPath, 'utf8');

if (!html.includes("'@@TEMPLATE@@'")) {
  console.error("index.html에 '@@TEMPLATE@@' 플레이스홀더가 없습니다.");
  process.exit(1);
}

html = html.replace("'@@TEMPLATE@@'", `'${b64}'`);
fs.writeFileSync(htmlPath, html, 'utf8');
console.log(`완료: 템플릿 ${Math.round(b64.length * 0.75 / 1024)}KB 주입됨`);
