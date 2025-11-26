const http = require('http');
const os = require('os');

console.log('\n========================================');
console.log('  SERVER CONNECTION DIAGNOSTIC');
console.log('========================================\n');

// 1. Kiểm tra network interfaces
console.log('1️⃣  Network Interfaces:');
const networkInterfaces = os.networkInterfaces();
const addresses = [];
for (const name of Object.keys(networkInterfaces)) {
  for (const net of networkInterfaces[name]) {
    if (net.family === 'IPv4' && !net.internal) {
      addresses.push(net.address);
      console.log(`   ✓ ${name}: ${net.address}`);
    }
  }
}

// 2. Test kết nối
console.log('\n2️⃣  Testing Connections:\n');

const testHosts = [
  { name: 'Localhost', host: 'localhost' },
  { name: 'Loopback', host: '127.0.0.1' },
  ...addresses.map(addr => ({ name: `Network (${addr})`, host: addr }))
];

async function testConnection(host, port) {
  return new Promise((resolve) => {
    const options = {
      hostname: host,
      port: port,
      path: '/api/health',
      method: 'GET',
      timeout: 3000
    };

    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          resolve({ success: true, status: res.statusCode, data: json });
        } catch (e) {
          resolve({ success: false, error: 'Invalid JSON' });
        }
      });
    });

    req.on('error', (error) => {
      resolve({ success: false, error: error.message });
    });

    req.on('timeout', () => {
      req.destroy();
      resolve({ success: false, error: 'Timeout' });
    });

    req.end();
  });
}

async function runTests() {
  for (const testHost of testHosts) {
    const url = `http://${testHost.host}:8888/api/health`;
    process.stdout.write(`   Testing ${testHost.name.padEnd(20)}: `);
    
    const result = await testConnection(testHost.host, 8888);
    
    if (result.success) {
      console.log(`✅ SUCCESS (${result.status})`);
    } else {
      console.log(`❌ FAILED - ${result.error}`);
    }
  }
  
  console.log('\n========================================');
  console.log('  RECOMMENDATIONS');
  console.log('========================================\n');
  
  const hasSuccess = await testConnection('localhost', 8888);
  
  if (!hasSuccess.success) {
    console.log('❌ Server không chạy hoặc không listen port 8888');
    console.log('   → Chạy: cd Backend && node server.js');
  } else {
    console.log('✅ Server đang chạy');
    console.log('\n📝 Sử dụng một trong các URL sau:');
    testHosts.forEach(test => {
      console.log(`   - http://${test.host}:8888/api/health`);
    });
  }
  
  console.log('\n========================================\n');
}

runTests();
