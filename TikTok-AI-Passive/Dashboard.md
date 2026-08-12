# 🎬 Dashboard TikTok AI

## 📥 Pendientes de revisar
```dataview
TABLE estado, fecha_creacion, hook
FROM "03-Contenidos/Episodios"
WHERE estado != "publicado"
SORT fecha_creacion DESC
```

## ✅ Publicados (top por views)
```dataview
TABLE views, likes, comentarios, compartidos, retencion_3s
FROM "03-Contenidos/Episodios"
WHERE estado = "publicado"
SORT views DESC
```

## 🗂️ Todos los episodios
```dataview
TABLE estado, views, likes, fecha_creacion
FROM "03-Contenidos/Episodios"
SORT fecha_creacion DESC
```

---

## ⚙️ Configuración requerida

Para que el dashboard funcione:
1. Instalar plugin **Dataview** en Obsidian (Settings → Community Plugins → Browse → Dataview)
2. Activar el plugin
3. Recargar la ventana (Cmd+R)
