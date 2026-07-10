# 🟢 Usamos la versión oficial de Node.js ligera
FROM node:20-slim

# Definimos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos los archivos de dependencias de Node
COPY package*.json ./

# Instalamos los módulos de Node (limpio y rápido para producción)
RUN npm ci --only=production

# Copiamos todo el código del BFF a la carpeta del contenedor
COPY . .

# Exponemos el puerto 8000 interno que configuramos en el docker-compose
ENV PORT=8000
EXPOSE 8000

# 🚀 EL COMANDO MÁGICO: Arranca automáticamente tu bff-server.js
CMD ["node", "bff-server.js"]