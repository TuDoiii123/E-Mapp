const fs = require('fs').promises;
const path = require('path');

const DATA_FILE = path.join(__dirname, '../data/users.json');

// Ensure data directory exists
async function ensureDataFile() {
  try {
    await fs.access(DATA_FILE);
  } catch {
    // File doesn't exist, create it with empty array
    await fs.mkdir(path.dirname(DATA_FILE), { recursive: true });
    await fs.writeFile(DATA_FILE, JSON.stringify([], null, 2));
  }
}

// Read users from file
async function getUsers() {
  await ensureDataFile();
  const data = await fs.readFile(DATA_FILE, 'utf-8');
  return JSON.parse(data || '[]');
}

// Write users to file
async function saveUsers(users) {
  await ensureDataFile();
  // Save users with all properties including password
  const usersToSave = users.map(user => {
    if (user instanceof User) {
      // If it's a User instance, get all properties including password
      return {
        id: user.id,
        cccdNumber: user.cccdNumber,
        fullName: user.fullName,
        dateOfBirth: user.dateOfBirth,
        phone: user.phone,
        email: user.email,
        password: user.password, // Keep password for storage
        role: user.role,
        isVNeIDVerified: user.isVNeIDVerified,
        vneidId: user.vneidId,
        createdAt: user.createdAt,
        updatedAt: user.updatedAt
      };
    }
    return user; // Already plain object
  });
  await fs.writeFile(DATA_FILE, JSON.stringify(usersToSave, null, 2));
}

class User {
  constructor(data) {
    this.id = data.id || Date.now().toString();
    this.cccdNumber = data.cccdNumber;
    this.fullName = data.fullName;
    this.dateOfBirth = data.dateOfBirth;
    this.phone = data.phone;
    this.email = data.email;
    this.password = data.password; // Hashed
    this.role = data.role || 'citizen'; // 'citizen' or 'admin'
    this.isVNeIDVerified = data.isVNeIDVerified || false;
    this.vneidId = data.vneidId || null;
    this.createdAt = data.createdAt || new Date().toISOString();
    this.updatedAt = data.updatedAt || new Date().toISOString();
  }

  // Remove password before returning
  toJSON() {
    const { password, ...user } = this;
    return user;
  }

  // Find user by CCCD number
  static async findByCCCD(cccdNumber) {
    const users = await getUsers();
    const userData = users.find(u => u.cccdNumber === cccdNumber);
    return userData ? new User(userData) : null;
  }

  // Find user by ID
  static async findById(id) {
    const users = await getUsers();
    const userData = users.find(u => u.id === id);
    return userData ? new User(userData) : null;
  }

  // Find user by email
  static async findByEmail(email) {
    const users = await getUsers();
    const userData = users.find(u => u.email === email);
    return userData ? new User(userData) : null;
  }

  // Create new user
  static async create(userData) {
    const users = await this.findAll();
    
    // Kiểm tra user đã tồn tại
    const existingUser = users.find(u => u.cccdNumber === userData.cccdNumber);
    if (existingUser) {
      throw new Error('Người dùng với số CCCD này đã tồn tại');
    }

    const newUser = {
      id: `USR-${Date.now()}`,
      ...userData,
      password: userData.password, // LƯU TRỰC TIẾP, KHÔNG HASH
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    users.push(newUser);
    await writeData(userFilePath, users);
    return new User(newUser);
  }

  // Update user
  async update(updates) {
    const users = await getUsers();
    const index = users.findIndex(u => u.id === this.id);
    
    if (index === -1) {
      throw new Error('User not found');
    }

    // If password is being updated, hash it
    if (updates.password) {
      updates.password = await bcrypt.hash(updates.password, 10);
    }

    users[index] = {
      ...users[index],
      ...updates,
      updatedAt: new Date().toISOString()
    };

    await saveUsers(users);
    return new User(users[index]);
  }

  // Verify password
  async verifyPassword(password) {
    return password === this.password; // SO SÁNH TRỰC TIẾP
  }

  // Initialize with default admin user (for demo)
  static async initializeDefaultUsers() {
    const users = await getUsers();
    
    // Check if admin exists and has password
    const adminExists = users.find(u => u.role === 'admin');
    if (!adminExists || !adminExists.password) {
      // Remove old admin if exists but has no password
      if (adminExists) {
        const index = users.findIndex(u => u.id === adminExists.id);
        if (index !== -1) {
          users.splice(index, 1);
        }
      }
      
      // Create new admin with password
      const adminPassword = await bcrypt.hash('admin123', 10);
      const admin = new User({
        id: 'admin-001',
        cccdNumber: '000000000000',
        fullName: 'Administrator',
        dateOfBirth: '1990-01-01',
        phone: '0123456789',
        email: 'admin@publicservices.gov.vn',
        password: adminPassword,
        role: 'admin',
        isVNeIDVerified: true
      });
      users.push(admin);
      await saveUsers(users);
      console.log('Default admin user created: admin@publicservices.gov.vn / admin123');
    }
  }
}

module.exports = User;

