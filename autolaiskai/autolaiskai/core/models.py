from asyncio import coroutines
from types import coroutine
from django.db import models
from authentication.models import CustomUser

from django.db.models.signals import pre_save
from django.dispatch import receiver
import os

# Modelis skirtas gretimybių pažymoms (pdf) sukelti
def user_directory_path(instance, filename):
    # faila ikels i MEDIA_ROOT/user_<id>/<filename>
    return 'temp/user_{0}/{1}'.format(instance.fk_id, filename)

class NeighbourNote(models.Model):
    fk = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    rc_pdf = models.FileField(null = True, upload_to=user_directory_path)
    rc_pdf_old = models.FileField(null = True, upload_to=user_directory_path)

class CrudList(models.Model):
    fk = models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True, blank=True)
    kad_nr= models.CharField(max_length=200)
    name = models.CharField(max_length=100)
    name_address = models.CharField(max_length=500)
    gim_data = models.CharField(max_length=200)
    coordinates = models.CharField(max_length=200)
    kad_address = models.CharField(max_length=1000)
    mat_date = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'CRUD_1'


@receiver(pre_save, sender=NeighbourNote)
def file_update(sender, instance, **kwargs):    
    try: 
        old_template_header = sender.objects.get(fk=instance.fk_id).rc_pdf_old.path
        print(old_template_header) 
        if old_template_header:
            path = old_template_header
            os.remove(path)
        
    except: 
        print('None 1')
   
       