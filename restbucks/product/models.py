from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.

CHOICES = (
    ('skim', _('skim')),
    ('semi', _('semi')),
    ('whole', _('whole')),
    ('small', _('small')),
    ('medium', _('medium')),
    ('large', _('large')),
    ('single', _('single')),
    ('double', _('double')),
    ('triple', _('triple')),
    ('choclate_chip', _('choclate chip')),
    ('ginger', _('ginger')),
)

TITLE = (
    ('size', _("Size")),
    ('shots', _("Shots")),
    ('kind', _("Kind")),
)

class Customazition(models.Model):
    c_option = models.CharField(_("Custome Option"), max_length=13, choices=CHOICES, unique=True)

    def __str__(self):
        return str(self.get_c_option_display())


class Option(models.Model):
    title = models.CharField(_("Title"), choices=TITLE, max_length=120)
    customazition = models.ManyToManyField(Customazition, 'option', blank=True, verbose_name=_("Customazition"))
    product = models.ForeignKey('Product', models.CASCADE, 'option', verbose_name=_("Product"))

    def __str__(self):
        return f"{self.title}: {self.product}"


class Product(models.Model):
    title = models.CharField(_("Title"), max_length=120)
    slug = models.SlugField(_("Slug"), max_length=120, unique=True, allow_unicode=True, blank=True)
    image = models.ImageField(_("Image"), blank=True)
    description = models.TextField(_("Description"))
    price = models.PositiveIntegerField(verbose_name=_("Price"))
    offered_price = models.PositiveIntegerField(verbose_name=_("Offered Price"), blank=True, null=True)
    special = models.BooleanField(_("Special"), default=False)
    created_date = models.DateTimeField(_("Created"), auto_now_add=True)
    updated_date = models.DateTimeField(_("Updated"), auto_now=True)

    def __str__(self):
        return str(self.title)