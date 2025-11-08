const fs = require('fs').promises;
const path = require('path');

const DATA_FILE = path.join(__dirname, '../data/service_categories.json');

async function ensureDataFile() {
  try {
    await fs.access(DATA_FILE);
  } catch {
    await fs.mkdir(path.dirname(DATA_FILE), { recursive: true });
    await fs.writeFile(DATA_FILE, JSON.stringify([], null, 2));
  }
}

async function getCategories() {
  await ensureDataFile();
  const data = await fs.readFile(DATA_FILE, 'utf-8');
  return JSON.parse(data || '[]');
}

async function saveCategories(categories) {
  await ensureDataFile();
  await fs.writeFile(DATA_FILE, JSON.stringify(categories, null, 2));
}

class ServiceCategory {
  constructor(data) {
    this.id = data.id || Date.now().toString();
    this.name = data.name;
    this.nameEn = data.nameEn || data.name;
    this.code = data.code;
    this.description = data.description || '';
    this.icon = data.icon || 'building';
    this.createdAt = data.createdAt || new Date().toISOString();
    this.updatedAt = data.updatedAt || new Date().toISOString();
  }

  static async findAll() {
    return await getCategories();
  }

  static async findById(id) {
    const categories = await getCategories();
    return categories.find(c => c.id === id) || null;
  }

  static async findByCode(code) {
    const categories = await getCategories();
    return categories.find(c => c.code === code) || null;
  }

  static async create(data) {
    const categories = await getCategories();
    const existing = categories.find(c => c.code === data.code);
    if (existing) {
      throw new Error('Category code already exists');
    }
    const category = new ServiceCategory(data);
    categories.push(category);
    await saveCategories(categories);
    return category;
  }
}

module.exports = ServiceCategory;

