from django.db import models


class Link(models.Model):
    href = models.CharField(max_length=255, help_text="URL do link", verbose_name="Link")
    label = models.CharField(max_length=255, help_text="Texto do link", verbose_name="Texto")
    icon = models.CharField(
        max_length=255,
        default="/static/img/pmesp.svg",
        blank=True,
        help_text="URL ou caminho do ícone",
        verbose_name="Ícone"
    )
    alt = models.CharField(max_length=255, blank=True, help_text="Texto alternativo da imagem", verbose_name="Texto Alternativo")
    target = models.CharField(max_length=20, default="_self", choices=[("_self", "Mesma aba"), ("_blank", "Nova aba")], help_text="Onde abrir o link", verbose_name="Target")
    order = models.PositiveIntegerField(default=0, help_text="Ordem de exibição do link", verbose_name="Ordem")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Link"
        verbose_name_plural = "Links"

    def __str__(self):
        return self.label

    def save(self, *args, **kwargs):
        if self._state.adding:
            used_orders = set(type(self).objects.values_list("order", flat=True))
            self.order = 1
            while self.order in used_orders:
                self.order += 1

        if not self.alt:
            self.alt = self.label
        super().save(*args, **kwargs)