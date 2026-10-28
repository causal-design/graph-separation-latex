// Optional browser checks. Install Playwright outside this source tree, or set
// PLAYWRIGHT_MODULE to an existing installation. No network is needed by the page.
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const fs = require('node:fs');
const assert = require('node:assert/strict');
const path = require('node:path');

(async () => {
  const browser = await chromium.launch({headless: true,
    ...(process.env.CHROME_CHANNEL ? {channel: process.env.CHROME_CHANNEL} : {}),
    ...(process.env.CHROME_EXECUTABLE ? {executablePath: process.env.CHROME_EXECUTABLE} : {})});
  const reports = [];
  const prefix = process.env.ARTIFACT_PREFIX || 'preview';
  assert(/^[a-z0-9-]+$/.test(prefix));
  try {
    for (const width of [1280, 390]) {
      const page = await browser.newPage({viewport: {width, height: 1000}});
      const errors = [], failed = [];
      page.on('pageerror', e => errors.push(String(e)));
      page.on('console', m => {if (m.type() === 'error') errors.push(m.text());});
      page.on('response', r => {if (r.status() >= 400) failed.push(r.url());});
      await page.goto(process.env.REVIEW_URL || 'http://127.0.0.1:8766/preview/');
      await page.evaluate(() => MathJax.startup.promise);
      await page.waitForFunction(() => [...document.querySelectorAll('mjx-container image')]
        .every(i => i.getAttribute('href') || i.getAttribute('xlink:href')));
      const result = await page.evaluate(async () => {
        const images = [...document.querySelectorAll('mjx-container image')];
        const loaded = await Promise.all(images.map(i => new Promise(resolve => {
          const image = new Image();
          image.onload = () => resolve(image.naturalWidth > 0);
          image.onerror = () => resolve(false);
          image.src = i.getAttribute('href') || i.getAttribute('xlink:href');
        })));
        return {expressions: document.querySelectorAll('mjx-container').length,
          glyphs: images.length, loaded: loaded.filter(Boolean).length,
          mathErrors: document.querySelectorAll('[data-mml-node="merror"]').length,
          horizontalOverflow: document.documentElement.scrollWidth > innerWidth,
          imageSizes: images.map(i => ({width: i.getBoundingClientRect().width,
            height: i.getBoundingClientRect().height}))};
      });
      assert.equal(result.mathErrors, 0);
      assert(result.glyphs >= 18);
      assert.equal(result.loaded, result.glyphs);
      assert.equal(result.horizontalOverflow, false);
      assert.deepEqual(errors, []);
      assert.deepEqual(failed, []);
      const output = path.resolve(__dirname, '../build');
      await page.screenshot({path: `${output}/${prefix}-${width}.png`, fullPage: true});
      if (width === 1280) {
        await page.pdf({path: `${output}/${prefix}-print.pdf`, format: 'A4', printBackground: true});
      }
      reports.push({width, ...result});
      await page.close();
    }
    fs.writeFileSync(path.resolve(__dirname, `../build/${prefix}-browser-report.json`),
      JSON.stringify(reports, null, 2) + '\n');
    console.log(JSON.stringify(reports.map(({imageSizes, ...r}) => r), null, 2));
  } finally {
    await browser.close();
  }
})().catch(e => {console.error(e); process.exitCode = 1;});
