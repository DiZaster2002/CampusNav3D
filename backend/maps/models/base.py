class SpatialComponent:
    """
    Componente Base del Patrón Composite (OCP Compliant).
    Las operaciones del árbol son genéricas y no requieren modificación ante nuevos nodos.
    """
    _child_relation = None  # Debe ser sobrescrito por nodos compuestos

    @property
    def is_leaf(self) -> bool:
        raise NotImplementedError("Los modelos que hereden de SpatialComponent deben implementar 'is_leaf'")

    def get_children(self):
        """Navegación genérica del árbol por reflexión de relaciones Django."""
        if self.is_leaf or not self._child_relation:
            return []
        relation = getattr(self, self._child_relation, None)
        return relation.all() if relation else []

    def get_total_area(self) -> float:
        """Operación uniforme compartida por toda la jerarquía."""
        return self.geometry.area