# 🚀 Guía de Despliegue

Esta guía explica cómo desplegar **Vision Human Insight** en un VPS o servidor propio.

## 📋 Opciones de Despliegue

### Opción 1: Despliegue Local (Desarrollo)
Seguir las instrucciones de `INSTALLATION.md`

### Opción 2: VPS con Docker (Recomendado)
Usar Docker Compose para facilitar el despliegue

### Opción 3: VPS Manual
Instalar y configurar manualmente en el servidor

## 🐳 Despliegue con Docker

### Requisitos

- Docker instalado
- Docker Compose instalado
- VPS con al menos 2GB RAM

### Pasos

1. **Clonar proyecto en el servidor**

```bash
git clone <repo-url>
cd vision-aiagentek
```

2. **Configurar variables de entorno**

Crear archivo `.env` en la raíz:

```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_SERVICE_ROLE_KEY=tu_service_role_key
OPENAI_API_KEY=opcional
FRONTEND_URL=https://tu-dominio.com
```

3. **Construir y ejecutar**

```bash
cd infra
docker-compose up -d
```

4. **Configurar Nginx (reverso proxy)**

```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    # Frontend
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🖥️ Despliegue Manual en VPS

### Configuración del Servidor

1. **Actualizar sistema**

```bash
sudo apt update && sudo apt upgrade -y
```

2. **Instalar Node.js 22.x**

```bash
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs
```

3. **Instalar Python 3.11**

```bash
sudo apt install python3.11 python3.11-venv python3-pip
```

4. **Instalar Nginx**

```bash
sudo apt install nginx
```

### Configurar Backend

```bash
# Crear usuario para la aplicación
sudo useradd -m -s /bin/bash visionapp

# Cambiar a usuario
sudo su - visionapp

# Clonar proyecto
git clone <repo-url> vision-app
cd vision-app/apps/api

# Crear entorno virtual
python3.11 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar .env
nano .env
# (copiar variables de entorno)

# Crear servicio systemd
sudo nano /etc/systemd/system/vision-api.service
```

Contenido del servicio:

```ini
[Unit]
Description=Vision Human Insight API
After=network.target

[Service]
User=visionapp
WorkingDirectory=/home/visionapp/vision-app/apps/api
Environment="PATH=/home/visionapp/vision-app/apps/api/venv/bin"
ExecStart=/home/visionapp/vision-app/apps/api/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```

Activar servicio:

```bash
sudo systemctl enable vision-api
sudo systemctl start vision-api
sudo systemctl status vision-api
```

### Configurar Frontend

```bash
cd /home/visionapp/vision-app/apps/web

# Instalar dependencias
npm install

# Construir para producción
npm run build

# Instalar PM2 (process manager)
npm install -g pm2

# Crear script de inicio
pm2 start npm --name "vision-web" -- run preview
pm2 save
pm2 startup
```

### Configurar Nginx

```bash
sudo nano /etc/nginx/sites-available/vision-app
```

Configuración:

```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    # Frontend
    location / {
        proxy_pass http://localhost:4173;  # Puerto de preview de Vite
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Activar sitio:

```bash
sudo ln -s /etc/nginx/sites-available/vision-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Configurar SSL con Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d tu-dominio.com
```

## 🔒 Seguridad

### Firewall

```bash
# Permitir solo puertos necesarios
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### Variables de Entorno

- Nunca commitear `.env` a Git
- Usar variables de entorno del sistema o secretos
- Rotar keys periódicamente

### HTTPS

- Siempre usar HTTPS en producción
- Configurar certificados SSL
- Redirigir HTTP a HTTPS

## 📊 Monitoreo

### Logs

```bash
# Backend
sudo journalctl -u vision-api -f

# Frontend (PM2)
pm2 logs vision-web

# Nginx
sudo tail -f /var/log/nginx/error.log
```

### Recursos

```bash
# CPU y memoria
htop

# Espacio en disco
df -h

# Procesos
ps aux | grep uvicorn
```

## 🔄 Actualizaciones

```bash
# Backend
cd /home/visionapp/vision-app/apps/api
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart vision-api

# Frontend
cd /home/visionapp/vision-app/apps/web
git pull
npm install
npm run build
pm2 restart vision-web
```

## 🌐 Configuración de Dominio

1. Registrar dominio
2. Configurar DNS A record apuntando a IP del VPS
3. Esperar propagación DNS (puede tardar horas)
4. Configurar SSL con Let's Encrypt

## 💰 Costos Estimados

- **VPS básico**: $5-10/mes (DigitalOcean, Linode, Vultr)
- **Supabase**: Gratis (hasta cierto límite)
- **Dominio**: $10-15/año
- **Total**: ~$10-15/mes

## 📝 Checklist de Despliegue

- [ ] VPS configurado con Node.js y Python
- [ ] Proyecto clonado y dependencias instaladas
- [ ] Variables de entorno configuradas
- [ ] Supabase configurado y esquema SQL ejecutado
- [ ] Backend ejecutándose y accesible
- [ ] Frontend construido y servido
- [ ] Nginx configurado como reverse proxy
- [ ] SSL/HTTPS configurado
- [ ] Firewall configurado
- [ ] Monitoreo de logs configurado
- [ ] Backup de base de datos configurado (opcional)

## 🆘 Troubleshooting

### Backend no responde

- Verificar logs: `sudo journalctl -u vision-api`
- Verificar puerto: `netstat -tulpn | grep 8000`
- Verificar firewall

### Frontend no carga

- Verificar build: `npm run build`
- Verificar PM2: `pm2 status`
- Verificar Nginx: `sudo nginx -t`

### Errores de conexión a Supabase

- Verificar variables de entorno
- Verificar que RLS está configurado
- Verificar conectividad desde el servidor

---

**¿Necesitas ayuda?** Revisa los logs y la documentación de cada servicio.

