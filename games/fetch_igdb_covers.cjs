const fs = require('fs');
const https = require('https');

const IGDB_CLIENT_ID = 'q12h9vnj16kgj3ifvykqla67vc2cip';
const IGDB_CLIENT_SECRET = '6vqk45gmb6axve81mel5gmei5oyc4d';

let accessToken = null;
let tokenExpiry = null;

function httpsRequest(options, body) {
  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          try {
            resolve(JSON.parse(data));
          } catch (e) {
            resolve(data);
          }
        } else {
          reject(new Error(`HTTP ${res.statusCode}: ${data.substring(0, 200)}`));
        }
      });
    });
    req.on('error', reject);
    if (body) req.write(body);
    req.end();
  });
}

async function getAccessToken() {
  if (accessToken && tokenExpiry && Date.now() < tokenExpiry) {
    return accessToken;
  }
  
  try {
    const body = JSON.stringify({
      client_id: IGDB_CLIENT_ID,
      client_secret: IGDB_CLIENT_SECRET,
      grant_type: 'client_credentials'
    });
    
    const result = await httpsRequest({
      hostname: 'id.twitch.tv',
      path: '/oauth2/token',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body)
      }
    }, body);
    
    accessToken = result.access_token;
    tokenExpiry = Date.now() + (result.expires_in - 3600) * 1000;
    console.log('Got new access token');
    return accessToken;
  } catch (e) {
    console.error('Error getting access token:', e.message);
    return null;
  }
}

async function searchIGDB(title) {
  const token = await getAccessToken();
  if (!token) return null;
  
  try {
    const body = `search "${title.replace(/"/g, '\\"')}"; fields name, cover.url, cover.image_id; limit 5;`;
    
    const result = await httpsRequest({
      hostname: 'api.igdb.com',
      path: '/games',
      method: 'POST',
      headers: {
        'Client-ID': IGDB_CLIENT_ID,
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'text/plain',
        'Accept': 'application/json',
        'Content-Length': Buffer.byteLength(body)
      }
    }, body);
    
    return result;
  } catch (e) {
    // Don't log every error to avoid spam
    return null;
  }
}

function getBestCover(game) {
  if (!game || !game.cover || !game.cover.image_id) return null;
  const imageId = game.cover.image_id;
  return `https://images.igdb.com/igdb/image/upload/t_cover_big/${imageId}.jpg`;
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function fetchMissingCovers() {
  const gameData = JSON.parse(fs.readFileSync('game_data_cache.json', 'utf8'));
  const allGames = JSON.parse(fs.readFileSync('all_games_consolidated.json', 'utf8'));
  
  const gamesNeedingCovers = [];
  for (const platform of Object.keys(allGames)) {
    for (const game of allGames[platform]) {
      const data = gameData[game.id];
      if (data && !data.cover) {
        gamesNeedingCovers.push({ platform, game });
      }
    }
  }
  
  console.log(`Games missing covers: ${gamesNeedingCovers.length}`);
  
  if (gamesNeedingCovers.length === 0) {
    console.log('All games have covers!');
    return;
  }
  
  let found = 0;
  let notFound = 0;
  let errors = 0;
  
  for (let i = 0; i < gamesNeedingCovers.length; i++) {
    const { game } = gamesNeedingCovers[i];
    
    const results = await searchIGDB(game.title);
    await sleep(100);
    
    if (results && Array.isArray(results) && results.length > 0) {
      const bestMatch = results.find(r => r.cover && r.cover.image_id) || results[0];
      const coverUrl = getBestCover(bestMatch);
      
      if (coverUrl) {
        gameData[game.id].cover = coverUrl;
        found++;
      } else {
        notFound++;
      }
    } else {
      notFound++;
    }
    
    if ((i + 1) % 50 === 0) {
      console.log(`  [${i + 1}/${gamesNeedingCovers.length}] Found: ${found}, Not found: ${notFound}`);
      fs.writeFileSync('game_data_cache.json', JSON.stringify(gameData, null, 2));
    }
  }
  
  fs.writeFileSync('game_data_cache.json', JSON.stringify(gameData, null, 2));
  console.log(`\nDone! Found covers: ${found}, Still missing: ${notFound}`);
}

fetchMissingCovers().catch(console.error);
