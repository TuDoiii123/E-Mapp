/**
 * Calculate distance between two coordinates using Haversine formula
 * @param {number} lat1 - Latitude of first point
 * @param {number} lon1 - Longitude of first point
 * @param {number} lat2 - Latitude of second point
 * @param {number} lon2 - Longitude of second point
 * @returns {number} Distance in kilometers
 */
function calculateDistance(lat1, lon1, lat2, lon2) {
  const R = 6371; // Radius of the Earth in kilometers
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  
  const a = 
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  const distance = R * c;
  
  return Math.round(distance * 100) / 100; // Round to 2 decimal places
}

/**
 * Convert degrees to radians
 */
function toRad(degrees) {
  return degrees * (Math.PI / 180);
}

/**
 * Find nearby services within a radius
 * @param {Array} services - Array of services with latitude and longitude
 * @param {number} userLat - User's latitude
 * @param {number} userLng - User's longitude
 * @param {number} radiusKm - Radius in kilometers (default: 10km)
 * @returns {Array} Sorted array of services with distance property
 */
function findNearby(services, userLat, userLng, radiusKm = 10) {
  if (!userLat || !userLng) {
    return [];
  }

  const nearby = services
    .filter(service => service.latitude && service.longitude)
    .map(service => {
      const distance = calculateDistance(
        userLat,
        userLng,
        service.latitude,
        service.longitude
      );
      return {
        ...service,
        distance
      };
    })
    .filter(service => service.distance <= radiusKm)
    .sort((a, b) => a.distance - b.distance);

  return nearby;
}

module.exports = {
  calculateDistance,
  findNearby,
  toRad
};

