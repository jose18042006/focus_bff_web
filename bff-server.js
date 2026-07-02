// BFF (Backend For Frontend) - Servidor Preparado para Integración
;require('dotenv').config();
const express = require('express');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3001;
const MOCK_MODE = process.env.MOCK_MODE === 'true'; // Detecta si usamos datos ficticios o reales

app.use(cors());
app.use(express.json());

// ==========================================
// BASE DE DATOS SIMULADA (MOCK DATA)
// ==========================================
let users = [
  { id: 1, name: 'Ignacio Silva', email: 'ignacio@focus.cl', role: 'Alumno', status: 'Activo' },
  { id: 2, name: 'Valeria Constanzo', email: 'v.constanzo@focus.cl', role: 'Dungeon Master', status: 'Activo' },
  { id: 3, name: 'Bastián Muñoz', email: 'bastian.m@focus.cl', role: 'Alumno', status: 'Inactivo' },
  { id: 4, name: 'Camila Rojas', email: 'camila.rojas@focus.cl', role: 'Alumno', status: 'Activo' },
];

let activeRooms = [
  { id: 1, name: 'Sala de Estudio: Álgebra Lineal', host: 'Prof. Carlos Retamal', participants: 18, avgFocus: '89%', status: 'Alta Concentración' },
  { id: 2, name: 'Laboratorio de Programación Python', host: 'Dra. María Paz', participants: 32, avgFocus: '74%', status: 'Normal' },
  { id: 3, name: 'Grupo de Repaso: Historia Universal', host: 'Prof. Juan Pérez', participants: 8, avgFocus: '45%', status: 'Distracción Detectada' },
];

// ==========================================
// 1. ENDPOINTS DE ESTADÍSTICAS Y KPIS
// ==========================================

app.get('/api/stats/summary', async (req, res) => {
  if (MOCK_MODE) {
    // Si el modo simulado está activo, responde de inmediato con lo que ya conocemos
    const totalActiveStudents = users.filter(u => u.status === 'Activo' && u.role === 'Alumno').length * 35;
    return res.json([
      { title: 'Usuarios Activos Hoy', value: `${totalActiveStudents} alumnos`, detail: '+12% respecto a ayer' },
      { title: 'Tiempo Promedio Focus', value: '48 min', detail: 'Meta ideal: 45 min por sesión' },
      { title: 'Nivel de Atención Promedio', value: '84.5%', detail: 'Basado en tareas completadas' }
    ]);
  }

  // MODO REAL: Cuando conectes con el microservicio de tus compañeros
  try {
    // Ejemplo de cómo llamará el BFF al microservicio real en el futuro:
    // const response = await fetch(`${process.env.STATS_SERVICE_URL}/metrics/summary`);
    // const data = await response.json();
    // res.json(data);
    res.json({ message: "Conexión real con Microservicio de Estadísticas no implementada aún" });
  } catch (error) {
    res.status(500).json({ error: 'Error al conectar con el microservicio de estadísticas' });
  }
});

app.get('/api/stats/chart', async (req, res) => {
  if (MOCK_MODE) {
    return res.json([
      { hora: '08:00', alumnos: 30, atencionMedia: 88 },
      { hora: '10:00', alumnos: 110, atencionMedia: 85 },
      { hora: '12:00', alumnos: 142, atencionMedia: 82 },
      { hora: '14:00', alumnos: 45, atencionMedia: 78 },
      { hora: '16:00', alumnos: 95, atencionMedia: 86 },
      { hora: '18:00', alumnos: 120, atencionMedia: 84 },
      { hora: '20:00', alumnos: 60, atencionMedia: 80 },
    ]);
  }
  // Espacio para la llamada real al microservicio de gráficos
  res.json({ message: "Modo real no conectado" });
});

// ==========================================
// 2. ENDPOINTS DE GESTIÓN DE USUARIOS (CRUD)
// ==========================================

app.get('/api/users', (req, res) => {
  // Aquí también podríamos preguntar si estamos en MOCK_MODE o traer de la base de datos real
  res.json(users);
});

app.post('/api/users', (req, res) => {
  const { name, email, role, status } = req.body;
  if (!name || !email || !role) {
    return res.status(400).json({ error: 'Faltan campos obligatorios' });
  }
  const newUser = { id: Date.now(), name, email, role, status: status || 'Activo' };
  users.push(newUser);
  res.status(201).json(newUser);
});

app.put('/api/users/:id', (req, res) => {
  const { id } = req.params;
  const { name, email, role, status } = req.body;
  const userIndex = users.findIndex(u => u.id === parseInt(id));
  
  if (userIndex === -1) return res.status(404).json({ error: 'Usuario no encontrado' });

  users[userIndex] = {
    ...users[userIndex],
    name: name || users[userIndex].name,
    email: email || users[userIndex].email,
    role: role || users[userIndex].role,
    status: status || users[userIndex].status
  };
  res.json(users[userIndex]);
});

app.delete('/api/users/:id', (req, res) => {
  const { id } = req.params;
  users = users.filter(u => u.id !== parseInt(id));
  res.json({ message: 'Usuario removido exitosamente', deletedId: parseInt(id) });
});

// ==========================================
// 3. ENDPOINTS DE MONITOREO DE SALAS
// ==========================================

app.get('/api/rooms', (req, res) => {
  res.json(activeRooms);
});

app.listen(PORT, () => {
  console.log(`====================================================`);
  console.log(` 🛡️  BFF FocusAdmin corriendo en http://localhost:${PORT}`);
  console.log(` ⚙️  Modo Simulado (MOCK_MODE): ${MOCK_MODE ? 'ACTIVADO 🟢' : 'DESACTIVADO 🔴'}`);
  console.log(`====================================================`);
});