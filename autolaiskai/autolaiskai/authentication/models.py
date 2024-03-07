from pyexpat import model
from urllib import request
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required


from django.db.models.signals import pre_save
from django.dispatch import receiver
import os


class MyCustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, kv_nr, password=None):
        if not email: 
            raise ValueError("Vartotojas turi turėti pašto adresą.")
        if not first_name:
            raise ValueError("Vartotojas turi turėti Vardą.")
        if not last_name:
            raise ValueError("Vartotojas turi turėti Pavardę.")
        if not kv_nr:
            raise ValueError("Vartotojas turi turėti kvalifikacijos pažymėjimo numerį.")
        user  = self.model(
                email=self.normalize_email(email),
                first_name=first_name,
                last_name=last_name,
                kv_nr=kv_nr,
            )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, kv_nr, password):
        user = self.create_user(
               email=self.normalize_email(email),
               first_name=first_name,
               last_name=last_name,
               kv_nr=kv_nr,
               password=password,
            )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user



def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.id, filename)

class CustomUser (AbstractBaseUser, PermissionsMixin):

    STATUS = {
        ('regular','regular'),
        ('trial','trial'),
        ('premium','premium')
    }

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(verbose_name='Email', max_length=60, unique=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    date_created = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    kv_nr = models.CharField(verbose_name='matininko kvalifikacijos pažymėjimas', max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS, default='regular')
    template_header = models.FileField(null = True, upload_to=user_directory_path, blank=True)
    generated_kv = models.FileField(null = True, upload_to=user_directory_path, blank=True)
    nr = models.IntegerField(null=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name','kv_nr']

    objects = MyCustomUserManager()

    def __str__(self) -> str:
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    class Meta:
        verbose_name = 'User'

## Then uploading new file, replace it with already existing file
@receiver(pre_save, sender=CustomUser)
def file_update(sender, instance, **kwargs):
    expectation = 'user_' + str(instance.id) + '/'
    try:
        if expectation not in instance.template_header:
            try: 
                #print(instance.id)
                #print(instance.template_header, 'new')
                #print(sender.objects.get(pk=instance.pk).template_header.path, 'old')
                #print(instance.generated_kv, 'new')
                old_template_header = sender.objects.get(pk=instance.pk).template_header.path
                #print(old_template_header) 
                if old_template_header:
                    path = old_template_header
                    os.remove(path)
            except: 
                print('None1')
    except: 
        print('None')
       
    