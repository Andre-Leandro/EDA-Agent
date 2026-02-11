# Docker - Instrucciones de uso

## Prerrequisitos

1. Crear archivo `.env` con tu API key de Google:
```bash
GOOGLE_API_KEY=tu_api_key_aqui
```

## Opción 1: Docker directo

### Construcción de la imagen

```bash
cd backend
docker build -t eda-agent .
```

### Ejecución del contenedor

```bash
docker run --env-file .env -p 8000:8000 eda-agent
```

## Opción 2: Docker Compose (Recomendado)

```bash
cd backend
docker-compose up --build
```

Para ejecutar en background:
```bash
docker-compose up -d
```

Para detener:
```bash
docker-compose down
```

## Opciones adicionales

### Ejecutar en modo detached (background)
```bash
docker run -d --env-file .env -p 8000:8000 --name eda-agent-backend eda-agent
```

### Ver logs del contenedor
```bash
docker logs -f eda-agent-backend
```

### Detener el contenedor
```bash
docker stop eda-agent-backend
```

### Eliminar el contenedor
```bash
docker rm eda-agent-backend
```

### Reconstruir sin cache
```bash
docker build --no-cache -t eda-agent .
```

## Verificación

Una vez ejecutado, acceder a:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Notas

- El directorio `plots/` se crea automáticamente dentro del contenedor
- Matplotlib está configurado en modo headless (Agg backend)
- Los plots generados se almacenan en memoria del contenedor
- Si necesitas persistir plots entre reinicios, monta un volumen:
  ```bash
  docker run --env-file .env -p 8000:8000 -v $(pwd)/plots:/app/plots eda-agent
  ```
