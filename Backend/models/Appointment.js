const fs = require('fs').promises;
const path = require('path');

const DATA_FILE = path.join(__dirname, '../data/appointments.json');

class Appointment {
  constructor(data) {
    this.id = data.id;
    this.userId = data.userId || data.user_id;
    this.agencyId = data.agencyId || data.agency_id;
    this.serviceCode = data.serviceCode || data.service_code;
    this.date = data.date;
    this.time = data.time;
    this.status = data.status;
    this.fullName = data.fullName || data.full_name || '';
    this.phone = data.phone || '';
    this.info = data.info || data.details || '';
    this.createdAt = data.createdAt || data.created_at || new Date().toISOString();
  }

  static async readData() {
    try {
      const dir = path.dirname(DATA_FILE);
      await fs.mkdir(dir, { recursive: true }).catch(() => {});
      const data = await fs.readFile(DATA_FILE, 'utf8');
      try {
        return JSON.parse(data);
      } catch (parseErr) {
        // If corrupted, backup and reset
        const backupPath = path.join(dir, `appointments_corrupted_${Date.now()}.json`);
        await fs.writeFile(backupPath, data, 'utf8').catch(() => {});
        await fs.writeFile(DATA_FILE, '[]', 'utf8');
        return [];
      }
    } catch (error) {
      if (error.code === 'ENOENT') {
        // File doesn't exist, create it
        const dir = path.dirname(DATA_FILE);
        await fs.mkdir(dir, { recursive: true }).catch(() => {});
        await fs.writeFile(DATA_FILE, '[]', 'utf8');
        return [];
      }
      throw error;
    }
  }

  static async writeData(data) {
    const dir = path.dirname(DATA_FILE);
    await fs.mkdir(dir, { recursive: true }).catch(() => {});
    const tmpPath = path.join(dir, `appointments_${Date.now()}.tmp`);
    const json = JSON.stringify(data, null, 2);
    await fs.writeFile(tmpPath, json, 'utf8');
    // Atomic replace
    await fs.rename(tmpPath, DATA_FILE);
  }

  static async findAll() {
    try {
      const data = await this.readData();
      return data.map(item => new Appointment(item));
    } catch (error) {
      console.error('Error in findAll:', error);
      return [];
    }
  }

  static async create(appointmentData) {
    try {
      const appointments = await this.readData();
      
      // Check for existing appointment at same time
      const existingAppointments = appointments.filter(
        apt => apt.agencyId === appointmentData.agencyId && apt.date === appointmentData.date
      );

      const sameTimeCount = existingAppointments.filter(
        apt => apt.time === appointmentData.time
      ).length;

      if (sameTimeCount >= 5) {
        throw new Error('Slot này đã đầy. Vui lòng chọn thời gian khác.');
      }

      // Generate unique ID
      const id = 'APT-' + Math.random().toString(36).substr(2, 8).toUpperCase();

      const newAppointment = {
        id,
        userId: appointmentData.userId,
        agencyId: appointmentData.agencyId,
        serviceCode: appointmentData.serviceCode,
        date: appointmentData.date,
        time: appointmentData.time,
        status: appointmentData.status || 'pending',
        fullName: appointmentData.fullName || '',
        phone: appointmentData.phone || '',
        info: appointmentData.info || '',
        createdAt: new Date().toISOString()
      };

      appointments.push(newAppointment);
      await this.writeData(appointments);

      return new Appointment(newAppointment);
    } catch (error) {
      console.error('Error in create:', error);
      throw error;
    }
  }

  static async findByAgencyAndDate(agencyId, date) {
    try {
      const appointments = await this.readData();
      const filtered = appointments.filter(
        apt => apt.agencyId === agencyId && apt.date === date
      );
      return filtered.map(item => new Appointment(item));
    } catch (error) {
      console.error('Error in findByAgencyAndDate:', error);
      return [];
    }
  }

  static async findByAgency(agencyId) {
    try {
      const appointments = await this.readData();
      const filtered = appointments.filter(apt => apt.agencyId === agencyId);
      return filtered.map(item => new Appointment(item));
    } catch (error) {
      console.error('Error in findByAgency:', error);
      return [];
    }
  }

  static async findById(id) {
    try {
      const appointments = await this.readData();
      const found = appointments.find(apt => apt.id === id);
      return found ? new Appointment(found) : null;
    } catch (error) {
      console.error('Error in findById:', error);
      return null;
    }
  }

  async update(updateData) {
    try {
      const appointments = await Appointment.readData();
      const index = appointments.findIndex(apt => apt.id === this.id);
      
      if (index === -1) {
        throw new Error('Appointment not found');
      }

      appointments[index] = {
        ...appointments[index],
        ...updateData,
        updatedAt: new Date().toISOString()
      };

      await Appointment.writeData(appointments);
      
      Object.assign(this, appointments[index]);
      return this;
    } catch (error) {
      console.error('Error in update:', error);
      throw error;
    }
  }
}

module.exports = Appointment;
