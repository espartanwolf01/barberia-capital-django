from django.db.models import Q
from datetime import datetime, time

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone

from .models import Barbero, Cita, Perfil, Servicio

Usuario = get_user_model()

HORARIOS = [
    (f"{hora:02d}:00", f"{hora:02d}:00")
    for hora in range(8, 19)
]


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


class EditarPerfilForm(forms.ModelForm):
    nombre_completo = forms.CharField(
        label="Nombre completo",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Tu nombre completo",
                "autocomplete": "name",
            }
        ),
    )

    telefono = forms.RegexField(
        label="Teléfono",
        regex=r"^\+?[0-9\s()-]{7,20}$",
        max_length=20,
        error_messages={
            "invalid": "Escribe un teléfono válido.",
        },
        widget=forms.TextInput(
            attrs={
                "type": "tel",
                "placeholder": "Tu número de teléfono",
                "autocomplete": "tel",
            }
        ),
    )

    class Meta:
        model = Perfil
        fields = ["nombre_completo", "telefono"]


class CitaForm(forms.ModelForm):
    servicio = forms.ModelChoiceField(
        label="Servicio",
        queryset=Servicio.objects.none(),
        empty_label="Selecciona un servicio",
        widget=forms.Select(
            attrs={"class": "form-select"}
        ),
    )

    barbero = forms.ModelChoiceField(
        label="Barbero",
        queryset=Barbero.objects.none(),
        empty_label="Selecciona un barbero",
        widget=forms.Select(
            attrs={"class": "form-select"}
        ),
    )

    fecha = forms.DateField(
        label="Fecha",
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={
                "type": "date",
                "class": "form-input",
            },
        ),
    )

    hora = forms.TimeField(
        label="Hora",
        input_formats=["%H:%M"],
        widget=forms.Select(
            choices=[
                ("", "Selecciona una hora"),
                *HORARIOS,
            ],
            attrs={"class": "form-select"},
        ),
    )

    notas = forms.CharField(
        label="Notas adicionales",
        required=False,
        max_length=1000,
        widget=forms.Textarea(
            attrs={
                "class": "form-textarea",
                "rows": 3,
                "placeholder": "Cuéntanos tus preferencias...",
            }
        ),
    )

    class Meta:
        model = Cita
        fields = [
            "servicio",
            "barbero",
            "fecha",
            "hora",
            "notas",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["servicio"].queryset = (
            Servicio.objects.filter(activo=True)
        )
        self.fields["barbero"].queryset = (
            Barbero.objects.filter(activo=True).filter(Q(usuario__isnull=True) | Q(usuario__is_active=True))
        )

        hoy = datetime.now(
            timezone.get_current_timezone()
        ).date()

        self.fields["fecha"].widget.attrs["min"] = (
            hoy.isoformat()
        )

    def clean_fecha(self):
        fecha = self.cleaned_data["fecha"]

        hoy = datetime.now(
            timezone.get_current_timezone()
        ).date()

        if fecha < hoy:
            raise forms.ValidationError(
                "No puedes reservar una fecha pasada."
            )

        return fecha

    def clean_hora(self):
        hora = self.cleaned_data["hora"]

        horarios_permitidos = [
            time(numero, 0)
            for numero in range(8, 19)
        ]

        if hora not in horarios_permitidos:
            raise forms.ValidationError(
                "Selecciona una hora entre las 08:00 y las 18:00, "
                "en punto."
            )

        return hora

    def clean(self):
        datos = super().clean()

        barbero = datos.get("barbero")
        fecha = datos.get("fecha")
        hora = datos.get("hora")

        if fecha and hora:
            ahora = datetime.now(
                timezone.get_current_timezone()
            )

            if (
                fecha == ahora.date()
                and hora <= ahora.time()
            ):
                self.add_error(
                    "hora",
                    "Ese horario ya pasó. Elige uno posterior.",
                )

        if barbero and fecha and hora:
            turnos_ocupados = Cita.objects.filter(
                barbero=barbero,
                fecha=fecha,
                hora=hora,
                estado__in=[
                    Cita.Estado.PENDIENTE,
                    Cita.Estado.ATENDIDA,
                ],
            )

            if self.instance.pk:
                turnos_ocupados = turnos_ocupados.exclude(
                    pk=self.instance.pk
                )

            if turnos_ocupados.exists():
                raise forms.ValidationError(
                    "Ese barbero ya tiene una cita en ese horario. "
                    "Elige otra hora o barbero."
                )

        return datos