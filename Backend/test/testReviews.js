const http = require('http');

const testEndpoints = [
  {
    name: 'Get All Reviews',
    path: '/api/reviews',
    method: 'GET'
  },
  {
    name: 'Get Analytics',
    path: '/api/reviews/analytics',
    method: 'GET'
  },
  {
    name: 'Get Single Review',
    path: '/api/reviews/R-0001',
    method: 'GET'
  }
];

function testEndpoint(endpoint) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: '192.168.1.231',
      port: 8888,
      path: endpoint.path,
      method: endpoint.method
    };

    console.log(`\n🧪 Testing: ${endpoint.name}`);
    console.log(`   ${endpoint.method} http://${options.hostname}:${options.port}${endpoint.path}`);
    
    const req = http.request(options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          console.log(`   ✅ Status: ${res.statusCode}`);
          console.log(`   📊 Response:`, JSON.stringify(json, null, 2).substring(0, 200) + '...');
          resolve({ endpoint: endpoint.name, success: true, data: json });
        } catch (e) {
          console.log(`   ❌ Invalid JSON response`);
          reject({ endpoint: endpoint.name, success: false, error: e.message });
        }
      });
    });
    
    req.on('error', (error) => {
      console.log(`   ❌ Error: ${error.message}`);
      reject({ endpoint: endpoint.name, success: false, error: error.message });
    });
    
    req.setTimeout(5000, () => {
      console.log(`   ⏱️  Timeout`);
      req.destroy();
      reject({ endpoint: endpoint.name, success: false, error: 'Timeout' });
    });
    
    req.end();
  });
}

async function runTests() {
  console.log('\n========================================');
  console.log('  TESTING REVIEWS API ENDPOINTS');
  console.log('========================================');
  
  const results = [];
  
  for (const endpoint of testEndpoints) {
    try {
      const result = await testEndpoint(endpoint);
      results.push(result);
    } catch (error) {
      results.push(error);
    }
  }
  
  console.log('\n========================================');
  console.log('  TEST SUMMARY');
  console.log('========================================');
  
  const passed = results.filter(r => r.success).length;
  const failed = results.filter(r => !r.success).length;
  
  console.log(`✅ Passed: ${passed}/${testEndpoints.length}`);
  console.log(`❌ Failed: ${failed}/${testEndpoints.length}`);
  
  if (failed > 0) {
    console.log('\nFailed tests:');
    results.filter(r => !r.success).forEach(r => {
      console.log(`  - ${r.endpoint}: ${r.error}`);
    });
  }
  
  console.log('\n========================================\n');
}

// Chạy tests
runTests();
