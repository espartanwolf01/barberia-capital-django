from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Barbero

Usuario = get_user_model()


class CuentaForm(forms.Form):
    nombre = forms.CharField(label="Nombre completo", max_length=150)
    email = forms.EmailField(label="Correo de acceso", max_length=150)
    telefono = forms.RegexField(
        label="Teléfono", regex=r"^\+?[0-9\s()-]{7,20}$",
        max_length=20, required=False,
        error_messages={"invalid": "Escribe un teléfono válido."},
    )
    rol = forms.ChoiceField(choices=[("cliente", "Cliente"), ("barbero", "Barbero")])
    barbero = forms.ModelChoiceField(
        queryset=Barbero.objects.none(), required=False,
        empty_label="Selecciona el barbero (solo para ese rol)",
    )
    password1 = forms.CharField(label="Contraseña", strip=False, widget=forms.PasswordInput)
    password2 = forms.CharField(label="Repite la contraseña", strip=False, widget=forms.PasswordInput)

    def __init__(self, *args, administrador, **kwargs):
        super().__init__(*args, **kwargs)
        if administrador.is_superuser:
            self.fields["rol"].choices += [("administrador", "Administrador")]
        self.fields["barbero"].queryset = Barbero.objects.filter(
            activo=True, usuario__isnull=True,
        )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if Usuario.objects.filter(email__iexact=email).exists() or Usuario.objects.filter(username__iexact=email).exists():
            raise forms.ValidationError("Ese correo ya tiene una cuenta.")
        return email

    def clean(self):
        datos = super().clean()
        rol, barbero = datos.get("rol"), datos.get("barbero")
        if rol == "barbero" and barbero is None:
            self.add_error("barbero", "Selecciona un barbero sin cuenta vinculada.")
        if rol and rol != "barbero" and barbero is not None:
            self.add_error("barbero", "Este campo solo se utiliza para cuentas de barbero.")
        clave = datos.get("password1")
        if clave and clave != datos.get("password2"):
            self.add_error("password2", "Las contraseñas no coinciden.")
        if clave:
            usuario = Usuario(username=datos.get("email", ""), email=datos.get("email", ""), first_name=datos.get("nombre", ""))
            try:
                validate_password(clave, usuario)
            except forms.ValidationError as errores:
                self.add_error("password1", errores)
        return datos


class AgendaFiltroForm(forms.Form):
    fecha = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"))
    estado = forms.ChoiceField(required=False, choices=[
        ("", "Todos los estados"), ("pendiente", "Pendiente"),
        ("atendida", "Atendida"), ("cancelada", "Cancelada"),
    ])


class BarberoVinculoForm(forms.ModelForm):
    class Meta:
        model = Barbero
        fields = "__all__"

    def clean_usuario(self):
        usuario = self.cleaned_data.get("usuario")
        if usuario and (usuario.is_staff or usuario.is_superuser):
            raise forms.ValidationError("Vincula una cuenta sin acceso administrativo. El barbero tiene su propia agenda.")
        return usuario
