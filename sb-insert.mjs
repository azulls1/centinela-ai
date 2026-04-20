import { createClient } from '@supabase/supabase-js';

const url = process.env.SUPABASE_URL;
const serviceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
const table = process.env.SUPABASE_EVENT_TABLE || 'vishum_session_events';

if (!url || !serviceKey) {
  console.error('❌ Faltan SUPABASE_URL o SUPABASE_SERVICE_ROLE_KEY');
  process.exit(1);
}

const supabase = createClient(url, serviceKey, {
  auth: { persistSession: false },
});

const row = {
  session_id: `diagnostic-${Date.now()}`,
  event_type: 'diagnostic_ping',
  payload: { note: 'Inserción automática de prueba' },
};

const { data, error } = await supabase.from(table).insert(row).select();

if (error) {
  console.error('❌ Error al insertar en Supabase:', error.message);
  process.exit(2);
}

console.log('✅ Inserción registrada:', data);

