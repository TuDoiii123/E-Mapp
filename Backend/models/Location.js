const fs = require('fs').promises;
const path = require('path');

const DATA_FILE = path.join(__dirname, '../data/locations.json');

async function ensureDataFile() {
  try {
    await fs.access(DATA_FILE);
  } catch {
    await fs.mkdir(path.dirname(DATA_FILE), { recursive: true });
    await fs.writeFile(DATA_FILE, JSON.stringify([], null, 2));
  }
}

async function getLocations() {
  await ensureDataFile();
  const data = await fs.readFile(DATA_FILE, 'utf-8');
  return JSON.parse(data || '[]');
}

async function saveLocations(locations) {
  await ensureDataFile();
  await fs.writeFile(DATA_FILE, JSON.stringify(locations, null, 2));
}

class Location {
  constructor(data) {
    this.id = data.id || Date.now().toString();
    this.name = data.name;
    this.address = data.address;
    this.ward = data.ward || ''; // Phường/Xã
    this.district = data.district || ''; // Quận/Huyện
    this.province = data.province || ''; // Tỉnh/Thành phố
    this.latitude = data.latitude;
    this.longitude = data.longitude;
    this.level = data.level || 'district'; // 'ward', 'district', 'province'
    this.createdAt = data.createdAt || new Date().toISOString();
    this.updatedAt = data.updatedAt || new Date().toISOString();
  }

  static async findAll() {
    return await getLocations();
  }

  static async findById(id) {
    const locations = await getLocations();
    return locations.find(l => l.id === id) || null;
  }

  static async findByProvince(province) {
    const locations = await getLocations();
    return locations.filter(l => l.province === province);
  }

  static async findByDistrict(district) {
    const locations = await getLocations();
    return locations.filter(l => l.district === district);
  }

  static async create(data) {
    const locations = await getLocations();
    const location = new Location(data);
    locations.push(location);
    await saveLocations(locations);
    return location;
  }
}

module.exports = Location;

