# OPTIMISATIONS

- Centralisation de la couche HTTP (baseURL, timeout, retry) pour réduire duplication et erreurs.
- Réduction des effets de bord WebSocket avec cleanup explicite.
- Réduction overhead Electron en évitant l'ouverture DevTools en prod.
