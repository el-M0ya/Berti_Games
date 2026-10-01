const fs = require('fs');
const path = require('path');

// Read all JSON files
const files = ['game_scan.json', 'game_scan_ps4.json', 'ps3.json', 'ps5.json', 'xbox360.json', 'xbox360_2.json'];
const allGames = {};

files.forEach(f => {
  const data = JSON.parse(fs.readFileSync(f, 'utf8'));
  Object.keys(data).forEach(console_key => {
    if (!allGames[console_key]) allGames[console_key] = [];
    allGames[console_key].push(...data[console_key]);
  });
});

// Count games per platform
console.log('Games per platform:');
Object.keys(allGames).forEach(k => {
  console.log(`  ${k}: ${allGames[k].length}`);
});
console.log(`  TOTAL: ${Object.values(allGames).reduce((a, b) => a + b.length, 0)}`);

// Deduplicate by id within each platform
Object.keys(allGames).forEach(console_key => {
  const seen = new Set();
  allGames[console_key] = allGames[console_key].filter(g => {
    if (seen.has(g.id)) return false;
    seen.add(g.id);
    return true;
  });
});

console.log('\nAfter deduplication:');
Object.keys(allGames).forEach(k => {
  console.log(`  ${k}: ${allGames[k].length}`);
});
console.log(`  TOTAL: ${Object.values(allGames).reduce((a, b) => a + b.length, 0)}`);

// Save consolidated data
fs.writeFileSync('all_games_consolidated.json', JSON.stringify(allGames, null, 2));
console.log('\nSaved to all_games_consolidated.json');
