const express = require('express');
const cors = require('cors');

const app = express();

app.use(cors());
app.use(express.json());

const PORT = 8006;

// ⚡ MAPA DE PUERTOS REALES SEGÚN TU DOCKER PS
const DOCKER_AUTH_MS = 'http://localhost:8001'; 
const DOCKER_STATS_MS = 'http://localhost:8002';
const DOCKER_ROOMS_MS = 'http://localhost:8004';

console.log("====================================================");
console.log(" 🛡️  BFF FocusAdmin - CONECTADO A MICROSERVICIOS REALES");
console.log(` ⚙️  Escuchando peticiones de React en: http://localhost:${PORT}`);
console.log("====================================================");

// ====================================================
// 1. ENDPOINT: LOGIN DE ADMINISTRADOR
// ====================================================
// ====================================================
// 1. ENDPOINT: LOGIN DE ADMINISTRADOR BLINDADO
// ====================================================
// ====================================================
// 1. ENDPOINT: LOGIN DE ADMINISTRADOR BLINDADO
// ====================================================
app.post('/api/v1/auth/login', async (req, res) => {
  try {
    // CORREGIDO: Usamos la variable real definida arriba (DOCKER_AUTH_MS)
    const urlLogin = `${DOCKER_AUTH_MS}/api/v1/auth/login`;
    console.log(`\n➡️  BFF: Intento de Login para: ${req.body.email}`);

    // 1. Autenticamos contra Litestar
    const responseAuth = await fetch(urlLogin, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: req.body.email, password: req.body.password })
    });

    const dataAuth = await responseAuth.json().catch(() => ({}));
    if (!responseAuth.ok) return res.status(responseAuth.status).json(dataAuth);

    const token = dataAuth.access_token || dataAuth.token;

    // 2. 🚨 CAPA DE SEGURIDAD ESTRICTA: Consultamos la lista de usuarios reales para validar el rol
    const responseAllUsers = await fetch(`${DOCKER_AUTH_MS}/api/v1/users`, {
      method: 'GET',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    const usersList = await responseAllUsers.json().catch(() => []);
    
    // Buscamos al usuario que está intentando ingresar
    const usuarioLogueado = usersList.find(u => u.email.toLowerCase() === req.body.email.toLowerCase());

    // 3. Bloqueamos el paso si no existe o si su rol no es exactamente "administrador"
    if (!usuarioLogueado || usuarioLogueado.role !== 'administrador') {
      console.log(`🚨 BFF BLOQUEO: Acceso denegado para ${req.body.email}. Rol detectado: ${usuarioLogueado ? usuarioLogueado.role : 'ninguno'}`);
      return res.status(403).json({ error: 'Acceso denegado. Este panel es exclusivo para el rol ADMINISTRADOR.' });
    }

    console.log(`🔑 BFF ACCESO CONCEDIDO: ${req.body.email} es Administrador.`);
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
  try {
    console.log("➡️  BFF: Consultando reportes reales al ms_stats...");
    
    const response = await fetch(`${DOCKER_STATS_MS}/api/v1/sessions/reports?limit=100`, {
      method: 'GET',
      headers: { 'Authorization': req.headers.authorization || '' }
    });

    const data = await response.json().catch(() => ({}));
    
    // Extraemos la lista de reportes (si viene envuelto en un objeto o directo como array)
    const reports = Array.isArray(data) ? data : (data.reports || []);

    if (reports.length === 0) {
      // Data inicial por si la base de datos está recién creada y vacía
      return res.json([
        { title: "Sesiones Monitoreadas", value: "0", detail: "Sin registros aún" },
        { title: "Tiempo Promedio Focus", value: "0 min", detail: "Esperando alumnos" },
        { title: "Atención Media Global", value: "0%", detail: "Base de datos limpia" }
      ]);
    }

    // Procesamiento matemático real de las sesiones guardadas de los alumnos
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
  try {
    const response = await fetch(`${DOCKER_STATS_MS}/api/v1/sessions/reports?limit=50`, {
      method: 'GET',
      headers: { 'Authorization': req.headers.authorization || '' }
    });

    const data = await response.json().catch(() => ({}));
    const reports = Array.isArray(data) ? data : (data.reports || []);

    if (reports.length === 0) {
      return res.json([
        { hora: "Sin Datos", alumnos: 0, atencionMedia: 0 }
      ]);
    }

    // Mapeamos los reportes reales para armar las coordenadas del gráfico de áreas
    const chartData = reports.map((session, index) => {
      // Extraemos o formateamos la hora del registro
      let horaFormateada = `Bloque ${index + 1}`;
      if (session.created_at || session.start_time) {
        const fecha = new Date(session.created_at || session.start_time);
        if (!isNaN(fecha.getTime())) {
          horaFormateada = fecha.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        }
      }

      return {
        hora: horaFormateada,
        alumnos: session.participants_count || session.total_users || 1, // Usuarios en la sesión
        atencionMedia: Math.round(parseFloat(session.avg_focus_score || session.focus_score || 80))
      };
    });

    // Lo ordenamos cronológicamente si es necesario y respondemos a Recharts
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

    // Mapeamos los campos del backend de salas móviles al formato que lee tu componente RoomMonitor.jsx
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