# Acceptance Criteria Template

Plantilla para definir criterios de aceptacion detallados de cada historia de usuario.

---

## Estructura

Cada criterio de aceptacion debe ser:

1. **Especifico**: Describe un comportamiento observable
2. **Verificable**: Se puede comprobar con una prueba
3. **Completable**: Se puede marcar como hecho/no hecho

Formato sugerido: "Dado [contexto], cuando [accion], entonces [resultado esperado]"

---

## Categorias de Criterios

### Funcionales
- Comportamiento del sistema ante una accion del usuario
- Validaciones y reglas de negocio
- Flujos de trabajo

### Tecnicos
- Integraciones con APIs externas
- Rendimiento o limites
- Seguridad

### UX
- Mensajes al usuario
- Navegacion
- Feedback visual

---

## Ejemplo

**US-CLI-02**: Campos obligatorios en contacto

| # | Criterio | Dado | Cuando | Entonces |
|---|----------|------|--------|----------|
| 1 | Nombre obligatorio | Formulario de contacto abierto | Usuario intenta guardar sin nombre | Mensaje "El campo Nombre es obligatorio" y formulario no se guarda |
| 2 | Telefono obligatorio | Formulario de contacto abierto | Usuario intenta guardar sin telefono | Mensaje "El campo Telefono es obligatorio" y formulario no se guarda |
| 3 | Email obligatorio | Formulario de contacto abierto | Usuario intenta guardar sin email | Mensaje "El campo Email es obligatorio" y formulario no se guarda |
| 4 | Campos completos | Formulario con nombre, telefono y email | Usuario guarda | Contacto se crea/actualiza correctamente |

---

## Checklist por US

Antes de marcar una US como Completada:

- [ ] Todos los criterios de aceptacion pasan
- [ ] Pruebas manuales o automaticas ejecutadas
- [ ] Documentacion actualizada si aplica
- [ ] Sin regresiones en funcionalidad existente
