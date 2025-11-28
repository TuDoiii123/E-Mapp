const fs = require('fs').promises;
const path = require('path');

const DATA_FILE = path.join(__dirname, '../data/notifications.json');

class Notification {
  constructor(data) {
    this.id = data.id;
    this.toUserId = data.toUserId || data.to_user_id;
    this.fromAgencyId = data.fromAgencyId || data.from_agency_id;
    this.title = data.title;
    this.message = data.message;
    this.type = data.type;
    this.relatedId = data.relatedId || data.related_id;
    this.isRead = data.isRead || data.is_read || false;
    this.createdAt = data.createdAt || data.created_at || new Date().toISOString();
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

  static async create(notificationData) {
    try {
      const notifications = await this.readData();
      
      const id = 'NTF-' + Math.random().toString(36).substr(2, 8).toUpperCase();

      const newNotification = {
        id,
        toUserId: notificationData.toUserId,
        fromAgencyId: notificationData.fromAgencyId,
        title: notificationData.title,
        message: notificationData.message,
        type: notificationData.type || 'system',
        relatedId: notificationData.relatedId,
        isRead: false,
        createdAt: new Date().toISOString()
      };

      notifications.push(newNotification);
      await this.writeData(notifications);

      return new Notification(newNotification);
    } catch (error) {
      console.error('Error in create notification:', error);
      throw error;
    }
  }

  static async findByUserId(userId) {
    try {
      const notifications = await this.readData();
      const filtered = notifications.filter(n => n.toUserId === userId);
      return filtered.map(item => new Notification(item));
    } catch (error) {
      console.error('Error in findByUserId:', error);
      return [];
    }
  }

  static async markAsRead(id, userId) {
    try {
      const notifications = await this.readData();
      const index = notifications.findIndex(n => n.id === id && n.toUserId === userId);
      
      if (index === -1) {
        return null;
      }

      notifications[index].isRead = true;
      notifications[index].readAt = new Date().toISOString();
      
      await this.writeData(notifications);
      
      return new Notification(notifications[index]);
    } catch (error) {
      console.error('Error in markAsRead:', error);
      throw error;
    }
  }
}

module.exports = Notification;
