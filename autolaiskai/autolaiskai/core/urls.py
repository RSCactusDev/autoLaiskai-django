from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from core.views import (
    landing_page,
    settings_view,
    generate,
    generate_letters_view,
    search_address, 
    process_table_data,
    download_file

)


urlpatterns = [
    path('', landing_page, name="landing_page"),
    path('settings/', settings_view, name="settings" ),
    path('generate/', generate, name="generate"),
    path('generate_letters/', generate_letters_view, name="generate_letters"),
    path('generate_letters_2/', search_address, name="generate_letters_2"),
    path('genereta_leters_3/', process_table_data, name="genereta_leters_3"),
     path('download/<path:file_path>/', download_file, name='download_file'),
] 
