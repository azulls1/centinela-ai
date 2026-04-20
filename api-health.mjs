import fetch from 'node-fetch';

const baseUrl = process.env.API_BASE_URL || 'http://localhost:8000/api';
const adminToken = process.env.ADMIN_API_TOKEN || 'vision_admin_secret_2025';

async function main() {
  try {
    const healthRes = await fetch(`${baseUrl}/health`);
    const healthText = await healthRes.text();
    console.log('Health status:', healthRes.status, healthText);

    const sessionsRes = await fetch(`${baseUrl}/sessions/admin`, {
      headers: {
        'x-admin-token': adminToken,
      },
    });
    const sessionsText = await sessionsRes.text();
    console.log('Sessions status:', sessionsRes.status, sessionsText);
  } catch (error) {
    console.error('❌ Error al consultar la API:', error);
    process.exit(1);
  }
}

main();

