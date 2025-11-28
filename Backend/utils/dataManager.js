const fs = require('fs').promises;
const path = require('path');

async function ensureFile(filePath, defaultContent = '[]') {
	// Ensure directory exists and file exists
	const dir = path.dirname(filePath);
	await fs.mkdir(dir, { recursive: true });
	try {
		await fs.access(filePath);
	} catch (err) {
		// create file with default content
		await fs.writeFile(filePath, defaultContent, 'utf8');
	}
}

async function readData(filePath) {
	await ensureFile(filePath);
	const content = await fs.readFile(filePath, 'utf8');
	try {
		return JSON.parse(content || '[]');
	} catch (err) {
		// If file corrupted, reset to empty array and return []
		await fs.writeFile(filePath, '[]', 'utf8');
		return [];
	}
}

async function writeData(filePath, data) {
	await ensureFile(filePath);
	const json = JSON.stringify(data, null, 2);
	await fs.writeFile(filePath, json, 'utf8');
}

module.exports = {
	readData,
	writeData,
	ensureFile
};
