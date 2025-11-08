const fs = require('fs').promises;
const path = require('path');

const DATA_FILE = path.join(__dirname, '../data/public_services.json');

async function ensureDataFile() {
  try {
    await fs.access(DATA_FILE);
  } catch {
    await fs.mkdir(path.dirname(DATA_FILE), { recursive: true });
    await fs.writeFile(DATA_FILE, JSON.stringify([], null, 2));
  }
}

async function getServices() {
  await ensureDataFile();
  const data = await fs.readFile(DATA_FILE, 'utf-8');
  return JSON.parse(data || '[]');
}

async function saveServices(services) {
  await ensureDataFile();
  await fs.writeFile(DATA_FILE, JSON.stringify(services, null, 2));
}

class PublicService {
  constructor(data) {
    this.id = data.id || Date.now().toString();
    this.name = data.name;
    this.description = data.description || '';
    this.categoryId = data.categoryId;
    this.locationId = data.locationId;
    this.address = data.address;
    this.latitude = data.latitude;
    this.longitude = data.longitude;
    this.phone = data.phone || '';
    this.email = data.email || '';
    this.website = data.website || '';
    this.workingHours = data.workingHours || {
      monday: '7:30-17:30',
      tuesday: '7:30-17:30',
      wednesday: '7:30-17:30',
      thursday: '7:30-17:30',
      friday: '7:30-17:30',
      saturday: '7:30-12:00',
      sunday: 'Closed'
    };
    this.services = data.services || []; // Danh sách dịch vụ hỗ trợ
    this.level = data.level || 'district'; // 'ward', 'district', 'province'
    this.rating = data.rating || 0;
    this.status = data.status || 'normal'; // 'normal', 'busy', 'available'
    this.distance = data.distance || null; // Khoảng cách tính từ vị trí người dùng (km)
    this.createdAt = data.createdAt || new Date().toISOString();
    this.updatedAt = data.updatedAt || new Date().toISOString();
  }

  static async findAll() {
    return await getServices();
  }

  static async findById(id) {
    const services = await getServices();
    return services.find(s => s.id === id) || null;
  }

  static async findByCategory(categoryId) {
    const services = await getServices();
    return services.filter(s => s.categoryId === categoryId);
  }

  static async findByLevel(level) {
    const services = await getServices();
    return services.filter(s => s.level === level);
  }

  static async search(query, categoryId = null) {
    const services = await getServices();
    let results = services;

    if (query) {
      const lowerQuery = query.toLowerCase();
      results = results.filter(s => 
        s.name.toLowerCase().includes(lowerQuery) ||
        s.description.toLowerCase().includes(lowerQuery) ||
        s.address.toLowerCase().includes(lowerQuery) ||
        s.services.some(service => service.toLowerCase().includes(lowerQuery))
      );
    }

    if (categoryId) {
      results = results.filter(s => s.categoryId === categoryId);
    }

    return results;
  }

  static async create(data) {
    const services = await getServices();
    const service = new PublicService(data);
    services.push(service);
    await saveServices(services);
    return service;
  }

  static async update(id, updates) {
    const services = await getServices();
    const index = services.findIndex(s => s.id === id);
    if (index === -1) {
      throw new Error('Service not found');
    }
    services[index] = {
      ...services[index],
      ...updates,
      updatedAt: new Date().toISOString()
    };
    await saveServices(services);
    return new PublicService(services[index]);
  }
}

module.exports = PublicService;

