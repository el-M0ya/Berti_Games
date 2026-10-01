const fs = require('fs');
const path = require('path');

const API_KEY = '6d82f143e5fb405aa50dd8dc9a2bd900';
const BASE_URL = 'https://api.rawg.io/api';
const DELAY_MS = 200; // Rate limit: ~5 requests per second max

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function searchGame(title) {
  try {
    const searchTerm = encodeURIComponent(title);
    const url = `${BASE_URL}/games?key=${API_KEY}&search=${searchTerm}&page_size=5`;
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
  // RAWG doesn't have direct player count, estimate from tags/description
  const tags = (game.tags || []).map(t => t.name.toLowerCase());
  const desc = (game.description || '').toLowerCase();
  
  // Check for multiplayer indicators
  const hasMultiplayer = tags.some(t => t.includes('multiplayer') || t.includes('co-op') || t.includes('coop'));
  const hasSinglePlayer = tags.some(t => t.includes('singleplayer') || t.includes('single-player'));
  
  // Check description for player count
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
    // Clean HTML tags
    let desc = game.description.replace(/<[^>]*>/g, '').trim();
    // Truncate if too long
    if (desc.length > 300) {
      desc = desc.substring(0, 297) + '...';
    }
    return desc;
  }
  return null;
}

async function processGames() {
  const allGames = JSON.parse(fs.readFileSync('all_games_consolidated.json', 'utf8'));
  
  // Load existing progress if any
  let progress = {};
  if (fs.existsSync('game_data_cache.json')) {
    progress = JSON.parse(fs.readFileSync('game_data_cache.json', 'utf8'));
  }
  
  const platforms = Object.keys(allGames);
  let totalProcessed = 0;
  let totalGames = 0;
  
  platforms.forEach(p => { totalGames += allGames[p].length; });
  
  console.log(`Processing ${totalGames} games across ${platforms.length} platforms...`);
  
  for (const platform of platforms) {
    console.log(`\n=== Processing ${platform} (${allGames[platform].length} games) ===`);
    
    for (let i = 0; i < allGames[platform].length; i++) {
      const game = allGames[platform][i];
      totalProcessed++;
      
      // Skip if already processed
      if (progress[game.id]) {
        if (totalProcessed % 100 === 0) {
          console.log(`  [${totalProcessed}/${totalGames}] ${game.title} (cached)`);
        }
        continue;
      }
      
      // Search for game in RAWG
      const searchResult = await searchGame(game.title);
      await sleep(DELAY_MS);
      
      if (searchResult) {
        // Get full details
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
        // Game not found in RAWG
        progress[game.id] = {
          year: null,
          cover: null,
          players: ['1 jugador'],
          genre: 'Variado',
          description: null
        };
      }
      
      if (totalProcessed % 50 === 0) {
        console.log(`  [${totalProcessed}/${totalGames}] ${game.title}`);
        // Save progress every 50 games
        fs.writeFileSync('game_data_cache.json', JSON.stringify(progress, null, 2));
      }
    }
    
    // Save progress after each platform
    fs.writeFileSync('game_data_cache.json', JSON.stringify(progress, null, 2));
    console.log(`  Completed ${platform}`);
  }
  
  // Final save
  fs.writeFileSync('game_data_cache.json', JSON.stringify(progress, null, 2));
  console.log(`\nDone! Processed ${totalProcessed} games.`);
  
  return progress;
}

processGames().then(() => {
  console.log('Generating JS files...');
  generateJSFiles();
}).catch(err => {
  console.error('Error:', err);
});

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
