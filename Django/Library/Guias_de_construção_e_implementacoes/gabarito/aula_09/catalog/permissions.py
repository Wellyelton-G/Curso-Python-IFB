from rest_framework import permissions


class IsStaffOrReadOnly(permissions.BasePermission):
    """Consultar (GET) é liberado para todos; criar, alterar e apagar só para a equipe.

    É o equivalente, na API, do nosso decorator staff_required das páginas.
    """

    def has_permission(self, request, view):
        # SAFE_METHODS são os métodos que só leem dados: GET, HEAD e OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)
