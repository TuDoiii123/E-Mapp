const http = require('http'); // Thay https thành http

const BASE_URL = 'http://localhost:8888';

// Test data
let CITIZEN_TOKEN = '';
let ADMIN_TOKEN = '';
let APPOINTMENT_ID = '';
let NOTIFICATION_ID = '';

// Helper function to make HTTP requests
function makeRequest(method, url, headers = {}, body = null) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const options = {
      hostname: urlObj.hostname,
      port: urlObj.port,
      path: urlObj.pathname + urlObj.search,
      method: method,
      headers: {
        'Content-Type': 'application/json',
        ...headers
      }
    };

    const req = http.request(options, (res) => { // Thay https thành http
      let data = '';
      res.on('data', (chunk) => {
        data += chunk;
      });
      res.on('end', () => {
        try {
          const jsonData = JSON.parse(data);
          console.log(`\n[${method}] ${url}`);
          console.log(`Status: ${res.statusCode}`);
          console.log('Response:', JSON.stringify(jsonData, null, 2));
          resolve({ response: res, data: jsonData });
        } catch (e) {
          console.log(`\n[${method}] ${url}`);
          console.log(`Status: ${res.statusCode}`);
          console.log('Response:', data);
          resolve({ response: res, data: null });
        }
      });
    });

    req.on('error', (err) => {
      console.error('Request error:', err.message);
      reject(err);
    });

    if (body) {
      req.write(JSON.stringify(body));
    }
    req.end();
  });
}

// Test functions
async function testLogin() {
  console.log('\n🚀 TESTING LOGIN...');
  
  // Login Citizen
  const citizenLogin = await makeRequest('POST', `${BASE_URL}/api/auth/login`, {}, {
    cccdNumber: '001200001234',
    password: 'Password123!'
  });
  
  if (citizenLogin.data.success) {
    CITIZEN_TOKEN = citizenLogin.data.data.token;
    console.log('✅ Citizen login successful');
  } else {
    console.log('❌ Citizen login failed');
  }
  
  // Login Admin
  const adminLogin = await makeRequest('POST', `${BASE_URL}/api/auth/login`, {}, {
    cccdNumber: '000000000001',
    password: 'AdminPassword123!'
  });
  
  if (adminLogin.data.success) {
    ADMIN_TOKEN = adminLogin.data.data.token;
    console.log('✅ Admin login successful');
  } else {
    console.log('❌ Admin login failed');
  }
}

async function testAppointments() {
  console.log('\n📅 TESTING APPOINTMENTS...');
  
  // 1. Citizen creates appointment
  const createAppointment = await makeRequest('POST', `${BASE_URL}/api/appointments`, {
    'Authorization': `Bearer ${CITIZEN_TOKEN}`
  }, {
    agencyId: 'UBND Quận Hoàn Kiếm',
    serviceCode: 'Cấp giấy khai sinh',
    date: '2025-12-15', // THAY ĐỔI: Ngày tương lai
    time: '09:30'
  });
  
  if (createAppointment.data.success) {
    APPOINTMENT_ID = createAppointment.data.data.id;
    console.log(`✅ Appointment created with ID: ${APPOINTMENT_ID}`);
  } else {
    console.log('❌ Failed to create appointment');
  }
  
  // 2. Admin views appointments
  const viewAppointments = await makeRequest('GET', `${BASE_URL}/api/appointments?agencyId=UBND%20Quận%20Hoàn%20Kiếm`, {
    'Authorization': `Bearer ${ADMIN_TOKEN}`
  });
  
  if (viewAppointments.data.success) {
    console.log(`✅ Admin can view ${viewAppointments.data.data.length} appointments`);
  } else {
    console.log('❌ Admin failed to view appointments');
  }
  
  // 3. Admin updates appointment status
  if (APPOINTMENT_ID) {
    const updateStatus = await makeRequest('PUT', `${BASE_URL}/api/appointments/${APPOINTMENT_ID}/status`, {
      'Authorization': `Bearer ${ADMIN_TOKEN}`,
      'Content-Type': 'application/json'
    }, {
      status: 'accepted'
    });
    
    if (updateStatus.data.success) {
      console.log('✅ Appointment status updated to accepted');
    } else {
      console.log('❌ Failed to update appointment status');
    }
  }
}

async function testNotifications() {
  console.log('\n🔔 TESTING NOTIFICATIONS...');
  
  // 1. Citizen views notifications
  const viewNotifications = await makeRequest('GET', `${BASE_URL}/api/notifications`, {
    'Authorization': `Bearer ${CITIZEN_TOKEN}`
  });
  
  if (viewNotifications.data.success) {
    console.log(`✅ Citizen can view ${viewNotifications.data.data.length} notifications`);
    if (viewNotifications.data.data.length > 0) {
      NOTIFICATION_ID = viewNotifications.data.data[0].id;
    }
  } else {
    console.log('❌ Citizen failed to view notifications');
  }
  
  // 2. Admin sends notification
  const sendNotification = await makeRequest('POST', `${BASE_URL}/api/notifications`, {
    'Authorization': `Bearer ${ADMIN_TOKEN}`
  }, {
    toUserId: 'USR-002', // Citizen user ID
    title: 'Thông báo quan trọng',
    message: 'Lịch hẹn của bạn đã được cập nhật.',
    type: 'appointment_update',
    relatedId: APPOINTMENT_ID
  });
  
  if (sendNotification.data.success) {
    console.log('✅ Admin sent notification successfully');
    NOTIFICATION_ID = sendNotification.data.data.id;
  } else {
    console.log('❌ Admin failed to send notification');
  }
  
  // 3. Citizen marks notification as read
  if (NOTIFICATION_ID) {
    const markAsRead = await makeRequest('PUT', `${BASE_URL}/api/notifications/${NOTIFICATION_ID}/read`, {
      'Authorization': `Bearer ${CITIZEN_TOKEN}`
    });
    
    if (markAsRead.data.success) {
      console.log('✅ Notification marked as read');
    } else {
      console.log('❌ Failed to mark notification as read');
    }
  }
}

// Main test function
async function runTests() {
  try {
    console.log('🧪 STARTING API TESTS...');
    
    await testLogin();
    await testAppointments();
    await testNotifications();
    
    console.log('\n✅ ALL TESTS COMPLETED!');
  } catch (error) {
    console.error('❌ Test failed:', error.message);
  }
}

// Run tests
runTests();
