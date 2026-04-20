import { createClient } from '@supabase/supabase-js';

const url = process.env.SUPABASE_URL;
const anonKey = process.env.SUPABASE_ANON_KEY;
const table = process.env.SUPABASE_TABLE || 'vishum_sessions';

if (!url || !anonKey) {
  console.error('❌ Faltan variables SUPABASE_URL o SUPABASE_ANON_KEY');
  process.exit(1);
}

const supabase = createClient(url, anonKey, {
  auth: { persistSession: false },
});

const { data, error } = await supabase
  .from(table)
  .select('*')
  .limit(1);

if (error) {
  console.error('❌ Error al consultar Supabase:', error.message);
  process.exit(2);
}

console.log('✅ Conexión exitosa. Muestra:', data);

