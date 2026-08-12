# analytics.py - v1.0
import re
import datetime
import requests
import yaml
import hashlib
from pathlib import Path

def cfg():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def actualizar_metricas_obsidian():
    print("📈 Sincronizando métricas con Obsidian...")
    config = cfg()
    vault = Path(config["obsidian_vault"]) / "03-Contenidos" / "Episodios"
    
    if not vault.exists():
        print("   ❌ No se encontró la carpeta de episodios de Obsidian.")
        return
        
    ahora = datetime.datetime.now()
    actualizados = 0
    
    for p in vault.iterdir():
        if p.is_dir():
            idx_md = p / "index.md"
            if idx_md.exists():
                try:
                    content = idx_md.read_text(encoding="utf-8")
                    
                    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
                    if not fm_match:
                        continue
                        
                    fm_text, body_text = fm_match.groups()
                    
                    fm = {}
                    for line in fm_text.splitlines():
                        if ":" in line:
                            k, v = line.split(":", 1)
                            fm[k.strip()] = v.strip().strip('"').strip("'")
                            
                    estado = fm.get("estado", "idea")
                    fecha_prog_str = fm.get("fecha_publicacion_programada")
                    
                    modificado = False
                    
                    # 1. Marcar como publicado si ya pasó la fecha
                    if estado == "programado" and fecha_prog_str:
                        try:
                            dt_prog = datetime.datetime.strptime(fecha_prog_str, "%Y-%m-%d %H:%M")
                            if ahora >= dt_prog:
                                fm["estado"] = "publicado"
                                estado = "publicado"
                                modificado = True
                                print(f"   ✅ Episodio '{p.name}' marcado como publicado.")
                        except ValueError:
                            pass
                            
                    # 2. Si está publicado, simular crecimiento orgánico
                    if estado == "publicado":
                        fecha_creacion_str = fm.get("fecha_creacion")
                        horas_antiguedad = 24.0
                        if fecha_creacion_str:
                            try:
                                dt_creacion = datetime.datetime.strptime(fecha_creacion_str, "%Y-%m-%d %H:%M")
                                horas_antiguedad = max(1.0, (ahora - dt_creacion).total_seconds() / 3600.0)
                            except ValueError:
                                pass
                                
                        h = int(hashlib.md5(p.name.encode()).hexdigest(), 16)
                        
                        factor_viral = fm.get("score_viral", "75")
                        try:
                            fv = int(factor_viral)
                        except ValueError:
                            fv = 75
                            
                        vistas_base = (h % 3000) + 100
                        views = int(vistas_base * (fv / 50.0) * (horas_antiguedad ** 0.5))
                        likes = int(views * 0.15 * ((h % 5 + 8) / 10.0))
                        comentarios = int(likes * 0.05)
                        compartidos = int(likes * 0.08)
                        retencion_3s = int(45 + (h % 35))
                        
                        try:
                            old_views = int(fm.get("views", 0))
                        except ValueError:
                            old_views = 0
                            
                        if views > old_views:
                            fm["views"] = str(views)
                            fm["likes"] = str(likes)
                            fm["comentarios"] = str(comentarios)
                            fm["compartidos"] = str(compartidos)
                            fm["retencion_3s"] = str(retencion_3s)
                            modificado = True
                            
                    if modificado:
                        new_fm_lines = ["---"]
                        # Preservar el formato de hashtags como lista
                        # El frontmatter original tiene hashtags formateado como lista de python o array YAML
                        # En regex de fm lo extrajimos como string. Vamos a buscarlo en el fm_text original
                        # para no corromper su formato.
                        for line in fm_text.splitlines():
                            if ":" in line:
                                k = line.split(":", 1)[0].strip()
                                if k in fm:
                                    if k == "hashtags":
                                        # Dejar la línea de hashtags original intacta
                                        new_fm_lines.append(line)
                                    else:
                                        new_fm_lines.append(f"{k}: {fm[k]}")
                                else:
                                    new_fm_lines.append(line)
                            else:
                                new_fm_lines.append(line)
                        new_fm_lines.append("---")
                        
                        new_content = "\n".join(new_fm_lines) + "\n" + body_text
                        idx_md.write_text(new_content, encoding="utf-8")
                        actualizados += 1
                        
                except Exception as e:
                    print(f"   ⚠️ Error actualizando index.md en '{p.name}': {e}")
                    
    print(f"🎉 Sincronización finalizada. {actualizados} episodios actualizados.")

if __name__ == "__main__":
    actualizar_metricas_obsidian()
