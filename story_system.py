# story_system.py
import pygame
import os
import os_config

dialog_aktif = False
dialog_metni = ""
gosterilen_dialog = ""
dialog_harf_indeksi = 0
dialog_son_harf_zamani = 0
ses_dialog = None

def init_story():
    global ses_dialog
    try:
        yol = os.path.join("Assets", "soundeffect", "dialoguesound.mp3")
        ses_dialog = pygame.mixer.Sound(yol)
    except:
        ses_dialog = None

def dialog_baslat(metin):
    global dialog_metni, gosterilen_dialog, dialog_aktif, dialog_harf_indeksi, dialog_son_harf_zamani
    dialog_metni = metin
    gosterilen_dialog = ""
    dialog_aktif = True
    dialog_harf_indeksi = 0
    dialog_son_harf_zamani = pygame.time.get_ticks()
    if ses_dialog:
        ses_dialog.stop()
        ses_dialog.set_volume((os_config.os_sistem_sesi / 100) * 0.15)
        ses_dialog.play(-1)

def update_story(suan):
    global dialog_aktif, gosterilen_dialog, dialog_harf_indeksi, dialog_son_harf_zamani
    if dialog_aktif:
        if dialog_harf_indeksi < len(dialog_metni):
            if suan - dialog_son_harf_zamani > 40:
                gosterilen_dialog += dialog_metni[dialog_harf_indeksi]
                dialog_harf_indeksi += 1
                dialog_son_harf_zamani = suan
                if dialog_harf_indeksi == len(dialog_metni):
                    if ses_dialog:
                        ses_dialog.stop()

def tikla_gec_veya_kapat():
    global dialog_aktif, gosterilen_dialog, dialog_harf_indeksi
    if dialog_aktif:
        if dialog_harf_indeksi < len(dialog_metni):
            gosterilen_dialog = dialog_metni
            dialog_harf_indeksi = len(dialog_metni)
            if ses_dialog:
                ses_dialog.stop()
        else:
            dialog_aktif = False
        return True
    return False