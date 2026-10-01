const fs = require('fs');

const API_KEY = '6d82f143e5fb405aa50dd8dc9a2bd900';
const BASE_URL = 'https://api.rawg.io/api';
const BATCH_SIZE = 500; // Process 500 games per run
const DELAY_MS = 150;

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function searchGame(title) {
  try {
    const searchTerm = encodeURIComponent(title);
    const url = `${BASE_URL}/games?key=${API_KEY}&search=${searchTerm}&page_size=3`;
    const response = await fetch(url);
    if (!response.ok) return null;
    const data = await response.json();
    if (data.results && data.results.length > 0) {
      return data.results[0];
    }
    return null;
  } catch (e) {
    return null;
  }
}

async function getGameDetails(gameId) {
  try {
    const url = `${BASE_URL}/games/${gameId}?key=${API_KEY}`;
    const response = await fetch(url);
    if (!response.ok) return null;
    return await response.json();
  } catch (e) {
    return null;
  }
}

function extractGenre(game) {
  if (game.genres && game.genres.length > 0) {
    return game.genres.map(g => g.name).join(', ');
  }
  return 'Variado';
}

function extractPlayers(game) {
  const tags = (game.tags || []).map(t => t.name.toLowerCase());
  const desc = (game.description || '').toLowerCase();
  
  const hasMultiplayer = tags.some(t => t.includes('multiplayer') || t.includes('co-op') || t.includes('coop'));
  const descMentions2 = desc.includes('2 player') || desc.includes('two player') || desc.includes('2-player');
  const descMentions4 = desc.includes('4 player') || desc.includes('four player') || desc.includes('4-player');
  
  if (hasMultiplayer || descMentions4) {
    return ['1 jugador', '2 jugadores', '4 jugadores'];
  } else if (descMentions2) {
    return ['1 jugador', '2 jugadores'];
  }
  
  return ['1 jugador'];
}

function extractCover(game) {
  if (game.background_image) {
    return game.background_image;
  }
  return null;
}

function extractYear(game) {
  if (game.released) {
    const year = parseInt(game.released.split('-')[0]);
    if (!isNaN(year) && year > 1980 && year < 2030) {
      return year;
    }
  }
  return null;
}

function extractDescription(game) {
  if (game.description) {
    let desc = game.description.replace(/<[^>]*>/g, '').trim();
    if (desc.length > 300) {
      desc = desc.substring(0, 297) + '...';
    }
    return desc;
  }
  return null;
}

async function processBatch() {
  const allGames = JSON.parse(fs.readFileSync('all_games_consolidated.json', 'utf8'));
  const progress = JSON.parse(fs.readFileSync('game_data_cache.json', 'utf8'));
  
  // Find unprocessed games
  const unprocessed = [];
  for (const platform of Object.keys(allGames)) {
    for (const game of allGames[platform]) {
      if (!progress[game.id]) {
        unprocessed.push({ platform, game });
      }
    }
  }
  
  console.log(`Total unprocessed: ${unprocessed.length}`);
  
  if (unprocessed.length === 0) {
    console.log('All games processed! Generating JS files...');
    generateJSFiles();
    return;
  }
  
  // Process batch
  const batch = unprocessed.slice(0, BATCH_SIZE);
  console.log(`Processing batch of ${batch.length} games...`);
  
  for (let i = 0; i < batch.length; i++) {
    const { game } = batch[i];
    
    const searchResult = await searchGame(game.title);
    await sleep(DELAY_MS);
    
    if (searchResult) {
      const details = await getGameDetails(searchResult.id);
      await sleep(DELAY_MS);
      
      const gameData = details || searchResult;
      
      progress[game.id] = {
        year: extractYear(gameData),
        cover: extractCover(gameData),
        players: extractPlayers(gameData),
        genre: extractGenre(gameData),
        description: extractDescription(gameData)
      };
    } else {
      progress[game.id] = {
        year: null,
        cover: null,
        players: ['1 jugador'],
        genre: 'Variado',
        description: null
      };
    }
    
    if ((i + 1) % 50 === 0) {
      console.log(`  [${i + 1}/${batch.length}] ${game.title}`);
      fs.writeFileSync('game_data_cache.json', JSON.stringify(progress, null, 2));
    }
  }
  
  // Save final progress
  fs.writeFileSync('game_data_cache.json', JSON.stringify(progress, null, 2));
  console.log(`Batch complete! Total cached: ${Object.keys(progress).length}`);
  
  // If there are more games, suggest running again
  if (unprocessed.length > BATCH_SIZE) {
    console.log(`\nRun again to process next batch (${unprocessed.length - BATCH_SIZE} remaining)`);
  } else {
    console.log('\nAll games processed! Generating JS files...');
    generateJSFiles();
  }
}

function generateJSFiles() {
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
  
  for (const platform of Object.keys(allGames)) {
    const varName = `${platformNames[platform]}_GAMES`;
    let output = `export const ${varName} = [\n`;
    
    for (const game of allGames[platform]) {
      const data = gameData[game.id] || {};
      
      output += '  {\n';
      output += `    id: '${game.id}',\n`;
      output += `    title: '${game.title.replace(/'/g, "\\'")}',\n`;
      output += `    year: ${data.year || null},\n`;
      output += `    cover: '${data.cover || ''}',\n`;
      output += `    players: [${(data.players || ['1 jugador']).map(p => `'${p}'`).join(', ')}],\n`;
      output += `    genre: '${(data.genre || 'Variado').replace(/'/g, "\\'")}',\n`;
      output += `    description: '${(data.description || '').replace(/'/g, "\\'")}',\n`;
      output += '  },\n';
    }
    
    output += '];\n';
    
    const fileName = `${platform}.js`;
    fs.writeFileSync(fileName, output);
    console.log(`Generated ${fileName} with ${allGames[platform].length} games`);
  }
}

processBatch().catch(err => {
  console.error('Error:', err);
  process.exit(1);
});
