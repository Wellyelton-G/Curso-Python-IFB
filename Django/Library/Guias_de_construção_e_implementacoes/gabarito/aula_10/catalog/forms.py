from django import forms
from django.contrib.auth.forms import UserCreationForm  # formulário de cadastro que já vem no Django
from django.contrib.auth.models import User

from .models import Review


class SignUpForm(UserCreationForm):
    """Formulário de cadastro: o do Django (usuário + senha duas vezes) com e-mail obrigatório."""

    # Campo novo, acrescentado aos campos que o UserCreationForm já tem
    email = forms.EmailField(label="E-mail", help_text="Usado para recuperar a senha.")

    class Meta(UserCreationForm.Meta):  # herda a configuração do formulário original
        model = User
        fields = ("username", "email")  # as senhas já são tratadas pelo UserCreationForm

    def clean_email(self):
        """Validação extra: não aceitar um e-mail que já tem conta.

        O Django chama sozinho todo método clean_<nome_do_campo> durante o is_valid().
        """
        email = self.cleaned_data["email"]  # valor já validado como e-mail
        # __iexact compara sem diferenciar maiúsculas: ANA@x.com e ana@x.com são o mesmo e-mail
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Já existe uma conta com este e-mail.")
        return email  # o método precisa devolver o valor aprovado


class ReviewForm(forms.ModelForm):
    """Formulário de avaliação: o usuário só preenche nota e comentário."""

    # Declaramos a nota "à mão" para usar botões de rádio sem a opção vazia "---------".
    # coerce=int converte o valor recebido (texto) em número.
    rating = forms.TypedChoiceField(label="Nota", choices=Review.RATING_CHOICES, coerce=int, widget=forms.RadioSelect)

    class Meta:
        model = Review
        # Livro e usuário ficam de fora de propósito: quem preenche é a view, não o navegador
        fields = ["rating", "comment"]
        widgets = {
            # Textarea é uma caixa de texto com várias linhas
            "comment": forms.Textarea(attrs={"rows": 4, "placeholder": "O que você achou do livro?"}),
        }
