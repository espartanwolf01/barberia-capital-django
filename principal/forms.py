from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

Usuario = get_user_model()


class RegistroForm(forms.Form):
    nombre = forms.CharField(max_length=150)
    email = forms.EmailField(max_length=150)
    telefono = forms.RegexField(
        regex=r"^\+?[0-9\s()-]{7,20}$",
        max_length=20,
        error_messages={
            "invalid": "Escribe un teléfono válido.",
        },
    )
    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput,
    )

    def clean_email(self):
        email = self.cleaned_data["email"].lower()

        if (
            Usuario.objects.filter(email__iexact=email).exists()
            or Usuario.objects.filter(username__iexact=email).exists()
        ):
            raise forms.ValidationError(
                "Este correo ya está registrado."
            )

        return email

    def clean(self):
        datos = super().clean()
        password = datos.get("password")

        if password:
            usuario = Usuario(
                username=datos.get("email", ""),
                email=datos.get("email", ""),
                first_name=datos.get("nombre", ""),
            )

            try:
                validate_password(password, user=usuario)
            except forms.ValidationError as errores:
                self.add_error("password", errores)

        return datos