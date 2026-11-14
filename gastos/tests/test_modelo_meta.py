from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

from gastos.models import Meta

User = get_user_model()


class MetaModeloTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ana = User.objects.create_user(
            username="ana@ejemplo.com", email="ana@ejemplo.com", password="clave-de-ejemplo-123"
        )
        cls.beto = User.objects.create_user(
            username="beto@ejemplo.com", email="beto@ejemplo.com", password="clave-de-ejemplo-123"
        )

    def test_meta_se_guarda_con_sus_campos(self):
        meta = Meta.objects.create(
            usuario=self.ana,
            nombre="Portátil",
            precio=Decimal("1500000"),
            fecha_limite=date(2027, 6, 30),
        )
        meta.refresh_from_db()
        self.assertEqual(meta.usuario, self.ana)
        self.assertEqual(meta.nombre, "Portátil")
        self.assertEqual(meta.precio, Decimal("1500000"))
        self.assertEqual(meta.ahorrado, 0)
        self.assertEqual(meta.fecha_limite, date(2027, 6, 30))
        self.assertIsNotNone(meta.creado)

    def test_base_de_datos_rechaza_precio_cero(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Meta.objects.create(
                    usuario=self.ana,
                    nombre="Viaje",
                    precio=0,
                    fecha_limite=date(2027, 6, 30),
                )

    def test_base_de_datos_rechaza_ahorrado_negativo(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Meta.objects.create(
                    usuario=self.ana,
                    nombre="Viaje",
                    precio=1000,
                    ahorrado=-1,
                    fecha_limite=date(2027, 6, 30),
                )

    def test_usuario_solo_ve_sus_metas(self):
        de_ana = Meta.objects.create(
            usuario=self.ana, nombre="Portátil", precio=1000, fecha_limite=date(2027, 6, 30)
        )
        de_beto = Meta.objects.create(
            usuario=self.beto, nombre="Bici", precio=2000, fecha_limite=date(2027, 7, 30)
        )
        self.assertEqual(list(self.ana.metas.all()), [de_ana])
        self.assertEqual(list(self.beto.metas.all()), [de_beto])

    def test_borrar_usuario_borra_sus_metas(self):
        Meta.objects.create(
            usuario=self.ana, nombre="Portátil", precio=1000, fecha_limite=date(2027, 6, 30)
        )
        Meta.objects.create(
            usuario=self.beto, nombre="Bici", precio=2000, fecha_limite=date(2027, 7, 30)
        )
        self.ana.delete()
        self.assertEqual(Meta.objects.filter(nombre="Portátil").count(), 0)
        self.assertEqual(Meta.objects.filter(usuario=self.beto).count(), 1)
