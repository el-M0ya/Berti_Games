const fs = require('fs');

// Multiple cover sources
const SOURCES = {
  // RAWG CDN patterns
  rawg: {
    cover: (gameId) => `https://media.rawg.io/media/games/${gameId}/${gameId}.jpg`,
    screenshot: (gameId) => `https://media.rawg.io/media/screenshots/${gameId}/${gameId}.jpg`,
  },
  
  // IGDB cover patterns (requires API)
  igdb: {
    cover: (imageId) => `https://images.igdb.com/igdb/image/upload/t_cover_big/${imageId}.jpg`,
  },
  
  // Giant Bomb (requires API)
  giantBomb: {
    cover: (gameId) => `https://www.giantbomb.com/a/uploads/original/${gameId}.jpg`,
  },
};

// Try to get cover from RAWG game details
async function getRAWGCover(gameId) {
  try {
    const API_KEY = '6d82f143e5fb405aa50dd8dc9a2bd900';
    const url = `https://api.rawg.io/api/games/${gameId}?key=${API_KEY}`;
    const response = await fetch(url);
    if (!response.ok) return null;
    const data = await response.json();
    
    // Try different cover fields
    if (data.background_image) return data.background_image;
    if (data.background_image_additional) return data.background_image_additional;
    
    return null;
  } catch (e) {
    return null;
  }
}

// Search for cover using Google Custom Search (requires API key)
async function searchGoogleCover(title) {
  try {
    // This would require Google Custom Search API key
    // For now, return null
    return null;
  } catch (e) {
    return null;
  }
}

// Generate cover URL from title using various patterns
function generateCoverUrl(title, platform) {
  const cleanTitle = title.toLowerCase()
    .replace(/[^a-z0-9\s]/g, '')
    .replace(/\s+/g, '-');
  
  // Try different URL patterns
  const patterns = [
    `https://images.igdb.com/igdb/image/upload/t_cover_big/${cleanTitle}.jpg`,
    `https://static-cdn.jtvnw.net/ttv-boxart/${cleanTitle}.jpg`,
    `https://cdn.cloudflare.steamstatic.com/steam/apps/${cleanTitle}/header.jpg`,
  ];
  
  return patterns[0];
}

// Main function to fetch covers from multiple sources
async function fetchCovers() {
  const gameData = JSON.parse(fs.readFileSync('game_data_cache.json', 'utf8'));
  const allGames = JSON.parse(fs.readFileSync('all_games_consolidated.json', 'utf8'));
  
  let missingCovers = 0;
  let foundCovers = 0;
  
  // Find games with missing covers
  const gamesNeedingCovers = [];
  for (const platform of Object.keys(allGames)) {
    for (const game of allGames[platform]) {
      const data = gameData[game.id];
      if (data && !data.cover) {
        gamesNeedingCovers.push({ platform, game });
        missingCovers++;
      }
    }
  }
  
  console.log(`Games missing covers: ${missingCovers}`);
  
  // Try to find covers from multiple sources
  for (const { game } of gamesNeedingCovers) {
    // Try RAWG first
    const rawgCover = await getRAWGCover(game.id);
    if (rawgCover) {
      gameData[game.id].cover = rawgCover;
      foundCovers++;
      continue;
    }
    
    // Try other sources...
    // For now, use a placeholder
    const cleanTitle = game.title.toLowerCase()
      .replace(/[^a-z0-9\s]/g, '')
      .replace(/\s+/g, '-');
    
    gameData[game.id].cover = `https://via.placeholder.com/264x376?text=${encodeURIComponent(game.title)}`;
  }
  
  // Save updated data
  fs.writeFileSync('game_data_cache.json', JSON.stringify(gameData, null, 2));
  
  console.log(`Found covers: ${foundCovers}`);
  console.log(`Still missing: ${missingCovers - foundCovers}`);
}

fetchCovers().catch(console.error);
