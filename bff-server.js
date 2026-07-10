const express = require('express');
const cors = require('cors');

const app = express();

app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 8000;

// ====================================================
// 🎛️ INTERRUPTOR DE MODO DE PRUEBA (PARA EL PROFESOR)
// ====================================================
// Cambia a true para simular datos, o a false para conectar la app real de tu equipo
const MODO_MOCK = false; 

// ⚡ MAPA DE PUERTOS REALES SEGÚN TU DOCKER PS
const DOCKER_AUTH_MS = process.env.AUTH_SERVICE_URL || 'http://localhost:8001'; 
const DOCKER_STATS_MS = process.env.STATS_SERVICE_URL || 'http://localhost:8002';
const DOCKER_ROOMS_MS = process.env.ROOMS_SERVICE_URL || 'http://localhost:8004';

console.log("====================================================");
console.log(` 🛡️  BFF FocusAdmin - MODO INTELIGENTE [${MODO_MOCK ? 'PRUEBA SIMULADA' : 'CONEXIÓN REAL'}]`);
console.log(` ⚙️  Escuchando peticiones de React en: http://localhost:${PORT}`);
console.log("====================================================");

// ====================================================
// 📦 COLECCIÓN DE DATOS FALSOS (MOCKS)
// ====================================================
const mockKPIs = [
  { title: "Sesiones Monitoreadas", value: "32", detail: "Total histórico en BD" },
  { title: "Tiempo Promedio Focus", value: "45 min", detail: "Por bloque de estudio" },
  { title: "Atención Media Global", value: "82.5%", detail: "Rendimiento real acumulado" }
];

const mockChart = [
  { hora: "09:00", alumnos: 4, atencionMedia: 75 },
  { hora: "11:00", alumnos: 12, atencionMedia: 85 },
  { hora: "13:00", alumnos: 8, atencionMedia: 80 },
  { hora: "15:00", alumnos: 15, atencionMedia: 88 },
  { hora: "17:00", alumnos: 9, atencionMedia: 82 }
];

const mockRooms = [
  { id: 1, name: "Sala de Estudio Alfa", host: "jose18042006@gmail.com", participants: 5, status: "Enfoque Estable", avgFocus: "88%" },
  { id: 2, name: "Laboratorio Computación Beta", host: "profe_evaluador@focus.cl", participants: 12, status: "Distracción Detectada", avgFocus: "64%" },
  { id: 3, name: "Mesa de Trabajo Grupal C", host: "alumno_test@focus.cl", participants: 3, status: "Enfoque Estable", avgFocus: "91%" }
];

const mockUsers = [
  { id: "1", email: "admin@focus.cl", name: "José Admin", role: "administrador" },
  { id: "2", email: "estudiante@focus.cl", name: "Juan Alumno", role: "estudiante" }
];

// ====================================================
// 1. ENDPOINT: LOGIN DE ADMINISTRADOR BLINDADO
// ====================================================
app.post('/api/v1/auth/login', async (req, res) => {
  const { email, password } = req.body;
  console.log(`\n➡️  BFF: Intento de Login para: ${email}`);

  // 🔮 INTERCEPCIÓN MOCK
  if (MODO_MOCK) {
    if (email.toLowerCase() === 'admin@focus.cl' || password) {
      console.log(`🔑 BFF [MOCK] ACCESO CONCEDIDO: ${email} simulado como Administrador.`);
      return res.json({ token: "jwt_token_falso_modo_prueba_profe" });
    }
    return res.status(401).json({ error: "Credenciales inválidas en simulador" });
  }

  // 🔌 CÓDIGO REAL DE TU EQUIPO
  try {
    const urlLogin = `${DOCKER_AUTH_MS}/api/v1/auth/login`;

    const responseAuth = await fetch(urlLogin, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email, password: password })
    });

    const dataAuth = await responseAuth.json().catch(() => ({}));
    if (!responseAuth.ok) return res.status(responseAuth.status).json(dataAuth);

    const token = dataAuth.access_token || dataAuth.token;

    const responseAllUsers = await fetch(`${DOCKER_AUTH_MS}/api/v1/users`, {
      method: 'GET',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    const usersList = await responseAllUsers.json().catch(() => []);
    const usuarioLogueado = usersList.find(u => u.email.toLowerCase() === email.toLowerCase());

    if (!usuarioLogueado || usuarioLogueado.role !== 'administrador') {
      console.log(`🚨 BFF BLOQUEO: Acceso denegado para ${email}. Rol detectado: ${usuarioLogueado ? usuarioLogueado.role : 'ninguno'}`);
      return res.status(403).json({ error: 'Acceso denegado. Este panel es exclusivo para el rol ADMINISTRADOR.' });
    }

    console.log(`🔑 BFF ACCESO CONCEDIDO: ${email} es Administrador.`);
    res.json({ token: token });

  } catch (error) {
    console.error("💥 BFF Error en Login de Seguridad:", error.message);
    res.status(500).json({ error: 'Error interno en la validación de privilegios' });
  }
});

// ====================================================
// 2. ENDPOINT: REGISTRO / CREACIÓN DE USUARIOS
// ====================================================
app.post('/api/v1/auth/register', async (req, res) => {
  if (MODO_MOCK) {
    return res.json({ message: "Usuario creado exitosamente (Simulado)", user: req.body });
  }

  try {
    const response = await fetch(`${DOCKER_AUTH_MS}/api/v1/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req.body)
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) return res.status(response.status).json(data);
    res.json(data);
  } catch (error) {
    res.status(500).json({ error: 'Error al registrar usuario' });
  }
});

// ====================================================
// 3. ENDPOINT: LISTAR TODOS LOS USUARIOS (GET)
// ====================================================
app.get('/api/users', async (req, res) => {
  if (MODO_MOCK) return res.json(mockUsers);

  try {
    const response = await fetch(`${DOCKER_AUTH_MS}/api/v1/users`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': req.headers.authorization || ''
      }
    });

    const data = await response.json().catch(() => []);
    if (!response.ok) return res.status(response.status).json(data);
    res.json(data);
  } catch (error) {
    res.status(500).json({ error: 'Error al obtener usuarios de la base de datos' });
  }
});

// ====================================================
// 4. ENDPOINT: MODIFICACIÓN INTEGRAL DE CUENTAS (PATCH)
// ====================================================
app.patch('/api/users/:id', async (req, res) => {
  if (MODO_MOCK) return res.json({ success: true, message: "Usuario modificado (Simulado)" });

  try {
    const { id } = req.params;
    const response = await fetch(`${DOCKER_AUTH_MS}/api/v1/users/${id}`, {
      method: 'PATCH',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': req.headers.authorization || '' 
      },
      body: JSON.stringify(req.body)
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) return res.status(response.status).json(data);
    res.json(data);
  } catch (error) {
    res.status(500).json({ error: 'Error al editar usuario en backend' });
  }
});

// ====================================================
// 5. ENDPOINT: ELIMINACIÓN DE USUARIOS REALES (DELETE)
// ====================================================
app.delete('/api/users/:id', async (req, res) => {
  if (MODO_MOCK) return res.json({ success: true, message: "Usuario eliminado (Simulado)" });

  try {
    const { id } = req.params;
    const response = await fetch(`${DOCKER_AUTH_MS}/api/v1/users/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': req.headers.authorization || '' }
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) return res.status(response.status).json(data);
    res.json(data);
  } catch (error) {
    res.status(500).json({ error: 'Error al eliminar usuario en backend' });
  }
});

// ====================================================
// 📊 6. ENDPOINT INTEGRADO: METRICAS KPIS REALES (GET)
// ====================================================
app.get('/api/stats/summary', async (req, res) => {
  if (MODO_MOCK) {
    console.log("🔮 BFF [MOCK]: Retornando KPIs de prueba para el Dashboard.");
    return res.json(mockKPIs);
  }

  try {
    console.log("➡️  BFF: Consultando reportes reales al ms_stats...");
    const response = await fetch(`${DOCKER_STATS_MS}/api/v1/sessions/reports?limit=100`, {
      method: 'GET',
      headers: { 'Authorization': req.headers.authorization || '' }
    });

    const data = await response.json().catch(() => ({}));
    const reports = Array.isArray(data) ? data : (data.reports || []);

    if (reports.length === 0) {
      return res.json([
        { title: "Sesiones Monitoreadas", value: "0", detail: "Sin registros aún" },
        { title: "Tiempo Promedio Focus", value: "0 min", detail: "Esperando alumnos" },
        { title: "Atención Media Global", value: "0%", detail: "Base de datos limpia" }
      ]);
    }

    const totalSesiones = reports.length;
    let sumaTiempo = 0;
    let sumaAtencion = 0;

    reports.forEach(session => {
      sumaTiempo += parseInt(session.duration_minutes || session.duration || 0, 10);
      sumaAtencion += parseFloat(session.avg_focus_score || session.focus_score || session.atencion || 0);
    });

    const promedioTiempo = Math.round(sumaTiempo / totalSesiones) || 0;
    const promedioAtencion = (sumaAtencion / totalSesiones).toFixed(1) || 0;

    res.json([
      { title: "Sesiones Monitoreadas", value: totalSesiones.toLocaleString(), detail: "Total histórico en BD" },
      { title: "Tiempo Promedio Focus", value: `${promedioTiempo} min`, detail: "Por bloque de estudio" },
      { title: "Atención Media Global", value: `${promedioAtencion}%`, detail: "Rendimiento real acumulado" }
    ]);

  } catch (error) {
    console.error("💥 Error en BFF al calcular KPIs reales:", error.message);
    res.status(500).json({ error: 'No se pudieron procesar las métricas de ms_stats' });
  }
});

// ====================================================
// 📈 7. ENDPOINT INTEGRADO: GRÁFICO REAL DESDE BD (GET)
// ====================================================
app.get('/api/stats/chart', async (req, res) => {
  if (MODO_MOCK) {
    console.log("🔮 BFF [MOCK]: Retornando puntos del gráfico.");
    return res.json(mockChart);
  }

  try {
    const response = await fetch(`${DOCKER_STATS_MS}/api/v1/sessions/reports?limit=50`, {
      method: 'GET',
      headers: { 'Authorization': req.headers.authorization || '' }
    });

    const data = await response.json().catch(() => ({}));
    const reports = Array.isArray(data) ? data : (data.reports || []);

    if (reports.length === 0) {
      return res.json([{ hora: "Sin Datos", alumnos: 0, atencionMedia: 0 }]);
    }

    const chartData = reports.map((session, index) => {
      let horaFormateada = `Bloque ${index + 1}`;
      if (session.created_at || session.start_time) {
        const fecha = new Date(session.created_at || session.start_time);
        if (!isNaN(fecha.getTime())) {
          horaFormateada = fecha.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        }
      }

      return {
        hora: horaFormateada,
        alumnos: session.participants_count || session.total_users || 1,
        atencionMedia: Math.round(parseFloat(session.avg_focus_score || session.focus_score || 80))
      };
    });

    res.json(chartData.reverse().slice(-10)); 

  } catch (error) {
    console.error("💥 Error en BFF al armar gráfico real:", error.message);
    res.status(500).json({ error: 'No se pudieron mapear las analíticas de ms_stats' });
  }
});

// ====================================================
// 📡 8. ENDPOINT INTEGRADO: MONITOREO DE SALAS REALES (GET)
// ====================================================
app.get('/api/rooms', async (req, res) => {
  if (MODO_MOCK) {
    console.log("🔮 BFF [MOCK]: Enviando estado de salas simuladas.");
    return res.json(mockRooms);
  }

  try {
    console.log("➡️  BFF: Solicitando salas activas al ms_rooms...");
    const response = await fetch(`${DOCKER_ROOMS_MS}/api/v1/rooms`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': req.headers.authorization || ''
      }
    });

    const data = await response.json().catch(() => []);
    if (!response.ok) return res.status(response.status).json(data);

    const mappedRooms = data.map(room => ({
      id: room.id,
      name: room.name || room.titulo || "Sala de Estudio Focus",
      host: room.host_name || room.creator_email || "Dungeon Master",
      participants: room.members_count || room.current_members || 0,
      status: room.is_active === false ? "Finalizada" : (room.has_distraction ? "Distracción Detectada" : "Enfoque Estable"),
      avgFocus: room.average_focus ? `${Math.round(room.average_focus)}%` : "85%"
    }));

    res.json(mappedRooms);

  } catch (error) {
    console.error("💥 Error en BFF al solicitar salas de Docker:", error.message);
    res.status(500).json({ error: 'No se pudo conectar con el microservicio de salas' });
  }
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Servidor Express escuchando en el puerto ${PORT}`);
});