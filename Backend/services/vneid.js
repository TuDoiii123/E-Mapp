/**
 * VNeID Mock Service
 * This simulates VNeID API integration for demo purposes
 * In production, this would connect to the actual VNeID API
 */

/**
 * Verify user with VNeID
 * @param {string} cccdNumber - Citizen ID number
 * @returns {Promise<Object|null>} - VNeID user data or null if verification fails
 */
async function verifyVNeID(cccdNumber) {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 500));

  // Mock verification logic
  // In production, this would make an actual API call to VNeID service
  // For demo, we'll accept any valid 12-digit CCCD number
  
  if (!cccdNumber || cccdNumber.length !== 12 || !/^\d+$/.test(cccdNumber)) {
    return null;
  }

  // Mock VNeID response
  // In real implementation, this would be the actual response from VNeID API
  return {
    id: `vneid_${cccdNumber}`,
    cccdNumber: cccdNumber,
    verified: true,
    verifiedAt: new Date().toISOString(),
    // Additional VNeID data that might be returned
    fullName: null, // Would be populated from VNeID
    dateOfBirth: null,
    address: null
  };
}

/**
 * Get VNeID user information
 * @param {string} vneidId - VNeID user ID
 * @returns {Promise<Object|null>} - User information from VNeID
 */
async function getVNeIDUserInfo(vneidId) {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 300));

  if (!vneidId) {
    return null;
  }

  // Mock VNeID user info
  return {
    id: vneidId,
    verified: true,
    verificationLevel: 'level2', // level1, level2, level3
    verifiedAt: new Date().toISOString()
  };
}

/**
 * Check if VNeID is available (for demo purposes, always return true)
 * In production, this would check if VNeID service is online
 */
async function isVNeIDAvailable() {
  return true;
}

module.exports = {
  verifyVNeID,
  getVNeIDUserInfo,
  isVNeIDAvailable
};

