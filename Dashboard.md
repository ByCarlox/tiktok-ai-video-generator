# 🎬 Dashboard

## Pendientes
```dataview
TABLE estado, fecha_creacion
FROM "03-Contenidos/Episodios"
SORT fecha_creacion DESC
```

## Todos los videos
```dataview
TABLE views, likes, estado
FROM "03-Contenidos/Episodios"
SORT views DESC
```