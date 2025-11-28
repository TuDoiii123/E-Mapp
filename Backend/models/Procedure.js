const fs = require('fs').promises;
const path = require('path');

const DATA_FILE = path.join(__dirname, '../data/procedures.json');

class Procedure {
  constructor(data) {
    this.id = data.id;
    this.userId = data.userId || data.user_id;
    this.appointmentId = data.appointmentId || data.appointment_id;
    this.agencyId = data.agencyId || data.agency_id;
    this.serviceCode = data.serviceCode || data.service_code;
    this.title = data.title;
    this.status = data.status; // received, processing, missing_docs, completed
    this.submitDate = data.submitDate || data.submit_date;
    this.completedDate = data.completedDate || data.completed_date;
    this.office = data.office;
    this.progress = data.progress || 0;
    this.note = data.note;
    this.createdAt = data.createdAt || data.created_at || new Date().toISOString();
    this.updatedAt = data.updatedAt || data.updated_at;
  }

  static async readData() {
    try {
      const data = await fs.readFile(DATA_FILE, 'utf8');
      return JSON.parse(data);
    } catch (error) {
      if (error.code === 'ENOENT') {
        await fs.writeFile(DATA_FILE, '[]', 'utf8');
        return [];
      }
      throw error;
    }
  }

  static async writeData(data) {
    await fs.writeFile(DATA_FILE, JSON.stringify(data, null, 2), 'utf8');
  }

  static async create(data) {
    try {
      const procedures = await this.readData();
      
      const id = 'PROC-' + Math.random().toString(36).substr(2, 8).toUpperCase();

      const newProcedure = {
        id,
        userId: data.userId,
        appointmentId: data.appointmentId,
        agencyId: data.agencyId,
        serviceCode: data.serviceCode,
        title: data.title || data.serviceCode,
        status: data.status || 'received',
        submitDate: data.submitDate || new Date().toISOString().split('T')[0],
        office: data.office,
        progress: this.calculateProgress(data.status || 'received'),
        note: data.note,
        createdAt: new Date().toISOString()
      };

      procedures.push(newProcedure);
      await this.writeData(procedures);

      return new Procedure(newProcedure);
    } catch (error) {
      console.error('Error in create procedure:', error);
      throw error;
    }
  }

  static calculateProgress(status) {
    switch (status) {
      case 'received': return 25;
      case 'processing': return 50;
      case 'missing_docs': return 40;
      case 'completed': return 100;
      default: return 0;
    }
  }

  static async findByUserId(userId) {
    try {
      const procedures = await this.readData();
      const filtered = procedures.filter(p => p.userId === userId);
      return filtered.map(item => new Procedure(item));
    } catch (error) {
      console.error('Error in findByUserId:', error);
      return [];
    }
  }

  static async findById(id) {
    try {
      const procedures = await this.readData();
      const found = procedures.find(p => p.id === id);
      return found ? new Procedure(found) : null;
    } catch (error) {
      console.error('Error in findById:', error);
      return null;
    }
  }

  static async findAll() {
    try {
      const procedures = await this.readData();
      return procedures.map(item => new Procedure(item));
    } catch (error) {
      console.error('Error in findAll:', error);
      return [];
    }
  }

  async update(updateData) {
    try {
      const procedures = await Procedure.readData();
      const index = procedures.findIndex(p => p.id === this.id);
      
      if (index === -1) {
        throw new Error('Procedure not found');
      }

      const newStatus = updateData.status || this.status;
      procedures[index] = {
        ...procedures[index],
        ...updateData,
        progress: Procedure.calculateProgress(newStatus),
        updatedAt: new Date().toISOString()
      };

      await Procedure.writeData(procedures);
      
      Object.assign(this, procedures[index]);
      return this;
    } catch (error) {
      console.error('Error in update procedure:', error);
      throw error;
    }
  }
}

module.exports = Procedure;
