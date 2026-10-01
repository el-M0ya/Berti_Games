const fs = require('fs');

const allGames = JSON.parse(fs.readFileSync('all_games_consolidated.json', 'utf8'));
const gameData = JSON.parse(fs.readFileSync('game_data_cache.json', 'utf8'));

const platformNames = {
  ps1: 'PS1',
  ps2: 'PS2',
  ps3: 'PS3',
  psp: 'PSP',
  xbox360: 'XBOX360',
  ps4: 'PS4',
  ps5: 'PS5'
};

let totalGames = 0;
let gamesWithCovers = 0;
let gamesWithoutCovers = 0;

for (const platform of Object.keys(allGames)) {
  const varName = `${platformNames[platform]}_GAMES`;
  let output = `export const ${varName} = [\n`;
  
  for (const game of allGames[platform]) {
    const data = gameData[game.id] || {};
    
    // Use placeholder for missing covers
    const cover = data.cover || `https://via.placeholder.com/264x376?text=${encodeURIComponent(game.title.substring(0, 20))}`;
    
    if (data.cover) {
      gamesWithCovers++;
    } else {
      gamesWithoutCovers++;
    }
    totalGames++;
    
    output += '  {\n';
    output += `    id: '${game.id}',\n`;
    output += `    title: '${game.title.replace(/'/g, "\\'")}',\n`;
    output += `    year: ${data.year || null},\n`;
    output += `    cover: '${cover}',\n`;
    output += `    players: [${(data.players || ['1 jugador']).map(p => `'${p}'`).join(', ')}],\n`;
    output += `    genre: '${(data.genre || 'Variado').replace(/'/g, "\\'")}',\n`;
    output += `    description: '${(data.description || '').replace(/'/g, "\\'").replace(/\n/g, ' ')}',\n`;
    output += '  },\n';
  }
  
  output += '];\n';
  
  const fileName = `${platform}.js`;
  fs.writeFileSync(fileName, output);
  console.log(`Generated ${fileName} with ${allGames[platform].length} games`);
}

console.log(`\n=== SUMMARY ===`);
console.log(`Total games: ${totalGames}`);
console.log(`Games with covers: ${gamesWithCovers} (${(gamesWithCovers/totalGames*100).toFixed(1)}%)`);
console.log(`Games without covers: ${gamesWithoutCovers} (${(gamesWithoutCovers/totalGames*100).toFixed(1)}%)`);
