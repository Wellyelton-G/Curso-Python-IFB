"""Formulários da aplicação de catálogo.

PT-BR: define formulários para interação do usuário, incluindo avaliações de livros.
"""

from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
	"""Formulário para criar/editar avaliação de livro.
	
	PT-BR: usuário e livro são preenchidos automaticamente na view.
	Apenas nota e comentário são editáveis pelo usuário.
	"""
	
	class Meta:
		model = Review
		fields = ["rating", "comment"]
		widgets = {
			"rating": forms.RadioSelect(choices=[(i, f"{i}★") for i in range(1, 6)]),
			"comment": forms.Textarea(attrs={
				"rows": 4,
				"placeholder": "Compartilhe sua opinião sobre este livro...",
				"class": "form-control"
			}),
		}
		labels = {
			"rating": "Sua avaliação",
			"comment": "Comentário (opcional)",
		}
