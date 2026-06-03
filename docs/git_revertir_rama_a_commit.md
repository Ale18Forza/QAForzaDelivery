# Cómo revertir una rama remota a un commit específico

Guía de referencia para descartar un commit no deseado y dejar la rama remota apuntando a un commit anterior.

---

## Contexto del problema

- Tienes una rama con un commit "malo" en el tope (ej. un merge accidental).
- Quieres regresar al commit anterior y que el remoto también quede en ese punto.

---

## Comandos utilizados

### 1. Ver el historial reciente para identificar los commits
```bash
git log --oneline -8
```
- Muestra los últimos 8 commits con su hash corto y mensaje.
- Identifica el **commit bueno** al que quieres regresar.

---

### 2. Ver qué cambios tiene el commit malo (para confirmar antes de descartarlo)
```bash
git show <hash-commit-malo> --stat
```
Ejemplo:
```bash
git show 66110fd9 --stat
```

---

### 3. Ver qué cambios tiene el commit bueno (para confirmar que es el correcto)
```bash
git show <hash-commit-bueno> --stat
```
Ejemplo:
```bash
git show 4dc5a5d4 --stat
```

---

### 4. Mover el HEAD local al commit bueno (descarta el commit malo localmente)
```bash
git reset --hard <hash-commit-bueno>
```
Ejemplo:
```bash
git reset --hard 4dc5a5d44c8f60abf08ea5f8d28f53402f481abc
```
> ⚠️ `--hard` descarta los cambios sin posibilidad de recuperación local. Confirma el hash antes de ejecutar.

---

### 5. Subir el cambio al remoto (forzar la actualización)
```bash
git push origin <nombre-rama> --force-with-lease
```
Ejemplo:
```bash
git push origin feature/StagingQA --force-with-lease
```
> `--force-with-lease` es más seguro que `--force`: falla si alguien más subió cambios al remoto desde tu último fetch, evitando sobreescribir trabajo ajeno.

---

## Resumen de los 5 comandos en orden

```bash
# 1. Ver historial
git log --oneline -8

# 2. Inspeccionar commit malo
git show <hash-malo> --stat

# 3. Inspeccionar commit bueno
git show <hash-bueno> --stat

# 4. Revertir local al commit bueno
git reset --hard <hash-bueno>

# 5. Actualizar el remoto
git push origin <nombre-rama> --force-with-lease
```

---

## Caso real resuelto

| Campo            | Valor                                      |
|------------------|--------------------------------------------|
| Repositorio      | `settlement-dbo`                           |
| Rama             | `feature/StagingQA`                        |
| Commit descartado| `66110fd9` — merge de FDAPI-5972           |
| Commit destino   | `4dc5a5d4` — Ajuste de parametros de fechas|
| Remoto           | Bitbucket — `cashlogisticsgroup`           |

---

> **Nota:** Si necesitas recuperar el commit descartado antes de hacer push, puedes encontrarlo con `git reflog` mientras siga en el historial local.
