import pygame
import sys
import os
import math
import random
import json
from datetime import datetime

import os_config
import browser_pages
import story_system

# --- KAYIP RUH OYUNU (varsa) ---
try:
    import lost_soul_game
    LOST_SOUL_AVAILABLE = True
except ImportError:
    LOST_SOUL_AVAILABLE = False
    print("UYARI: lost_soul_game.py bulunamadı. Kayıp Ruh oyunu çalışmayacak.")

# --- GLOBAL DEĞİŞKENLER ---
lost_soul_game_instance = None
glitch_hata_mesajlari = []
glitch_hata_gosterimi = False
oyun_sonu_zamani = 0

# os_config içinde tanımlanmamış olma ihtimaline karşı dinamik çöküş değişkenleri
if not hasattr(os_config, "lost_soul_cildirdi"):
    os_config.lost_soul_cildirdi = False
if not hasattr(os_config, "lost_soul_cildirdi_zamani"):
    os_config.lost_soul_cildirdi_zamani = 0

# --- PYGAME BAŞLATMA ---
pygame.init()
pygame.mixer.init()
story_system.init_story()

OS_GENISLIK = os_config.OS_GENISLIK
OS_YUKSEKLIK = os_config.OS_YUKSEKLIK
tam_ekran = getattr(os_config, "tam_ekran", False)

if tam_ekran:
    ekran = pygame.display.set_mode((OS_GENISLIK, OS_YUKSEKLIK), pygame.FULLSCREEN)
else:
    ekran = pygame.display.set_mode((OS_GENISLIK, OS_YUKSEKLIK))
pygame.display.set_caption("ÇAĞRI")
saat = pygame.time.Clock()

# --- RENKLER ---
BEYAZ = os_config.BEYAZ
SIYAH = os_config.SIYAH
KIRMIZI = os_config.KIRMIZI
YESIL = os_config.YESIL
GRI = os_config.GRI
TURUNCU = os_config.TURUNCU
SARI = os_config.SARI
MOR = os_config.MOR
OS_ARKA_PLAN_RENK = os_config.OS_ARKA_PLAN_RENK
OS_PENCERE_BASLIK = os_config.OS_PENCERE_BASLIK

# --- FONTLAR ---
os_font = pygame.font.SysFont("tahoma", 14)
os_baslik_font = pygame.font.SysFont("tahoma", 16, bold=True)
os_buyuk_font = pygame.font.SysFont("tahoma", 28, bold=True)
mayin_font = pygame.font.SysFont("tahoma", 24, bold=True)
g_font = pygame.font.SysFont("tahoma", 80, bold=True)

mevcut_fontlar = pygame.font.get_fonts()
secilen_font_adi = "tahoma"
for f_adi in ["impact", "consolas", "couriernew", "arialblack"]:
    if f_adi in mevcut_fontlar:
        secilen_font_adi = f_adi
        break
zar_font = pygame.font.SysFont(secilen_font_adi, 75)
font = pygame.font.SysFont(secilen_font_adi, 42)
kucuk_font = pygame.font.SysFont(secilen_font_adi, 26)

# --- GLOBAL DURUMLAR ---
sistem_durumu = "ANA_GIRIS"
cutscene_asamasi = 0
boot_baslangic = 0
girilen_sifre = ""
shutdown_zaman = 0
os_baslat_acik = False
os_arka_plan_resmi = None
odak_pencere = None
pencere_sirasi = []
suruklenen_pencere = None
surukleme_farki_x = 0
surukleme_farki_y = 0
os_ayar_ses_surukleniyor = False
son_tiklama_zamani = 0
son_tiklanan_ikon = None
secili_ikon = None
indirme_durumu = "Yok"
indirme_yuzdesi = 0.0
bildirim_metni = ""
bildirim_zamani = 0
bildirim_suresi = 3000

pencere_durumlari = {
    "ZAR": {"acik": False, "x": 200, "y": 80},
    "OYUNLAR": {"acik": False, "x": 150, "y": 100},
    "MAYIN": {"acik": False, "x": 250, "y": 120},
    "TARAYICI": {"acik": False, "x": 300, "y": 100},
    "NOT": {"acik": False, "x": 450, "y": 150},
    "DUVAR": {"acik": False, "x": 400, "y": 200},
    "HESAP": {"acik": False, "x": 600, "y": 100},
    "AYAR": {"acik": False, "x": 800, "y": 150},
    "HL3": {"acik": False, "x": OS_GENISLIK//2-150, "y": OS_YUKSEKLIK//2-75},
    "KAYIP": {"acik": False, "x": 350, "y": 150},
    "BILGISAYAR": {"acik": False, "x": 100, "y": 150},
    "COP": {"acik": False, "x": 250, "y": 200},
    "KAMERA": {"acik": False, "x": 90, "y": 20}
}

not_metni = os_config.not_metni
hesap_metni = os_config.hesap_metni

# --- ZAR KRALI DEĞİŞKENLERİ ---
oyun_durumu = "ANA_MENU"
secili_indeks = 0
ayarlar_indeks = 0
market_indeks = 0
can_iksiri_sayisi = 3
hasar_iksiri_sayisi = 3
hasar_iksiri_aktif = False
tur_iksir_kullandi_mi = False
oyun_ici_durum = "OYUNCU_MENU"
aksiyon_indeks = 0
esya_indeks = 0
cubuk_x = 200
cubuk_yon = 1
atis_zamani = 0
animasyon_baslangic = 0
atis_durumu = "NORMAL"
zar_sesi_calindi = False
guncel_cubuk_hiz = 6
yesil_genislik = 80
kirmizi_genislik = 0
oyuncu_can = 100
bot_can = 100
bot_maks_can = 100
son_hasar = 0
son_zar = 0
hasar_yazisi_y = 0
hasar_yazisi_metin = ""
hasar_yazisi_renk = BEYAZ
hasar_yazisi_goster = False
zar_mevcut_x = 400
zar_mevcut_y = 450
ekran_sarsinti_suresi = 0
ekran_sarsinti_gucu = 0
flas_suresi = 0
flas_renk = BEYAZ
parcaciklar = []
secili_bolum = 0
aktif_oynanan_bolum = 1
mayin_grid = []
mayin_gorunum = []
mayin_durum = "Oynuyor"
mayin_ses_calindi = False
kayipruh_oyuncu_x = 400
kayipruh_oyuncu_y = 300

# --- GLITCH HATA MESAJLARI FONKSİYONU ---
def glitch_hata_ekle():
    global glitch_hata_mesajlari, glitch_hata_gosterimi
    glitch_hata_mesajlari = [
        "CRITICAL ERROR: Kayıp Ruh çöktü!",
        "MEMORY ACCESS VIOLATION at 0x7F8A3C",
        "SYSTEM CRASH IMMINENT - KERNEL PANIC",
        "GLITCH DETECTED IN MAIN LOOP",
        "CORRUPTED SAVE DATA DETECTED",
        "FATAL EXCEPTION: ACCESS_VIOLATION",
        "FILE NOT FOUND: lost_soul.exe",
        "RUNTIME ERROR: OUT OF BOUNDS"
    ]
    glitch_hata_gosterimi = True

# --- MEDYA YÜKLEME ---
def guvenli_resim_yukle(isim, klasor="windows", boyut=(60,60)):
    klasor_yolu = os.path.join("Assets", "images", klasor)
    tam_yol = os.path.join(klasor_yolu, isim)
    try:
        img = pygame.image.load(tam_yol).convert_alpha()
        return pygame.transform.scale(img, boyut)
    except:
        yuzey = pygame.Surface(boyut, pygame.SRCALPHA)
        yuzey.fill((150,150,150,100))
        return yuzey

def ses_yukle(isim, klasor="windows"):
    klasor_yolu = os.path.join("Assets", "soundeffect", klasor)
    tam_yol = os.path.join(klasor_yolu, isim)
    try:
        return pygame.mixer.Sound(tam_yol)
    except:
        return None

# --- İKONLAR ---
ikon_login = guvenli_resim_yukle("guest.png", "windows", (140,140))
if ikon_login.get_at((0,0)).a == 0 or ikon_login.get_at((0,0)) == (150,150,150,100):
    ikon_login = pygame.Surface((140,140), pygame.SRCALPHA)
    ikon_login.fill((60,90,130))
    pygame.draw.circle(ikon_login, (220,220,220), (70,50), 35)
    pygame.draw.circle(ikon_login, (220,220,220), (70,150), 65)
    pygame.draw.rect(ikon_login, BEYAZ, (0,0,140,140), 3)

ikon_start = guvenli_resim_yukle("start.png", "windows", (40,40))
ikon_computer = guvenli_resim_yukle("computer.png")
ikon_trash = guvenli_resim_yukle("trash.png")
ikon_folder = guvenli_resim_yukle("folder.png")
ikon_cal = guvenli_resim_yukle("cal.png")
ikon_explorer = guvenli_resim_yukle("explorer.png")
ikon_mayin = guvenli_resim_yukle("mayintarlasi.png")
ikon_not = guvenli_resim_yukle("notepad.png")
ikon_ayar = guvenli_resim_yukle("settings.png")
ikon_hl3 = guvenli_resim_yukle("half-life3.png")
ikon_kayipruh = guvenli_resim_yukle("lostsoul.png")
ikon_zar_resmi = guvenli_resim_yukle("diceking.jpg", "diceking")
ikon_cam = guvenli_resim_yukle("cam.png", "windows", (60,60))
ikon_ag = guvenli_resim_yukle("network.png", "windows", (20,20))

ikonlar = {
    "start": ikon_start,
    "COMPUTER": ikon_computer,
    "TRASH": ikon_trash,
    "OYUNLAR": ikon_folder,
    "DUVAR": ikon_folder,
    "TARAYICI": ikon_explorer,
    "HESAP": ikon_cal,
    "NOT": ikon_not,
    "AYAR": ikon_ayar,
    "MAYIN": ikon_mayin,
    "HL3": ikon_hl3,
    "KAYIP": ikon_kayipruh,
    "ZAR": ikon_zar_resmi,
    "CAM": ikon_cam,
    "AG": ikon_ag
}

# --- KAMERA GÖRSELLERİ ---
kamera_arkaplan = None
kamera_karakter = None
try:
    kamera_arkaplan = pygame.image.load(os.path.join("Assets", "images", "windows", "camerabackground.png")).convert_alpha()
    kamera_arkaplan = pygame.transform.scale(kamera_arkaplan, (320, 240))
except:
    kamera_arkaplan = pygame.Surface((320, 240))
    kamera_arkaplan.fill((50,50,50))

try:
    kamera_karakter = pygame.image.load(os.path.join("Assets", "images", "windows", "camera.png")).convert_alpha()
    kamera_karakter = pygame.transform.scale(kamera_karakter, (320, 240))
except:
    kamera_karakter = pygame.Surface((320, 240))
    kamera_karakter.fill((200,200,200))

# --- DUVAR KAĞITLARI ---
duvar_kagitlari = []
wp_klasor = os.path.join("Assets", "images", "wallpapers")
if os.path.exists(wp_klasor):
    for ds in os.listdir(wp_klasor):
        if ds.lower().endswith(('.png','.jpg','.jpeg','.webp')):
            tam = os.path.join(wp_klasor, ds)
            duvar_kagitlari.append({
                "kucuk": guvenli_resim_yukle(ds, "wallpapers", (120,80)),
                "buyuk": guvenli_resim_yukle(ds, "wallpapers", (OS_GENISLIK, OS_YUKSEKLIK)),
                "isim": ds
            })

cutscene_resmi = None
try:
    cutscene_resmi = pygame.transform.scale(
        pygame.image.load(os.path.join("Assets", "images", "windows", "cutscene.jpg")).convert_alpha(),
        (OS_GENISLIK, OS_YUKSEKLIK)
    )
except:
    cutscene_resmi = pygame.Surface((OS_GENISLIK, OS_YUKSEKLIK))
    cutscene_resmi.fill((40,40,40))

# --- ZAR KRALI GÖRSELLERİ ---
arka_plan_main = guvenli_resim_yukle("mainmenu.png", "diceking", (800,600))
arka_plan_oyun = guvenli_resim_yukle("menu.png", "diceking", (800,600))
guncel_arka_plan = arka_plan_main
el_kapali = guvenli_resim_yukle("hand1.png", "diceking", (220,220))
el_acik = guvenli_resim_yukle("hand2.png", "diceking", (220,220))
bot_el_kapali = pygame.transform.flip(el_kapali, True, False)
bot_el_acik = pygame.transform.flip(el_acik, True, False)
masa_resmi = guvenli_resim_yukle("table.png", "diceking", (400,220))
boss_avatarlari = [guvenli_resim_yukle(f"boss{i}.png", "diceking", (90,90)) for i in range(1,6)]

# --- SESLER ---
ses_startup = ses_yukle("startup.mp3", "windows")
ses_shutdown = ses_yukle("Windows Shutdown.wav", "windows")
ses_logon = ses_yukle("Windows Logon Sound.wav", "windows")
ses_notify = ses_yukle("Windows Notify.wav", "windows") or ses_yukle("Windows Ding.wav", "windows")
ses_error = ses_yukle("Windows Error.wav", "windows")
ms_start = ses_yukle("start.wav", "minesweeper")
ms_click = ses_yukle("click.wav", "minesweeper")
ms_lose = ses_yukle("lose.wav", "minesweeper")
ms_win = ses_yukle("win.wav", "minesweeper")
dk_ses_click = ses_yukle("click.mp3", "diceking")
ses_diceroll = ses_yukle("dicerool.mp3", "diceking")
ses_dmg = ses_yukle("dmg.mp3", "diceking")
ses_shoperror = ses_yukle("shoperror.mp3", "diceking")
ses_shoplvlup = ses_yukle("shoplvlup.mp3", "diceking")
dk_ses_win = ses_yukle("win.mp3", "diceking")
dk_ses_lose = ses_yukle("lose.mp3", "diceking")
yol_song1 = os.path.join("Assets", "soundeffect", "diceking", "song1.mp3")
yol_bossfight = os.path.join("Assets", "soundeffect", "diceking", "bossfight.mp3")

muzik_seviyesi = 50
sfx_seviyesi = 50
suanki_muzik = ""

def os_ses_oynat(ses):
    if ses:
        ses.set_volume(os_config.os_sistem_sesi / 100)
        ses.play()

def oyun_ses_oynat(ses):
    if ses:
        ses.set_volume(sfx_seviyesi / 100)
        ses.play()

def muzik_baslat(isim, yol):
    global suanki_muzik
    if suanki_muzik != isim:
        try:
            pygame.mixer.music.load(yol)
            pygame.mixer.music.set_volume(muzik_seviyesi / 100)
            pygame.mixer.music.play(-1)
            suanki_muzik = isim
        except:
            pass

def muzik_durdur():
    global suanki_muzik
    pygame.mixer.music.stop()
    suanki_muzik = ""

# --- YARDIMCI FONKSİYONLAR ---
def ikon_ciz(yuzey, rect, img, ad, ikon_id=""):
    if secili_ikon == ikon_id and ikon_id != "":
        secim_yuzey = pygame.Surface((80,100), pygame.SRCALPHA)
        secim_yuzey.fill((0,120,215,100))
        yuzey.blit(secim_yuzey, (rect.x-10, rect.y-10))
    yuzey.blit(img, (rect.x, rect.y))
    g_yazi = os_font.render(ad, True, SIYAH)
    yazi = os_font.render(ad, True, BEYAZ)
    t_x = rect.x + (rect.width - yazi.get_width()) // 2
    t_y = rect.y + 65
    yuzey.blit(g_yazi, (t_x+1, t_y+1))
    yuzey.blit(yazi, (t_x, t_y))

def get_pencere_baslik(p):
    return {
        "ZAR": "Zar Krali",
        "OYUNLAR": os_config.txt("Oyunlar", "Games"),
        "MAYIN": os_config.txt("Mayin Tarlasi", "Minesweeper"),
        "TARAYICI": "Internet Explorer",
        "NOT": os_config.txt("Not Defteri", "Notepad"),
        "DUVAR": os_config.txt("Duvar Kagidi", "Wallpaper"),
        "HESAP": os_config.txt("Hesap Makinesi", "Calculator"),
        "AYAR": os_config.txt("Ayarlar", "Settings"),
        "HL3": "Half-Life 3",
        "KAYIP": "Kayip Ruh",
        "BILGISAYAR": os_config.txt("Bilgisayarim", "My Computer"),
        "COP": os_config.txt("Cop Kutusu", "Recycle Bin"),
        "KAMERA": "Kamera"
    }.get(p, "Pencere")

def sarsinti_yarat(sure, guc):
    global ekran_sarsinti_suresi, ekran_sarsinti_gucu
    ekran_sarsinti_suresi = sure
    ekran_sarsinti_gucu = guc

def flas_yarat(sure, renk):
    global flas_suresi, flas_renk
    flas_suresi = sure
    flas_renk = renk

def parcacik_ekle(x, y, renk, adet=5):
    for _ in range(adet):
        parcaciklar.append({
            "x": x, "y": y,
            "hx": random.uniform(-5,5),
            "hy": random.uniform(-5,5),
            "o": random.randint(15,35),
            "r": renk,
            "b": random.randint(3,8)
        })

def parcacik_ciz(yuzey):
    for p in parcaciklar[:]:
        p["x"] += p["hx"]
        p["y"] += p["hy"]
        p["o"] -= 1
        if p["o"] <= 0:
            parcaciklar.remove(p)
        else:
            boyut = max(1, int(p["b"] * (p["o"] / 35)))
            pygame.draw.circle(yuzey, p["r"], (int(p["x"]), int(p["y"])), boyut)

def zar_ciz(yuzey, x, y, sayi):
    boyut = 75
    parlama = pygame.Surface((boyut+10, boyut+10), pygame.SRCALPHA)
    pygame.draw.circle(parlama, (255,255,200,40), (boyut//2+5, boyut//2+5), boyut//2+5)
    yuzey.blit(parlama, (x - boyut//2 - 5, y - boyut//2 - 5))
    rect = pygame.Rect(x - boyut//2, y - boyut//2, boyut, boyut)
    pygame.draw.rect(yuzey, BEYAZ, rect, border_radius=12)
    pygame.draw.rect(yuzey, SIYAH, rect, 3, border_radius=12)
    if sayi == 0:
        sayi_yazi = zar_font.render("X", True, KIRMIZI)
    else:
        sayi_yazi = zar_font.render(str(sayi), True, SIYAH)
    yuzey.blit(sayi_yazi, sayi_yazi.get_rect(center=(x, y)))

def yeni_oyun_sifirla():
    global not_metni, hesap_metni, oyun_durumu, secili_indeks, ayarlar_indeks, market_indeks
    global can_iksiri_sayisi, hasar_iksiri_sayisi, hasar_iksiri_aktif, tur_iksir_kullandi_mi
    global oyun_ici_durum, aksiyon_indeks, esya_indeks, cubuk_x, cubuk_yon
    global atis_zamani, animasyon_baslangic, atis_durumu, zar_sesi_calindi
    global guncel_cubuk_hiz, yesil_genislik, kirmizi_genislik, oyuncu_can, bot_can, bot_maks_can
    global son_hasar, son_zar, hasar_yazisi_y, hasar_yazisi_metin, hasar_yazisi_renk, hasar_yazisi_goster
    global zar_mevcut_x, zar_mevcut_y, ekran_sarsinti_suresi, ekran_sarsinti_gucu
    global flas_suresi, flas_renk, parcaciklar, secili_bolum, aktif_oynanan_bolum
    global mayin_grid, mayin_gorunum, mayin_durum, mayin_ses_calindi
    global kayipruh_oyuncu_x, kayipruh_oyuncu_y
    global indirme_durumu, indirme_yuzdesi, girilen_sifre
    global os_baslat_acik, os_arka_plan_resmi, odak_pencere, pencere_sirasi
    global suruklenen_pencere, os_ayar_ses_surukleniyor
    global son_tiklama_zamani, son_tiklanan_ikon, secili_ikon, guncel_arka_plan
    global bildirim_metni, bildirim_zamani
    global os_config, suanki_muzik
    global browser_pages
    global glitch_hata_mesajlari, glitch_hata_gosterimi

    not_metni = ""
    hesap_metni = ""
    os_config.not_metni = ""
    os_config.hesap_metni = ""
    oyun_durumu = "ANA_MENU"
    secili_indeks = 0
    ayarlar_indeks = 0
    market_indeks = 0
    can_iksiri_sayisi = 3
    hasar_iksiri_sayisi = 3
    hasar_iksiri_aktif = False
    tur_iksir_kullandi_mi = False
    oyun_ici_durum = "OYUNCU_MENU"
    aksiyon_indeks = 0
    esya_indeks = 0
    cubuk_x = 200
    cubuk_yon = 1
    atis_zamani = 0
    animasyon_baslangic = 0
    atis_durumu = "NORMAL"
    zar_sesi_calindi = False
    guncel_cubuk_hiz = 6
    yesil_genislik = 80
    kirmizi_genislik = 0
    oyuncu_can = 100
    bot_can = 100
    bot_maks_can = 100
    son_hasar = 0
    son_zar = 0
    hasar_yazisi_y = 0
    hasar_yazisi_metin = ""
    hasar_yazisi_renk = BEYAZ
    hasar_yazisi_goster = False
    zar_mevcut_x = 400
    zar_mevcut_y = 450
    ekran_sarsinti_suresi = 0
    ekran_sarsinti_gucu = 0
    flas_suresi = 0
    flas_renk = BEYAZ
    parcaciklar = []
    secili_bolum = 0
    aktif_oynanan_bolum = 1
    mayin_grid = []
    mayin_gorunum = []
    mayin_durum = "Oynuyor"
    mayin_ses_calindi = False
    kayipruh_oyuncu_x = 400
    kayipruh_oyuncu_y = 300
    indirme_durumu = "Yok"
    indirme_yuzdesi = 0.0
    girilen_sifre = ""
    os_baslat_acik = False
    os_arka_plan_resmi = None
    odak_pencere = None
    pencere_sirasi = []
    suruklenen_pencere = None
    os_ayar_ses_surukleniyor = False
    son_tiklama_zamani = 0
    son_tiklanan_ikon = None
    secili_ikon = None
    guncel_arka_plan = arka_plan_main
    bildirim_metni = ""
    bildirim_zamani = 0
    suanki_muzik = ""
    glitch_hata_mesajlari = []
    glitch_hata_gosterimi = False
    os_config.lost_soul_cildirdi = False
    os_config.lost_soul_cildirdi_zamani = 0

    for k in pencere_durumlari:
        pencere_durumlari[k]["acik"] = False

    browser_pages.secili_mail = None
    browser_pages.tarayici_sekme = "Google"
    browser_pages.tarayici_scroll = 0
    browser_pages.tarayici_arama_metni = ""
    browser_pages.gelen_kutusu = [
        {"gonderen": "Trendyol", "konu_tr": "Sepetinizdeki urunlerin fiyati dustu!", "konu_en": "Prices dropped in your cart!", "icerik_tr": "Hemen sitemize girip sepetinizi onaylayin.\nKampanyalar cok kisa sureli!", "icerik_en": "Check your cart now.", "yeni": False},
        {"gonderen": "Steam", "konu_tr": "Istek listenizdeki oyunlarda %50 indirim", "konu_en": "50% off on your wishlist", "icerik_tr": "Zar Krali ve bircok oyunda inanilmaz bahar indirimleri basladi.", "icerik_en": "Incredible spring sales have started for Dice King.", "yeni": False},
        {"gonderen": "Garanti Bankasi", "konu_tr": "Hesap ozetiniz hazir", "konu_en": "Your account statement is ready", "icerik_tr": "Sayin musterimiz, Mart ayi hesap ozetiniz ekte sunulmustur.\nDetaylar icin mobil uygulamayi ziyaret edin.", "icerik_en": "Dear customer, your March account statement is attached.", "yeni": True},
        {"gonderen": "Kargo Takip", "konu_tr": "Paketiniz yolda", "konu_en": "Your package is on the way", "icerik_tr": "Siparis numaraniz: 123456\nTahmini teslimat: 2 is gunu icerisinde.", "icerik_en": "Order number: 123456\nEstimated delivery within 2 business days.", "yeni": True},
        {"gonderen": "LinkedIn", "konu_tr": "Sizin icin 5 yeni is ilani", "konu_en": "5 new job offers for you", "icerik_tr": "Profilinize uygun yeni is ilanlari listelendi.\nHemen inceleyin ve basvurun.", "icerik_en": "New job offers matching your profile are listed.\nCheck them now.", "yeni": True},
        {"gonderen": "Netflix", "konu_tr": "Yeni sezon geliyor!", "konu_en": "New season coming!", "icerik_tr": "En cok izlediginiz dizinin yeni sezonu 15 Nisan'da yayinda.\nHatirlatma ayarlayin.", "icerik_en": "The new season of your favorite show is coming on April 15.\nSet a reminder.", "yeni": True},
        {"gonderen": "Spotify", "konu_tr": "Haftalik keşif listesi", "konu_en": "Weekly discovery playlist", "icerik_tr": "Bu hafta sizin icin secilen sarkilar listelendi.\nDinlemeye baslayin.", "icerik_en": "Your weekly discovery playlist is ready.\nStart listening.", "yeni": True}
    ]
    os_config.lost_soul_mail_zamani = 0
    os_config.lost_soul_mail_bekleniyor = False
    browser_pages.chat_dosya_gonderildi = False
    muzik_durdur()

# --- MAYIN TARLASI ---
def mayin_baslat():
    global mayin_grid, mayin_gorunum, mayin_durum, mayin_ses_calindi
    mayin_durum = "Oynuyor"
    mayin_ses_calindi = False
    mayin_grid = [[0 for _ in range(10)] for _ in range(10)]
    mayin_gorunum = [[0 for _ in range(10)] for _ in range(10)]
    m = 0
    while m < 10:
        r, c = random.randint(0,9), random.randint(0,9)
        if mayin_grid[r][c] != -1:
            mayin_grid[r][c] = -1
            m += 1
    for r in range(10):
        for c in range(10):
            if mayin_grid[r][c] == -1:
                continue
            say = 0
            for dr in [-1,0,1]:
                for dc in [-1,0,1]:
                    if 0 <= r+dr < 10 and 0 <= c+dc < 10:
                        if mayin_grid[r+dr][c+dc] == -1:
                            say += 1
            mayin_grid[r][c] = say
    if ms_start:
        ms_start.set_volume(0.02 * (os_config.os_sistem_sesi / 100))
        ms_start.play()

def mayin_ac(r, c):
    global mayin_durum, mayin_ses_calindi
    if mayin_gorunum[r][c] != 0 or mayin_durum != "Oynuyor":
        return
    mayin_gorunum[r][c] = 1
    if ms_click:
        ms_click.set_volume(0.02 * (os_config.os_sistem_sesi / 100))
        ms_click.play()
    if mayin_grid[r][c] == -1:
        mayin_durum = "Kaybettin"
        for ir in range(10):
            for ic in range(10):
                if mayin_grid[ir][ic] == -1:
                    mayin_gorunum[ir][ic] = 1
        if not mayin_ses_calindi:
            if ms_lose:
                ms_lose.set_volume(0.02 * (os_config.os_sistem_sesi / 100))
                ms_lose.play()
            mayin_ses_calindi = True
    elif mayin_grid[r][c] == 0:
        for dr in [-1,0,1]:
            for dc in [-1,0,1]:
                if 0 <= r+dr < 10 and 0 <= c+dc < 10:
                    mayin_ac(r+dr, c+dc)
    if mayin_durum == "Oynuyor":
        acilan = sum(satir.count(1) for satir in mayin_gorunum)
        if acilan == 90:
            mayin_durum = "Kazandin!"
            if not mayin_ses_calindi:
                if ms_win:
                    ms_win.set_volume(0.02 * (os_config.os_sistem_sesi / 100))
                    ms_win.play()
                mayin_ses_calindi = True

# --- ZAR KRALI ÇİZİM FONKSİYONLARI (kısa) ---
def zk_ana_menuyu_ciz(yuzey):
    baslangic_y = 310
    for i, m in enumerate([os_config.txt("Oyna","Play"), os_config.txt("Market","Shop"), os_config.txt("Ayarlar","Settings"), os_config.txt("Cikis","Exit")]):
        renk = KIRMIZI if i == secili_indeks else TURUNCU
        yazi = font.render(m, True, renk)
        yuzey.blit(yazi, yazi.get_rect(center=(400, baslangic_y + i*50)))

def zk_ayarlari_ciz(yuzey):
    yuzey.blit(font.render(os_config.txt("AYARLAR","SETTINGS"), True, TURUNCU), font.render(os_config.txt("AYARLAR","SETTINGS"), True, TURUNCU).get_rect(center=(400,80)))
    ayarlar_menuler = [os_config.txt("Muzik Sesi","Music Vol."), os_config.txt("Efekt Sesi","SFX Vol."), os_config.txt("Geri","Back")]
    for i, m in enumerate(ayarlar_menuler):
        renk = KIRMIZI if i == ayarlar_indeks else TURUNCU
        if i < 2:
            deger = muzik_seviyesi if i==0 else sfx_seviyesi
            yazi = font.render(f"{m}: %{deger}", True, renk)
        else:
            yazi = font.render(m, True, renk)
        yuzey.blit(yazi, yazi.get_rect(center=(400, 170 + i*120)))
        if i < 2:
            pygame.draw.rect(yuzey, GRI, (250, 210 + i*120, 300, 10))
            pygame.draw.rect(yuzey, KIRMIZI, (250, 210 + i*120, int((deger/100)*300), 10))
            pygame.draw.circle(yuzey, renk, (250 + int((deger/100)*300), 215 + i*120), 12)

def zk_marketi_ciz(yuzey):
    yuzey.blit(font.render(os_config.txt("DEMIRCI MARKETHANE","BLACKSMITH SHOP"), True, SARI), font.render(os_config.txt("DEMIRCI MARKETHANE","BLACKSMITH SHOP"), True, SARI).get_rect(center=(400,80)))
    yuzey.blit(font.render(f"{os_config.txt('Mevcut Altin','Gold')}: {os_config.toplam_altin}", True, TURUNCU), font.render(f"{os_config.txt('Mevcut Altin','Gold')}: {os_config.toplam_altin}", True, TURUNCU).get_rect(center=(400,130)))
    market_menuler = [os_config.txt("Zar Guclendirici (50 Altin)","Dice Buff (50G)"), os_config.txt("Alan Genisletici (70 Altin)","Area Expand (70G)"), os_config.txt("Can Iksiri (30 Altin)","HP Pot (30G)"), os_config.txt("Hasar Iksiri (40 Altin)","DMG Pot (40G)"), os_config.txt("Geri","Back")]
    for i, m in enumerate(market_menuler):
        renk = KIRMIZI if i == market_indeks else BEYAZ
        yuzey.blit(font.render(m, True, renk), font.render(m, True, renk).get_rect(center=(400, 200 + i*50)))
    yuzey.blit(kucuk_font.render(f"{os_config.txt('Envanter','Inv')} -> {os_config.txt('Can','HP')}: {can_iksiri_sayisi} | {os_config.txt('Hasar','DMG')}: {hasar_iksiri_sayisi}", True, GRI), (200, 480))
    yuzey.blit(kucuk_font.render(f"{os_config.txt('Gelistirmeler','Upgr')} -> Zar Lvl {os_config.zar_seviyesi} | Alan Lvl {os_config.alan_seviyesi}", True, GRI), (200, 510))

def zk_bolum_secim_ciz(yuzey):
    global secili_bolum
    yuzey.blit(font.render(os_config.txt("BOLUM SECIMI","LEVEL SELECT"), True, TURUNCU), font.render(os_config.txt("BOLUM SECIMI","LEVEL SELECT"), True, TURUNCU).get_rect(center=(400,120)))
    for i in range(5):
        rect = pygame.Rect((800-580)//2 + i*120, 250, 90,90)
        if i < os_config.kilit_acik_bolum:
            if boss_avatarlari[i] and boss_avatarlari[i].get_width() > 0:
                yuzey.blit(boss_avatarlari[i], rect)
            else:
                pygame.draw.rect(yuzey, SIYAH, rect)
            renk = KIRMIZI if i == secili_bolum else TURUNCU
            pygame.draw.rect(yuzey, renk, rect, 4 if i == secili_bolum else 2)
            yazi = font.render(str(i+1), True, BEYAZ)
        else:
            pygame.draw.rect(yuzey, SIYAH, rect)
            yazi = kucuk_font.render(os_config.txt("Kilit","Lock"), True, GRI)
        yuzey.blit(yazi, yazi.get_rect(center=rect.center))

def zk_oyun_ciz(yuzey, suan):
    global cubuk_x, cubuk_yon, oyun_ici_durum, zar_mevcut_x, zar_mevcut_y
    global hasar_yazisi_y, hasar_yazisi_goster

    if oyun_ici_durum != "OYUN_BITTI":
        pygame.draw.rect(yuzey, GRI, (20,20,200,20), border_radius=4)
        pygame.draw.rect(yuzey, YESIL if oyuncu_can > 50 else KIRMIZI, (20,20, int(oyuncu_can*2), 20), border_radius=4)
        yuzey.blit(kucuk_font.render(f"{os_config.txt('Oyuncu','Player')} HP: {oyuncu_can}/100", True, BEYAZ), (20,5))
        pygame.draw.rect(yuzey, GRI, (580,20,200,20), border_radius=4)
        bar = int((bot_can / bot_maks_can) * 200)
        pygame.draw.rect(yuzey, YESIL if bot_can > bot_maks_can/2 else KIRMIZI, (580,20, bar,20), border_radius=4)
        yuzey.blit(kucuk_font.render(f"Bot HP: {bot_can}/{bot_maks_can}", True, BEYAZ), (580,5))

        yuzey.blit(masa_resmi, (200,400))
        y_sapma = math.sin(suan * 0.005) * 15
        y_sapma_bot = math.sin((suan+500) * 0.005) * 15

        if oyun_ici_durum == "OYUNCU_ZAR_DONUYOR":
            yuzey.blit(el_acik, (40,240))
        else:
            yuzey.blit(el_kapali, (40,240 + y_sapma))
        if oyun_ici_durum == "BOT_ZAR_DONUYOR":
            yuzey.blit(bot_el_acik, (540,240))
        else:
            yuzey.blit(bot_el_kapali, (540,240 + y_sapma_bot))

    if oyun_ici_durum == "OYUNCU_MENU":
        for i, sec in enumerate([os_config.txt("Zar At","Roll"), os_config.txt("Esya","Item")]):
            renk = KIRMIZI if i == aksiyon_indeks else BEYAZ
            yuzey.blit(font.render(sec, True, renk), font.render(sec, True, renk).get_rect(center=(400, 470 + i*50)))
    elif oyun_ici_durum == "OYUNCU_ESYA":
        for i, sec in enumerate([os_config.txt("Can Iksiri","HP Pot"), os_config.txt("Hasar Iksiri","DMG Pot"), os_config.txt("Geri","Back")]):
            renk = KIRMIZI if i == esya_indeks else BEYAZ
            if i in [0,1] and tur_iksir_kullandi_mi:
                renk = GRI
            yuzey.blit(font.render(sec, True, renk), font.render(sec, True, renk).get_rect(center=(400, 440 + i*45)))
    elif oyun_ici_durum == "OYUNCU_BEKLIYOR":
        bar_sol = 200
        bar_sag = 600
        bar_orta = 400
        yesil_sol = bar_orta - yesil_genislik//2
        yesil_sag = bar_orta + yesil_genislik//2
        kirmizi_sol_sol = yesil_sol - kirmizi_genislik
        kirmizi_sol_sag = yesil_sol
        kirmizi_sag_sol = yesil_sag
        kirmizi_sag_sag = yesil_sag + kirmizi_genislik

        pygame.draw.rect(yuzey, SIYAH, (bar_sol-2, 518, 404, 34), border_radius=5)
        pygame.draw.rect(yuzey, GRI, (bar_sol, 520, 400, 30), border_radius=5)
        if kirmizi_genislik > 0:
            pygame.draw.rect(yuzey, KIRMIZI, (kirmizi_sol_sol, 520, kirmizi_genislik, 30))
            pygame.draw.rect(yuzey, KIRMIZI, (kirmizi_sag_sol, 520, kirmizi_genislik, 30))
        pygame.draw.rect(yuzey, YESIL, (yesil_sol, 520, yesil_genislik, 30))
        pygame.draw.rect(yuzey, SARI, (bar_orta-2, 520, 4, 30))

        cubuk_x += guncel_cubuk_hiz * cubuk_yon
        if cubuk_x >= bar_sag - 8:
            cubuk_yon = -1
        elif cubuk_x <= bar_sol:
            cubuk_yon = 1
        pygame.draw.rect(yuzey, BEYAZ, (cubuk_x, 515, 8, 40), border_radius=3)

        if hasar_iksiri_aktif:
            yanip = abs(math.sin(suan * 0.005)) * 255
            buff = font.render("HASAR BUFF AKTIF (+%20)", True, MOR)
            buff.set_alpha(int(yanip))
            yuzey.blit(buff, buff.get_rect(center=(400,120)))
        else:
            yuzey.blit(font.render("TAM ZAMANINDA SPACE'E BAS!", True, TURUNCU), font.render("TAM ZAMANINDA SPACE'E BAS!", True, TURUNCU).get_rect(center=(400,120)))

    elif oyun_ici_durum in ["OYUNCU_SONUC", "BOT_SONUC", "OYUNCU_ZAR_DONUYOR", "BOT_ZAR_DONUYOR"]:
        if oyun_ici_durum in ["OYUNCU_ZAR_DONUYOR","BOT_ZAR_DONUYOR"]:
            oran = min(1.0, (suan - animasyon_baslangic) / 1000)
            if oyun_ici_durum == "OYUNCU_ZAR_DONUYOR":
                x1, y1 = 140, 350
                x2, y2 = 400, 450
            else:
                x1, y1 = 660, 350
                x2, y2 = 400, 450
            zar_mevcut_x = int(x1 + (x2 - x1) * oran)
            zar_mevcut_y = int(y1 + (y2 - y1) * oran) - int(math.sin(oran * math.pi) * 120)
            goster = random.randint(1,6)
        else:
            goster = son_zar if son_zar != 0 else 0
        zar_ciz(yuzey, zar_mevcut_x, zar_mevcut_y, goster)
        if hasar_yazisi_goster:
            hasar_yazisi_y -= 2
            yuzey.blit(font.render(hasar_yazisi_metin, True, hasar_yazisi_renk), font.render(hasar_yazisi_metin, True, hasar_yazisi_renk).get_rect(center=(400, hasar_yazisi_y)))

    elif oyun_ici_durum == "OYUN_BITTI":
        if bot_can <= 0:
            mesaj = font.render(os_config.txt("TEBRIKLER! KAZANDIN", "CONGRATS! YOU WIN"), True, YESIL)
            alt = kucuk_font.render(os_config.txt(f"+{aktif_oynanan_bolum * 35} Altin! [SPACE]: Menuye Don", f"+{aktif_oynanan_bolum * 35} Gold! [SPACE]: Back"), True, BEYAZ)
        else:
            mesaj = font.render(os_config.txt("KAYBETTINIZ! BOT KAZANDI", "YOU LOST! BOT WINS"), True, KIRMIZI)
            alt = kucuk_font.render(os_config.txt("[SPACE]: Tekrar Dene", "[SPACE]: Try Again"), True, BEYAZ)
        yuzey.blit(mesaj, mesaj.get_rect(center=(400,230)))
        yuzey.blit(alt, alt.get_rect(center=(400,290)))

# ============================================================
#                     ANA DÖNGÜ BAŞLIYOR
# ============================================================
calisiyor = True
btn_yeni = pygame.Rect(OS_GENISLIK//2 - 150, 300, 300, 60)
btn_devam = pygame.Rect(OS_GENISLIK//2 - 150, 380, 300, 60)
btn_cikis = pygame.Rect(OS_GENISLIK//2 - 150, 460, 300, 60)
while calisiyor:
    mouse_x, mouse_y = pygame.mouse.get_pos()
    suan = pygame.time.get_ticks()

    story_system.update_story(suan)

    # --- AGRESİF DESKTOP MADNESS ZAMAN AŞIMI KONTROLÜ ---
    if getattr(os_config, "lost_soul_cildirdi", False) and suan - getattr(os_config, "lost_soul_cildirdi_zamani", 0) >= 10000:
        if os.path.exists("savegame.json"):
            try:
                os.remove("savegame.json")
            except:
                pass
        if os.path.exists(os.path.join("Assets", "desktop", "code.txt")):
            try:
                os.remove(os.path.join("Assets", "desktop", "code.txt"))
            except:
                pass
        pygame.quit()
        sys.exit()

    # --- BOOT EKRANI ---
    if sistem_durumu == "BOOT":
        if boot_baslangic == 0:
            boot_baslangic = suan
            os_ses_oynat(ses_startup)

        ekran.fill((0, 100, 200))
        logo = pygame.transform.scale(ikon_start, (150, 150))
        logo_rect = logo.get_rect(center=(OS_GENISLIK//2, OS_YUKSEKLIK//2 - 50))
        ekran.blit(logo, logo_rect)

        alt_yazi = os_buyuk_font.render("", True, (200, 200, 200))
        alt_rect = alt_yazi.get_rect(center=(OS_GENISLIK//2, OS_YUKSEKLIK//2 + 120))
        ekran.blit(alt_yazi, alt_rect)

        nokta_sayisi = ((suan - boot_baslangic) // 500) % 4
        noktalar = "." * nokta_sayisi
        yukleniyor_yazi = os_font.render(f"Yükleniyor{noktalar}", True, (180, 180, 180))
        yuk_rect = yukleniyor_yazi.get_rect(center=(OS_GENISLIK//2, OS_YUKSEKLIK//2 + 180))
        ekran.blit(yukleniyor_yazi, yuk_rect)

        pygame.display.update()

        if suan - boot_baslangic > 8000:
            sistem_durumu = "LOGIN"
            boot_baslangic = 0
            pygame.mixer.stop()
        continue

    # --- ZAMANLAYICI: 10 saniye sonra mail (Bölüm 2 için) ---
    if os_config.lost_soul_mail_bekleniyor and suan >= os_config.lost_soul_mail_zamani:
        os_config.lost_soul_mail_bekleniyor = False
        browser_pages.gelen_kutusu.insert(0, {
            "gonderen": "Teknik Destek",
            "konu_tr": "Kayıp Ruh - Yeni Sürüm (Güncelleme)",
            "konu_en": "Lost Soul - New Version (Update)",
            "icerik_tr": "Sayın kullanıcı, oyunun güncel sürümü hazır.\nAşağıdaki bağlantıdan indirebilirsiniz:\n[İNDİR]",
            "icerik_en": "Dear user, the updated version of the game is ready.\nYou can download it from the link below:\n[DOWNLOAD]",
            "yeni": True,
            "link": True
        })
        os_ses_oynat(ses_notify)
        bildirim_metni = os_config.txt("Yeni güncelleme maili geldi! Gmail'i kontrol edin.", "New update mail arrived! Check Gmail.")
        bildirim_zamani = suan

    # --- İNDİRME SİSTEMİ ---
    if indirme_durumu == "Indiriliyor":
        indirme_yuzdesi += 0.3
        if indirme_yuzdesi >= 100:
            indirme_durumu = "Tamamlandi"
            os_config.oyun_kayipruh_indirildi = True
            if browser_pages.chat_dosya_gonderildi:
                os_config.lost_soul_unlocked = True
                os_config.lost_soul_hatali = False
                os_config.lost_soul_ikinci_bolum = True
                os_config.kayit_sistemi.kaydet()
                bildirim_metni = os_config.txt("Yeni oyun sürümü indirildi! Artık oynayabilirsiniz.", "New game version downloaded! You can play now.")
                bildirim_zamani = suan
            else:
                bildirim_metni = os_config.txt("Kayıp Ruh oyunu indirildi.", "Lost Soul game downloaded.")
                bildirim_zamani = suan

    if bildirim_metni and suan - bildirim_zamani > bildirim_suresi:
        bildirim_metni = ""

    # --- ZAR KRALI MÜZİK ---
    if pencere_durumlari["ZAR"]["acik"]:
        if suanki_muzik != "song1" and oyun_durumu != "ANA_MENU":
            if oyun_durumu in ["BOLUM_SECIMI", "OYUN", "MARKET", "AYARLAR"]:
                muzik_baslat("song1", yol_song1)
    else:
        if suanki_muzik == "song1":
            muzik_durdur()

    # --- ZAR KRALI OYUN İÇİ MANTIĞI ---
    if pencere_durumlari["ZAR"]["acik"] and oyun_durumu == "OYUN":
        if oyun_ici_durum == "OYUNCU_ZAR_DONUYOR":
            oran = min(1.0, (suan - animasyon_baslangic) / 1000)
            if oran > 0.8 and not zar_sesi_calindi:
                oyun_ses_oynat(ses_diceroll)
                zar_sesi_calindi = True
            if oran >= 1.0:
                oyun_ici_durum = "OYUNCU_SONUC"
                bot_can -= son_hasar
                if bot_can < 0: bot_can = 0
                atis_zamani = suan
                hasar_yazisi_y = 350
                hasar_yazisi_goster = True
                if son_hasar > 0:
                    oyun_ses_oynat(ses_dmg)
                if atis_durumu == "KRITIK":
                    sarsinti_yarat(18,10); flas_yarat(4,SARI); parcacik_ekle(400,350,SARI,30)
                elif atis_durumu == "MUKEMMEL":
                    sarsinti_yarat(10,5); flas_yarat(2,YESIL); parcacik_ekle(400,350,YESIL,15)
        elif oyun_ici_durum == "OYUNCU_SONUC":
            if hasar_yazisi_goster:
                hasar_yazisi_y -= 2
            if suan - atis_zamani > 2000:
                hasar_yazisi_goster = False
                if bot_can <= 0:
                    oyun_ici_durum = "OYUN_BITTI"
                    os_config.toplam_altin += aktif_oynanan_bolum * 35
                    oyun_ses_oynat(dk_ses_win)
                    if aktif_oynanan_bolum == os_config.kilit_acik_bolum and os_config.kilit_acik_bolum < 5:
                        os_config.kilit_acik_bolum += 1
                    if os_config.kilit_acik_bolum == 3 and os_config.hikaye_asamasi == 1 and not os_config.mail_geldi:
                        os_config.mail_geldi = True
                        os_config.hikaye_asamasi = 2
                        os_ses_oynat(ses_notify)
                        browser_pages.gelen_kutusu.insert(0, {
                            "gonderen": "GIZLI YONETICI",
                            "konu_tr": "TEST ONAYLANDI.",
                            "konu_en": "TEST APPROVED.",
                            "icerik_tr": "Test asamasi basariyla tamamlandi. \nSistemde gizli olan 'KayipRuh' oyununu indir.\nDIKKAT: Arkana bakma.",
                            "icerik_en": "Test phase completed. \nDownload 'LostSoul' game below.\nWARNING: Don't look behind.",
                            "yeni": True
                        })
                        story_system.dialog_baslat(os_config.txt("Aha! Bir mail geldi galiba...", "Aha! A mail arrived..."))
                else:
                    oyun_ici_durum = "BOT_BEKLIYOR"
                    atis_zamani = suan
        elif oyun_ici_durum == "BOT_BEKLIYOR":
            if suan - atis_zamani > 1000:
                bot_zar_sans = random.random()
                mukemmel_ihtimali = 0.20 + (os_config.kilit_acik_bolum * 0.05)
                if bot_zar_sans < mukemmel_ihtimali:
                    son_zar = random.randint(4,6)
                    atis_durumu = "MUKEMMEL"
                else:
                    son_zar = random.randint(1,4)
                    atis_durumu = "NORMAL"
                son_hasar = son_zar * 10
                oyun_ici_durum = "BOT_ZAR_DONUYOR"
                animasyon_baslangic = suan
                zar_sesi_calindi = False
        elif oyun_ici_durum == "BOT_ZAR_DONUYOR":
            oran = min(1.0, (suan - animasyon_baslangic) / 1000)
            if oran > 0.8 and not zar_sesi_calindi:
                oyun_ses_oynat(ses_diceroll)
                zar_sesi_calindi = True
            if oran >= 1.0:
                oyun_ici_durum = "BOT_SONUC"
                oyuncu_can -= son_hasar
                if oyuncu_can < 0: oyuncu_can = 0
                atis_zamani = suan
                hasar_yazisi_y = 350
                hasar_yazisi_goster = True
                hasar_yazisi_metin = f"-{son_hasar} HP"
                hasar_yazisi_renk = KIRMIZI
                if son_hasar > 0:
                    oyun_ses_oynat(ses_dmg)
                sarsinti_yarat(12,6); flas_yarat(3,KIRMIZI); parcacik_ekle(400,350,KIRMIZI,20)
        elif oyun_ici_durum == "BOT_SONUC":
            if hasar_yazisi_goster:
                hasar_yazisi_y -= 2
            if suan - atis_zamani > 2000:
                hasar_yazisi_goster = False
                if oyuncu_can <= 0:
                    oyun_ici_durum = "OYUN_BITTI"
                    oyun_ses_oynat(dk_ses_lose)
                else:
                    oyun_ici_durum = "OYUNCU_MENU"
                    aksiyon_indeks = 0
                    tur_iksir_kullandi_mi = False

    # --- OLAY YÖNETİMİ ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            os_config.not_metni = not_metni
            os_config.hesap_metni = hesap_metni
            os_config.kayit_sistemi.kaydet()
            calisiyor = False

        if lost_soul_game_instance is not None:
            if lost_soul_game_instance.handle_event(event) == True:
                lost_soul_game_instance.durdur_ses()
                lost_soul_game_instance = None
                pencere_durumlari["KAYIP"]["acik"] = False
                if "KAYIP" in pencere_sirasi:
                    pencere_sirasi.remove("KAYIP")
                continue

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if glitch_hata_gosterimi:
                for i, metin in enumerate(glitch_hata_mesajlari):
                    metin_surf = os_baslik_font.render(metin, True, BEYAZ)
                    x = 100 + i * 150
                    y = 50 + i * 80
                    kapat_rect = pygame.Rect(x + metin_surf.get_width() - 20, y - 10, 20, 20)
                    if kapat_rect.collidepoint(mouse_x, mouse_y):
                        glitch_hata_mesajlari.pop(i)
                        if not glitch_hata_mesajlari:
                            glitch_hata_gosterimi = False
                        break

            if story_system.dialog_aktif:
                if story_system.tikla_gec_veya_kapat():
                    if sistem_durumu == "CUTSCENE" and cutscene_asamasi == 3 and not story_system.dialog_aktif:
                        sistem_durumu = "BOOT"
                        boot_baslangic = 0
                    continue

            if sistem_durumu == "ANA_GIRIS":
                # Yeni Oyun butonu (Bu kısmı koruyoruz, silmeyin)
                if btn_yeni.collidepoint(mouse_x, mouse_y):
                    yeni_oyun_sifirla()
                    os_config.toplam_altin = 100
                    os_config.zar_seviyesi = 1
                    os_config.alan_seviyesi = 1
                    os_config.kilit_acik_bolum = 1
                    os_config.hikaye_asamasi = 0
                    os_config.mail_basvuruldu = False
                    os_config.mail_geldi = False
                    os_config.oyun_kayipruh_indirildi = False
                    os_config.lost_soul_unlocked = False
                    os_config.lost_soul_hatali = False
                    os_config.lost_soul_ikinci_bolum = False
                    os_config.kayit_sistemi.kaydet()
                    sistem_durumu = "CUTSCENE"
                    cutscene_asamasi = 1
                    story_system.dialog_baslat(os_config.txt("Sonunda eve geldim...", "Finally home..."))
                
                # Kayıtlı Oyun butonu (Yeni kontrol eklenmiş güncel devam bloğu)
                elif btn_devam.collidepoint(mouse_x, mouse_y):
                    if os.path.exists("savegame.json"):
                        os_config.kayit_sistemi.yukle()
                        not_metni = os_config.not_metni
                        hesap_metni = os_config.hesap_metni
                        sistem_durumu = "LOGIN"
                        os_ses_oynat(ses_logon)
                
                # Çıkış butonu
                elif btn_cikis.collidepoint(mouse_x, mouse_y):
                    calisiyor = False
                continue

            if sistem_durumu == "CUTSCENE" and not story_system.dialog_aktif:
                if cutscene_asamasi == 1:
                    cutscene_asamasi = 2
                    story_system.dialog_baslat(os_config.txt("Hala is bulamadim...", "Still couldn't find a job..."))
                elif cutscene_asamasi == 2:
                    cutscene_asamasi = 3
                    story_system.dialog_baslat(os_config.txt("Biraz da internetten arastirayim...", "Let's search the internet..."))
                elif cutscene_asamasi == 3:
                    sistem_durumu = "BOOT"
                    boot_baslangic = 0
                continue

            if sistem_durumu == "LOGIN":
                if len(girilen_sifre) >= 5 and pygame.Rect(OS_GENISLIK//2 + 110, OS_YUKSEKLIK//2 + 50, 40, 40).collidepoint(mouse_x, mouse_y):
                    sistem_durumu = "OS"
                    os_ses_oynat(ses_logon)
                continue

            if sistem_durumu == "OS":
                if pencere_durumlari["HL3"]["acik"]:
                    hr = pygame.Rect(pencere_durumlari["HL3"]["x"], pencere_durumlari["HL3"]["y"]-30, 300, 180)
                    if not hr.collidepoint(mouse_x, mouse_y):
                        os_ses_oynat(ses_error)
                    else:
                        kapat = pygame.Rect(pencere_durumlari["HL3"]["x"]+260, pencere_durumlari["HL3"]["y"]-30, 40, 30)
                        ok = pygame.Rect(pencere_durumlari["HL3"]["x"]+100, pencere_durumlari["HL3"]["y"]+100, 100, 30)
                        if kapat.collidepoint(mouse_x, mouse_y) or ok.collidepoint(mouse_x, mouse_y):
                            pencere_durumlari["HL3"]["acik"] = False
                            if "HL3" in pencere_sirasi:
                                pencere_sirasi.remove("HL3")
                    continue

                clk = (suan - son_tiklama_zamani) < 500
                son_tiklama_zamani = suan
                tiklama_yakalandi = False

                if mouse_y >= OS_YUKSEKLIK - 45:
                    tiklama_yakalandi = True

                if os_baslat_acik and pygame.Rect(5, OS_YUKSEKLIK-455, 380, 410).collidepoint(mouse_x, mouse_y):
                    tiklama_yakalandi = True
                    kapat_btn = pygame.Rect(260, OS_YUKSEKLIK-75, 120, 25)
                    if kapat_btn.collidepoint(mouse_x, mouse_y):
                        os_config.not_metni = not_metni
                        os_config.hesap_metni = hesap_metni
                        os_config.kayit_sistemi.kaydet()
                        sistem_durumu = "ANA_GIRIS"
                        muzik_durdur()
                        for k in pencere_durumlari:
                            pencere_durumlari[k]["acik"] = False
                        pencere_sirasi.clear()
                        continue
                elif pygame.Rect(5, OS_YUKSEKLIK-45, 40, 40).collidepoint(mouse_x, mouse_y):
                    os_baslat_acik = not os_baslat_acik
                    tiklama_yakalandi = True
                else:
                    os_baslat_acik = False

                if not tiklama_yakalandi:
                    for p in reversed(pencere_sirasi):
                        info = pencere_durumlari[p]
                        if not info["acik"]:
                            continue
                        w, h = {
                            "ZAR": (800,600), "TARAYICI":(800,600), "KAYIP":(800,600),
                            "DUVAR":(500,400), "NOT":(500,400), "OYUNLAR":(400,300),
                            "MAYIN":(400,400), "HESAP":(250,350), "AYAR":(300,250),
                            "HL3":(300,150), "BILGISAYAR":(400,300), "COP":(400,300),
                            "KAMERA": (320, 240)
                        }.get(p, (400,300))

                        if pygame.Rect(info["x"]+w-40, info["y"]-30, 40, 30).collidepoint(mouse_x, mouse_y):
                            if p == "ZAR":
                                muzik_durdur()
                                oyun_durumu = "ANA_MENU"
                                oyun_ici_durum = "OYUNCU_MENU"
                                guncel_arka_plan = arka_plan_main
                            if p == "KAYIP":
                                if lost_soul_game_instance is not None:
                                    lost_soul_game_instance.durdur_ses()
                                    lost_soul_game_instance = None
                            info["acik"] = False
                            pencere_sirasi.remove(p)
                            tiklama_yakalandi = True
                            break
                        elif pygame.Rect(info["x"], info["y"]-30, w-40, 30).collidepoint(mouse_x, mouse_y):
                            suruklenen_pencere = p
                            surukleme_farki_x = mouse_x - info["x"]
                            surukleme_farki_y = mouse_y - info["y"]
                            pencere_sirasi.remove(p)
                            pencere_sirasi.append(p)
                            tiklama_yakalandi = True
                            break
                        elif pygame.Rect(info["x"], info["y"], w, h).collidepoint(mouse_x, mouse_y):
                            pencere_sirasi.remove(p)
                            pencere_sirasi.append(p)
                            odak_pencere = p

                            if p == "DUVAR":
                                b_y = 20
                                for kagit in duvar_kagitlari:
                                    if pygame.Rect(info["x"]+20, info["y"]+b_y, 120, 80).collidepoint(mouse_x, mouse_y):
                                        os_arka_plan_resmi = kagit["buyuk"]
                                    b_y += 100
                            elif p == "TARAYICI":
                                sekmeler = ["Google", os_config.txt("Haberler","News"), os_config.txt("Is Ilanlari","Jobs"), "Gmail"]
                                for i, s_ad in enumerate(sekmeler):
                                    s_id = ["Google","Haberler","Is Ilanlari","Gmail"][i]
                                    if pygame.Rect(info["x"]+10+i*105, info["y"]+5, 100, 25).collidepoint(mouse_x, mouse_y):
                                        browser_pages.tarayici_sekme = s_id
                                        browser_pages.secili_mail = None
                                        browser_pages.secili_ilan = None
                                        browser_pages.secili_haber = None
                                        break

                                if browser_pages.tarayici_sekme == "Is Ilanlari":
                                    if browser_pages.secili_ilan is None:
                                        yi = 120 + browser_pages.tarayici_scroll
                                        for ad, srk, is_hedef, detay in browser_pages.get_sahte_ilanlar():
                                            if pygame.Rect(info["x"]+20, info["y"]+yi, 760, 50).collidepoint(mouse_x, mouse_y):
                                                browser_pages.secili_ilan = (ad, srk, is_hedef, detay)
                                                if is_hedef and not os_config.mail_basvuruldu:
                                                    story_system.dialog_baslat(os_config.txt("Oyun oynayarak para kazanmak mi? Umarim geri donus yaparlar...", "Earning money by playing games? Hope they reply..."))
                                            yi += 60
                                    else:
                                        if pygame.Rect(info["x"]+30, info["y"]+85, 80, 30).collidepoint(mouse_x, mouse_y):
                                            browser_pages.secili_ilan = None
                                        elif browser_pages.secili_ilan[2] and pygame.Rect(info["x"]+30, info["y"]+180 + len(browser_pages.secili_ilan[3].split("\n"))*20 + 20, 140, 40).collidepoint(mouse_x, mouse_y):
                                            if not os_config.mail_basvuruldu:
                                                os_config.mail_basvuruldu = True
                                                os_config.hikaye_asamasi = 1
                                                os_config.kayit_sistemi.kaydet()
                                                story_system.dialog_baslat(os_config.txt("Geri donus alana kadar Zar Krali oynayayim bari...", "I should play Dice King until they reply..."))
                                            else:
                                                os_ses_oynat(ses_notify)
                                        else:
                                            story_system.dialog_baslat(os_config.txt("Bu iş tecrübe istiyor, başka iş bakmam lazım.", "This job requires experience, I need to look for another."))
                                elif browser_pages.tarayici_sekme == "Haberler":
                                    if browser_pages.secili_haber is None:
                                        yh = 120 + browser_pages.tarayici_scroll
                                        for bas, ic, detay in browser_pages.get_sahte_haberler():
                                            if pygame.Rect(info["x"]+20, info["y"]+yh, 760, 60).collidepoint(mouse_x, mouse_y):
                                                browser_pages.secili_haber = (bas, ic, detay)
                                            yh += 70
                                    else:
                                        if pygame.Rect(info["x"]+30, info["y"]+85, 80, 30).collidepoint(mouse_x, mouse_y):
                                            browser_pages.secili_haber = None
                                elif browser_pages.tarayici_sekme == "Gmail":
                                    if browser_pages.secili_mail is None:
                                        ym = 120
                                        for mail in browser_pages.gelen_kutusu:
                                            if pygame.Rect(info["x"]+20, info["y"]+ym, 760, 40).collidepoint(mouse_x, mouse_y):
                                                browser_pages.secili_mail = mail
                                                mail["yeni"] = False
                                                break
                                            ym += 50
                                    else:
                                        if pygame.Rect(info["x"]+170, info["y"]+110, 80, 30).collidepoint(mouse_x, mouse_y):
                                            browser_pages.secili_mail = None
                                        elif browser_pages.secili_mail["gonderen"] == "GIZLI YONETICI" and indirme_durumu == "Yok":
                                            icerik = os_config.txt(browser_pages.secili_mail["icerik_tr"], browser_pages.secili_mail.get("icerik_en",""))
                                            satir_sayisi = len(icerik.split("\n"))
                                            yc = 240 + satir_sayisi * 25
                                            if pygame.Rect(info["x"]+180, info["y"]+yc+30, 150, 40).collidepoint(mouse_x, mouse_y):
                                                indirme_durumu = "Indiriliyor"
                                                indirme_yuzdesi = 0
                                        elif browser_pages.secili_mail.get("link", False) and indirme_durumu == "Yok":
                                            icerik = os_config.txt(browser_pages.secili_mail["icerik_tr"], browser_pages.secili_mail.get("icerik_en",""))
                                            satir_sayisi = len(icerik.split("\n"))
                                            yc = 240 + satir_sayisi * 25
                                            if pygame.Rect(info["x"]+180, info["y"]+yc+30, 150, 40).collidepoint(mouse_x, mouse_y):
                                                indirme_durumu = "Indiriliyor"
                                                indirme_yuzdesi = 0
                                                browser_pages.chat_dosya_gonderildi = True

                            elif p == "AYAR":
                                if pygame.Rect(info["x"]+50, info["y"]+80, 200, 20).collidepoint(mouse_x, mouse_y):
                                    os_ayar_ses_surukleniyor = True
                                if pygame.Rect(info["x"]+100, info["y"]+150, 100, 40).collidepoint(mouse_x, mouse_y):
                                    os_config.os_dil = "EN" if os_config.os_dil == "TR" else "TR"
                                tam_ekran_check = pygame.Rect(info["x"]+50, info["y"]+200, 20, 20)
                                if tam_ekran_check.collidepoint(mouse_x, mouse_y):
                                    os_config.tam_ekran = not getattr(os_config, "tam_ekran", False)
                                    if os_config.tam_ekran:
                                        ekran = pygame.display.set_mode((OS_GENISLIK, OS_YUKSEKLIK), pygame.FULLSCREEN)
                                    else:
                                        ekran = pygame.display.set_mode((OS_GENISLIK, OS_YUKSEKLIK))
                                    if lost_soul_game_instance is not None:
                                        lost_soul_game_instance.genislik = OS_GENISLIK
                                        lost_soul_game_instance.yukseklik = OS_YUKSEKLIK
                            elif p == "HESAP":
                                butonlar = ["7","8","9","+","4","5","6","-","1","2","3","*","C","0","=","/"]
                                hx, hy = 10, 80
                                for idx, b in enumerate(butonlar):
                                    if pygame.Rect(info["x"]+hx, info["y"]+hy, 50, 50).collidepoint(mouse_x, mouse_y):
                                        if b == "C":
                                            hesap_metni = ""
                                        elif b == "=":
                                            try:
                                                hesap_metni = str(eval(hesap_metni))[:12]
                                            except:
                                                hesap_metni = "Hata"
                                        else:
                                            if hesap_metni == "Hata":
                                                hesap_metni = ""
                                            if len(hesap_metni) < 12:
                                                hesap_metni += b
                                    hx += 60
                                    if (idx+1) % 4 == 0:
                                        hx = 10
                                        hy += 60
                            elif p == "OYUNLAR":
                                if clk and son_tiklanan_ikon == "KLASOR_ZAR" and pygame.Rect(info["x"]+30, info["y"]+30, 60, 60).collidepoint(mouse_x, mouse_y):
                                    pencere_durumlari["ZAR"]["acik"] = True
                                    if "ZAR" not in pencere_sirasi:
                                        pencere_sirasi.append("ZAR")
                                    muzik_baslat("song1", yol_song1)
                                    son_tiklanan_ikon = None
                                elif pygame.Rect(info["x"]+30, info["y"]+30, 60, 60).collidepoint(mouse_x, mouse_y):
                                    son_tiklanan_ikon = "KLASOR_ZAR"

                                if clk and son_tiklanan_ikon == "KLASOR_MAYIN" and pygame.Rect(info["x"]+120, info["y"]+30, 60, 60).collidepoint(mouse_x, mouse_y):
                                    pencere_durumlari["MAYIN"]["acik"] = True
                                    if "MAYIN" not in pencere_sirasi:
                                        pencere_sirasi.append("MAYIN")
                                    mayin_baslat()
                                    son_tiklanan_ikon = None
                                elif pygame.Rect(info["x"]+120, info["y"]+30, 60, 60).collidepoint(mouse_x, mouse_y):
                                    son_tiklanan_ikon = "KLASOR_MAYIN"

                                if clk and son_tiklanan_ikon == "KLASOR_HL3" and pygame.Rect(info["x"]+210, info["y"]+30, 60, 60).collidepoint(mouse_x, mouse_y):
                                    pencere_durumlari["HL3"]["acik"] = True
                                    if "HL3" not in pencere_sirasi:
                                        pencere_sirasi.append("HL3")
                                    os_ses_oynat(ses_error)
                                    son_tiklanan_ikon = None
                                elif pygame.Rect(info["x"]+210, info["y"]+30, 60, 60).collidepoint(mouse_x, mouse_y):
                                    son_tiklanan_ikon = "KLASOR_HL3"

                                if os_config.oyun_kayipruh_indirildi and clk and son_tiklanan_ikon == "KLASOR_KAYIPRUH" and pygame.Rect(info["x"]+300, info["y"]+30, 60, 60).collidepoint(mouse_x, mouse_y):
                                    pencere_durumlari["KAYIP"]["acik"] = True
                                    if "KAYIP" not in pencere_sirasi:
                                        pencere_sirasi.append("KAYIP")
                                    if LOST_SOUL_AVAILABLE and lost_soul_game_instance is None:
                                        if os_config.lost_soul_hatali or os_config.lost_soul_unlocked:
                                            lost_soul_game_instance = lost_soul_game.LostSoulGame(800, 600, bolum=2)
                                        else:
                                            lost_soul_game_instance = lost_soul_game.LostSoulGame(800, 600, bolum=1)
                                    son_tiklanan_ikon = None
                                elif os_config.oyun_kayipruh_indirildi and pygame.Rect(info["x"]+300, info["y"]+30, 60, 60).collidepoint(mouse_x, mouse_y):
                                    son_tiklanan_ikon = "KLASOR_KAYIPRUH"
                            elif p == "MAYIN" and mayin_durum == "Oynuyor":
                                mc = (mouse_x - info["x"]) // 40
                                mr = (mouse_y - info["y"]) // 40
                                if 0 <= mr < 10 and 0 <= mc < 10:
                                    mayin_ac(mr, mc)

                            tiklama_yakalandi = True
                            break

                if not tiklama_yakalandi:
                    ikon_list = [
                        ("COMPUTER", pygame.Rect(20,20,60,60), ikon_computer, os_config.txt("Bilgisayarim", "My Computer")),
                        ("TRASH", pygame.Rect(20,110,60,60), ikon_trash, os_config.txt("Cop Kutusu", "Recycle Bin")),
                        ("CAM", pygame.Rect(90,20,60,60), ikon_cam, "Kamera"),
                        ("OYUNLAR", pygame.Rect(20,200,60,60), ikon_folder, os_config.txt("Oyunlar", "Games")),
                        ("DUVAR", pygame.Rect(20,290,60,60), ikon_folder, os_config.txt("DuvarKagidi", "Wallpaper")),
                        ("TARAYICI", pygame.Rect(20,380,60,60), ikon_explorer, os_config.txt("Tarayici", "Browser")),
                        ("HESAP", pygame.Rect(20,470,60,60), ikon_cal, os_config.txt("HesapMakine", "Calculator")),
                        ("NOT", pygame.Rect(20,560,60,60), ikon_not, os_config.txt("Not Defteri", "Notepad")),
                        ("AYAR", pygame.Rect(OS_GENISLIK-80,20,60,60), ikon_ayar, os_config.txt("Ayarlar", "Settings"))
                    ]
                    if os_config.lost_soul_hatali:
                        ikon_list.append(("CODE_TXT", pygame.Rect(90, 110, 60, 60), ikon_not, "code.txt"))
                    
                    for kimlik, rect, img, ad in ikon_list:
                        if rect.collidepoint(mouse_x, mouse_y):
                            if kimlik == "OYUNLAR" and os_config.hikaye_asamasi == 0:
                                story_system.dialog_baslat(os_config.txt("Once internetten is ilanlarina bakip bir is bulmam lazim...", "I need to check job ads first..."))
                            else:
                                if clk and son_tiklanan_ikon == kimlik:
                                    if kimlik == "CAM":
                                        pencere_durumlari["KAMERA"]["acik"] = True
                                        if "KAMERA" not in pencere_sirasi:
                                            pencere_sirasi.append("KAMERA")
                                    elif kimlik == "CODE_TXT":
                                        pencere_durumlari["NOT"]["acik"] = True
                                        if "NOT" not in pencere_sirasi:
                                            pencere_sirasi.append("NOT")
                                        not_metni = f"KAYIP RUH ERISIM KODU:\n\n{os_config.lost_soul_code}"
                                        son_tiklanan_ikon = None
                                    elif kimlik == "COMPUTER":
                                        pencere_durumlari["BILGISAYAR"]["acik"] = True
                                        if "BILGISAYAR" not in pencere_sirasi:
                                            pencere_sirasi.append("BILGISAYAR")
                                    elif kimlik == "TRASH":
                                        pencere_durumlari["COP"]["acik"] = True
                                        if "COP" not in pencere_sirasi:
                                            pencere_sirasi.append("COP")
                                    elif kimlik in pencere_durumlari:
                                        pencere_durumlari[kimlik]["acik"] = True
                                        if kimlik not in pencere_sirasi:
                                            pencere_sirasi.append(kimlik)
                                    son_tiklanan_ikon = None
                                else:
                                    son_tiklanan_ikon = kimlik
                                secili_ikon = kimlik
                            tiklama_yakalandi = True
                            break
                    if not tiklama_yakalandi:
                        secili_ikon = None
                        son_tiklanan_ikon = None

        if event.type == pygame.MOUSEWHEEL:
            if pencere_durumlari["TARAYICI"]["acik"] and pencere_sirasi and pencere_sirasi[-1] == "TARAYICI":
                if browser_pages.tarayici_sekme == "Is Ilanlari":
                    browser_pages.tarayici_scroll = max(min(0, -((len(browser_pages.get_sahte_ilanlar()) * 60) - 350)), min(0, browser_pages.tarayici_scroll + event.y * 40))
                elif browser_pages.tarayici_sekme == "Haberler":
                    browser_pages.tarayici_scroll = max(min(0, -((len(browser_pages.get_sahte_haberler()) * 70) - 350)), min(0, browser_pages.tarayici_scroll + event.y * 40))

        if event.type == pygame.KEYDOWN:
            if sistem_durumu == "LOGIN":
                if event.key == pygame.K_RETURN and len(girilen_sifre) >= 5:
                    sistem_durumu = "OS"
                    os_ses_oynat(ses_logon)
                elif event.key == pygame.K_BACKSPACE:
                    girilen_sifre = girilen_sifre[:-1]
                elif len(girilen_sifre) < 5 and event.unicode.isprintable():
                    girilen_sifre += event.unicode[0]

            elif sistem_durumu == "OS":
                if pencere_durumlari["NOT"]["acik"] and pencere_sirasi and pencere_sirasi[-1] == "NOT":
                    satirlar = not_metni.split("\n")
                    if event.key == pygame.K_BACKSPACE:
                        not_metni = not_metni[:-1]
                    elif event.key == pygame.K_RETURN and len(satirlar) < 16:
                        not_metni += "\n"
                    elif event.unicode.isprintable() and len(satirlar[-1]) < 55:
                        not_metni += event.unicode

                if pencere_durumlari["TARAYICI"]["acik"] and pencere_sirasi and pencere_sirasi[-1] == "TARAYICI":
                    if browser_pages.tarayici_sekme == "Google":
                        if event.key == pygame.K_BACKSPACE:
                            browser_pages.tarayici_arama_metni = browser_pages.tarayici_arama_metni[:-1]
                        elif event.unicode.isprintable() and len(browser_pages.tarayici_arama_metni) < 25:
                            browser_pages.tarayici_arama_metni += event.unicode

                if pencere_durumlari["ZAR"]["acik"] and pencere_sirasi and pencere_sirasi[-1] == "ZAR":
                    zk_menuler = [os_config.txt("Oyna","Play"), os_config.txt("Market","Shop"), os_config.txt("Ayarlar","Settings"), os_config.txt("Cikis","Exit")]
                    zk_ayarlar = [os_config.txt("Muzik Sesi","Music Vol."), os_config.txt("Efekt Sesi","SFX Vol."), os_config.txt("Geri","Back")]
                    zk_market = [os_config.txt("Zar Guclendirici (50 Altin)","Dice Buff (50G)"), os_config.txt("Alan Genisletici (70 Altin)","Area Expand (70G)"), os_config.txt("Can Iksiri (30 Altin)","HP Pot (30G)"), os_config.txt("Hasar Iksiri (40 Altin)","DMG Pot (40G)"), os_config.txt("Geri","Back")]
                    zk_aksiyon = [os_config.txt("Zar At","Roll"), os_config.txt("Esya","Item")]
                    zk_esya = [os_config.txt("Can Iksiri","HP Pot"), os_config.txt("Hasar Iksiri","DMG Pot"), os_config.txt("Geri","Back")]

                    if oyun_durumu == "ANA_MENU":
                        if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                            oyun_ses_oynat(dk_ses_click)
                            secili_indeks = (secili_indeks + 1) % len(zk_menuler)
                        elif event.key == pygame.K_w or event.key == pygame.K_UP:
                            oyun_ses_oynat(dk_ses_click)
                            secili_indeks = (secili_indeks - 1) % len(zk_menuler)
                        elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                            oyun_ses_oynat(dk_ses_click)
                            if secili_indeks == 0:
                                oyun_durumu = "BOLUM_SECIMI"
                                guncel_arka_plan = arka_plan_oyun
                                muzik_baslat("song1", yol_song1)
                            elif secili_indeks == 1:
                                oyun_durumu = "MARKET"
                                guncel_arka_plan = arka_plan_oyun
                            elif secili_indeks == 2:
                                oyun_durumu = "AYARLAR"
                                guncel_arka_plan = arka_plan_oyun
                            elif secili_indeks == 3:
                                pencere_durumlari["ZAR"]["acik"] = False
                                if "ZAR" in pencere_sirasi:
                                    pencere_sirasi.remove("ZAR")
                                oyun_durumu = "ANA_MENU"
                                guncel_arka_plan = arka_plan_main
                                muzik_durdur()
                    elif oyun_durumu == "AYARLAR":
                        if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                            oyun_ses_oynat(dk_ses_click)
                            ayarlar_indeks = (ayarlar_indeks + 1) % len(zk_ayarlar)
                        elif event.key == pygame.K_w or event.key == pygame.K_UP:
                            oyun_ses_oynat(dk_ses_click)
                            ayarlar_indeks = (ayarlar_indeks - 1) % len(zk_ayarlar)
                        elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                            if ayarlar_indeks == 0:
                                muzik_seviyesi = max(0, muzik_seviyesi - 5)
                                pygame.mixer.music.set_volume(muzik_seviyesi / 100)
                            elif ayarlar_indeks == 1:
                                sfx_seviyesi = max(0, sfx_seviyesi - 5)
                                oyun_ses_oynat(dk_ses_click)
                        elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                            if ayarlar_indeks == 0:
                                muzik_seviyesi = min(100, muzik_seviyesi + 5)
                                pygame.mixer.music.set_volume(muzik_seviyesi / 100)
                            elif ayarlar_indeks == 1:
                                sfx_seviyesi = min(100, sfx_seviyesi + 5)
                                oyun_ses_oynat(dk_ses_click)
                        elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                            if ayarlar_indeks == 2:
                                oyun_durumu = "ANA_MENU"
                                guncel_arka_plan = arka_plan_main
                        elif event.key == pygame.K_ESCAPE:
                            oyun_durumu = "ANA_MENU"
                            guncel_arka_plan = arka_plan_main
                    elif oyun_durumu == "MARKET":
                        if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                            oyun_ses_oynat(dk_ses_click)
                            market_indeks = (market_indeks + 1) % len(zk_market)
                        elif event.key == pygame.K_w or event.key == pygame.K_UP:
                            oyun_ses_oynat(dk_ses_click)
                            market_indeks = (market_indeks - 1) % len(zk_market)
                        elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                            if market_indeks == 0:
                                if os_config.toplam_altin >= 50:
                                    oyun_ses_oynat(ses_shoplvlup)
                                    os_config.toplam_altin -= 50
                                    os_config.zar_seviyesi += 1
                                else:
                                    oyun_ses_oynat(ses_shoperror)
                            elif market_indeks == 1:
                                if os_config.toplam_altin >= 70:
                                    oyun_ses_oynat(ses_shoplvlup)
                                    os_config.toplam_altin -= 70
                                    os_config.alan_seviyesi += 1
                                else:
                                    oyun_ses_oynat(ses_shoperror)
                            elif market_indeks == 2:
                                if os_config.toplam_altin >= 30:
                                    oyun_ses_oynat(ses_shoplvlup)
                                    os_config.toplam_altin -= 30
                                    can_iksiri_sayisi += 1
                                else:
                                    oyun_ses_oynat(ses_shoperror)
                            elif market_indeks == 3:
                                if os_config.toplam_altin >= 40:
                                    oyun_ses_oynat(ses_shoplvlup)
                                    os_config.toplam_altin -= 40
                                    hasar_iksiri_sayisi += 1
                                else:
                                    oyun_ses_oynat(ses_shoperror)
                            elif market_indeks == 4:
                                oyun_durumu = "ANA_MENU"
                                guncel_arka_plan = arka_plan_main
                        elif event.key == pygame.K_ESCAPE:
                            oyun_durumu = "ANA_MENU"
                            guncel_arka_plan = arka_plan_main
                    elif oyun_durumu == "BOLUM_SECIMI":
                        if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                            oyun_ses_oynat(dk_ses_click)
                            secili_bolum = max(0, secili_bolum - 1)
                        elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                            oyun_ses_oynat(dk_ses_click)
                            secili_bolum = min(4, secili_bolum + 1)
                        elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                            if secili_bolum < os_config.kilit_acik_bolum:
                                oyun_durumu = "OYUN"
                                aktif_oynanan_bolum = secili_bolum + 1
                                oyun_ici_durum = "OYUNCU_MENU"
                                aksiyon_indeks = 0
                                oyuncu_can = 100
                                bot_can = 100
                                cubuk_x = 200
                                can_havuzu = [100,150,220,320,500]
                                bot_maks_can = can_havuzu[aktif_oynanan_bolum-1]
                                bot_can = bot_maks_can
                                guncel_cubuk_hiz = 6 + (aktif_oynanan_bolum-1)*2
                                yesil_genislik = max(32, 80 - (aktif_oynanan_bolum-1)*12) + (os_config.alan_seviyesi-1)*10
                                kirmizi_genislik = (aktif_oynanan_bolum-1)*15 if aktif_oynanan_bolum > 1 else 0
                                if aktif_oynanan_bolum == 5:
                                    muzik_baslat("boss", yol_bossfight)
                                else:
                                    muzik_baslat("song1", yol_song1)
                        elif event.key == pygame.K_ESCAPE:
                            oyun_durumu = "ANA_MENU"
                            guncel_arka_plan = arka_plan_main
                            muzik_durdur()
                    elif oyun_durumu == "OYUN":
                        if oyun_ici_durum == "OYUNCU_MENU":
                            if event.key == pygame.K_ESCAPE:
                                oyun_durumu = "BOLUM_SECIMI"
                                muzik_baslat("song1", yol_song1)
                            elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                                oyun_ses_oynat(dk_ses_click)
                                aksiyon_indeks = (aksiyon_indeks + 1) % len(zk_aksiyon)
                            elif event.key == pygame.K_w or event.key == pygame.K_UP:
                                oyun_ses_oynat(dk_ses_click)
                                aksiyon_indeks = (aksiyon_indeks - 1) % len(zk_aksiyon)
                            elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                                if aksiyon_indeks == 0:
                                    oyun_ici_durum = "OYUNCU_BEKLIYOR"
                                    cubuk_x = 200
                                elif aksiyon_indeks == 1:
                                    oyun_ici_durum = "OYUNCU_ESYA"
                                    esya_indeks = 0
                        elif oyun_ici_durum == "OYUNCU_ESYA":
                            if event.key == pygame.K_ESCAPE:
                                oyun_ses_oynat(dk_ses_click)
                                oyun_ici_durum = "OYUNCU_MENU"
                            elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                                oyun_ses_oynat(dk_ses_click)
                                esya_indeks = (esya_indeks + 1) % len(zk_esya)
                            elif event.key == pygame.K_w or event.key == pygame.K_UP:
                                oyun_ses_oynat(dk_ses_click)
                                esya_indeks = (esya_indeks - 1) % len(zk_esya)
                            elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                                if esya_indeks == 0:
                                    if not tur_iksir_kullandi_mi and can_iksiri_sayisi > 0 and oyuncu_can < 100:
                                        oyun_ses_oynat(ses_shoplvlup)
                                        can_iksiri_sayisi -= 1
                                        oyuncu_can = min(100, oyuncu_can + 30)
                                        flas_yarat(3, YESIL)
                                        tur_iksir_kullandi_mi = True
                                        oyun_ici_durum = "OYUNCU_MENU"
                                    else:
                                        oyun_ses_oynat(ses_shoperror)
                                elif esya_indeks == 1:
                                    if not tur_iksir_kullandi_mi and hasar_iksiri_sayisi > 0 and not hasar_iksiri_aktif:
                                        oyun_ses_oynat(ses_shoplvlup)
                                        hasar_iksiri_sayisi -= 1
                                        hasar_iksiri_aktif = True
                                        flas_yarat(3, MOR)
                                        tur_iksir_kullandi_mi = True
                                        oyun_ici_durum = "OYUNCU_MENU"
                                    else:
                                        oyun_ses_oynat(ses_shoperror)
                                elif esya_indeks == 2:
                                    oyun_ses_oynat(dk_ses_click)
                                    oyun_ici_durum = "OYUNCU_MENU"
                        elif oyun_ici_durum == "OYUNCU_BEKLIYOR" and event.key == pygame.K_SPACE:
                            oyun_ses_oynat(ses_diceroll)
                            oyun_ici_durum = "OYUNCU_ZAR_DONUYOR"
                            animasyon_baslangic = suan
                            zar_sesi_calindi = False
                            orta_x = 400
                            sol_yesil = orta_x - yesil_genislik//2
                            sag_yesil = orta_x + yesil_genislik//2
                            sol_kirmizi_sol = sol_yesil - kirmizi_genislik
                            sag_kirmizi_sag = sag_yesil + kirmizi_genislik

                            if (orta_x - 7) <= cubuk_x <= (orta_x + 7):
                                atis_durumu = "KRITIK"
                                son_zar = random.randint(5,6)
                                son_hasar = int(son_zar * 15 * (1 + (os_config.zar_seviyesi - 1)*0.2))
                                hasar_yazisi_renk = SARI
                            elif sol_yesil <= cubuk_x <= sag_yesil:
                                atis_durumu = "MUKEMMEL"
                                son_zar = random.randint(4,6)
                                son_hasar = int(son_zar * 10 * (1 + (os_config.zar_seviyesi - 1)*0.2))
                                hasar_yazisi_renk = YESIL
                            elif cubuk_x < sol_yesil and cubuk_x >= sol_kirmizi_sol:
                                atis_durumu = "ISKA"
                                son_zar = 0
                                son_hasar = 0
                                hasar_yazisi_renk = KIRMIZI
                            elif cubuk_x > sag_yesil and cubuk_x <= sag_kirmizi_sag:
                                atis_durumu = "ISKA"
                                son_zar = 0
                                son_hasar = 0
                                hasar_yazisi_renk = KIRMIZI
                            else:
                                atis_durumu = "NORMAL"
                                son_zar = random.randint(1,4)
                                son_hasar = int(son_zar * 10 * (1 + (os_config.zar_seviyesi - 1)*0.2))
                                hasar_yazisi_renk = TURUNCU
                            if hasar_iksiri_aktif and son_hasar > 0:
                                son_hasar = int(son_hasar * 1.20)
                                hasar_iksiri_aktif = False
                            if atis_durumu == "KRITIK":
                                hasar_yazisi_metin = f"CRITICAL! -{son_hasar} HP"
                            elif atis_durumu == "ISKA":
                                hasar_yazisi_metin = "ISKA!"
                            else:
                                hasar_yazisi_metin = f"-{son_hasar} HP"
                        elif oyun_ici_durum == "OYUN_BITTI" and event.key == pygame.K_SPACE:
                            oyun_durumu = "BOLUM_SECIMI"
                            muzik_baslat("song1", yol_song1)

        if event.type == pygame.MOUSEBUTTONUP:
            suruklenen_pencere = None
            os_ayar_ses_surukleniyor = False

    # --- SÜRÜKLEME ---
    if suruklenen_pencere:
        info = pencere_durumlari[suruklenen_pencere]
        w, h = {
            "ZAR": (800,600), "TARAYICI":(800,600), "KAYIP":(800,600),
            "DUVAR":(500,400), "NOT":(500,400), "OYUNLAR":(400,300),
            "MAYIN":(400,400), "HESAP":(250,350), "AYAR":(300,250),
            "HL3":(300,150), "BILGISAYAR":(400,300), "COP":(400,300),
            "KAMERA": (320, 240)
        }.get(suruklenen_pencere, (400,300))
        min_x = 0
        max_x = OS_GENISLIK - w
        min_y = 0
        max_y = OS_YUKSEKLIK - h - 45
        info["x"] = max(min_x, min(mouse_x - surukleme_farki_x, max_x))
        info["y"] = max(min_y, min(mouse_y - surukleme_farki_y, max_y))

    if os_ayar_ses_surukleniyor:
        yeni_ses = int(((mouse_x - (pencere_durumlari["AYAR"]["x"] + 50)) / 200) * 100)
        os_config.os_sistem_sesi = max(0, min(100, yeni_ses))
        muzik_seviyesi = os_config.os_sistem_sesi
        sfx_seviyesi = os_config.os_sistem_sesi
        pygame.mixer.music.set_volume(os_config.os_sistem_sesi / 100)

    # --- LOST SOUL OYUN KAPANMA KONTROLÜ ---
    if lost_soul_game_instance is not None:
        if not lost_soul_game_instance.running:
            is_bolum2_win = (lost_soul_game_instance.bolum == 2 and lost_soul_game_instance.labirent_aktif and lost_soul_game_instance.labirent_kazandi)
            
            lost_soul_game_instance.durdur_ses()
            
            if is_bolum2_win:
                os_config.lost_soul_ikinci_bolum = True
                os_config.lost_soul_unlocked = True
                os_config.lost_soul_hatali = False
                os_config.kayit_sistemi.kaydet()
                
                lost_soul_game_instance = None
                pencere_durumlari["KAYIP"]["acik"] = False
                if "KAYIP" in pencere_sirasi:
                    pencere_sirasi.remove("KAYIP")
                
                sistem_durumu = "OYUN_SONU"
                oyun_sonu_zamani = suan
            else:
                # 3 kere öldüysek (Desktop Madness) tetiklemesi
                if lost_soul_game_instance.bolum == 2 and getattr(lost_soul_game_instance, 'hak_sayisi', 3) <= 0:
                    os_config.lost_soul_cildirdi = True
                    os_config.lost_soul_cildirdi_zamani = suan
                    lost_soul_game_instance = None
                    pencere_durumlari["KAYIP"]["acik"] = False
                    if "KAYIP" in pencere_sirasi:
                        pencere_sirasi.remove("KAYIP")
                else:
                    # Bölüm 1 çöküş senaryosu (şifre üretme)
                    sahte_masaustu = os.path.join("Assets", "desktop")
                    os.makedirs(sahte_masaustu, exist_ok=True)
                    dosya_yolu = os.path.join(sahte_masaustu, "code.txt")
                    
                    kod = str(random.randint(10000, 99999))
                    with open(dosya_yolu, 'w') as f:
                        f.write(kod)
                    
                    os_config.lost_soul_code = kod
                    os_config.lost_soul_txt_path = dosya_yolu
                    
                    os_config.lost_soul_hatali = True
                    os_config.lost_soul_unlocked = False
                    os_config.kayit_sistemi.kaydet()
                    
                    glitch_hata_ekle()
                    
                    lost_soul_game_instance = None
                    pencere_durumlari["KAYIP"]["acik"] = False
                    if "KAYIP" in pencere_sirasi:
                        pencere_sirasi.remove("KAYIP")
                    
                    bildirim_metni = os_config.txt("Bölüm 2'ye geçiş kodu oluşturuldu. Assets/desktop/code.txt dosyasına bak.", "Chapter 2 code created. Check Assets/desktop/code.txt.")
                    bildirim_zamani = suan

    # --- ÇİZİM ---
    if sistem_durumu == "ANA_GIRIS":
        ekran.fill((20,30,40))
        baslik = g_font.render("ÇAĞRI", True, BEYAZ)
        ekran.blit(baslik, (OS_GENISLIK//2 - baslik.get_width()//2, 150))
        for btn, yazi in [(btn_yeni, os_config.txt("Yeni Oyun","New Game")), (btn_devam, os_config.txt("Kayitli Oyun","Continue")), (btn_cikis, os_config.txt("Cikis","Quit"))]:
            renk = (0,100,150) if btn.collidepoint(mouse_x,mouse_y) else (50,60,70)
            if btn == btn_cikis:
                renk = (180,50,50) if btn.collidepoint(mouse_x,mouse_y) else (50,60,70)
            pygame.draw.rect(ekran, renk, btn, border_radius=10)
            yaz = os_buyuk_font.render(yazi, True, BEYAZ)
            ekran.blit(yaz, (btn.centerx - yaz.get_width()//2, btn.centery - yaz.get_height()//2))

    elif sistem_durumu == "CUTSCENE":
        ekran.blit(cutscene_resmi, (0,0))
        if cutscene_asamasi == 1:
            ekran.fill(SIYAH, (545, 10, 725, 700))
        elif cutscene_asamasi == 2:
            ekran.fill(SIYAH, (545, 338, 725, 368))

    elif sistem_durumu == "LOGIN":
        ekran.fill(OS_ARKA_PLAN_RENK)
        ekran.blit(ikon_login, (OS_GENISLIK//2 - 70, OS_YUKSEKLIK//2 - 140))
        ekran.blit(os_buyuk_font.render(os_config.txt("Kullanici","User"), True, BEYAZ), (OS_GENISLIK//2 - 55, OS_YUKSEKLIK//2 + 10))
        pygame.draw.rect(ekran, BEYAZ, (OS_GENISLIK//2 - 100, OS_YUKSEKLIK//2 + 50, 200, 40))
        pygame.draw.rect(ekran, SIYAH, (OS_GENISLIK//2 - 100, OS_YUKSEKLIK//2 + 50, 200, 40), 2)
        gizli = "*" * len(girilen_sifre)
        ekran.blit(os_buyuk_font.render(gizli, True, SIYAH), (OS_GENISLIK//2 - 90, OS_YUKSEKLIK//2 + 52))
        if len(girilen_sifre) >= 5:
            ok_r = pygame.Rect(OS_GENISLIK//2 + 110, OS_YUKSEKLIK//2 + 50, 40, 40)
            pygame.draw.rect(ekran, (0,150,255), ok_r)
            pygame.draw.rect(ekran, BEYAZ, ok_r, 2)
            ekran.blit(os_baslik_font.render("->", True, BEYAZ), (OS_GENISLIK//2 + 120, OS_YUKSEKLIK//2 + 60))

    elif sistem_durumu == "OS":
        if os_config.lost_soul_cildirdi:
            # Agresif ve ürkütücü kırmızı çöküş ekranı (Desktop Madness)
            ekran.fill((random.randint(150, 255), 0, 0))
            for i in range(12):
                gx = random.randint(0, OS_GENISLIK - 400)
                gy = random.randint(0, OS_YUKSEKLIK - 150)
                pygame.draw.rect(ekran, SIYAH, (gx, gy, random.randint(200, 450), random.randint(40, 100)))
                spooky_text = random.choice([
                    "CRITICAL EXCEPTION", "DELETE IN PROGRESS", "SYSTEM CORRUPTED", "HE IS WATCHING", "RUN RUN RUN",
                    "FATAL ERROR", "MEMORY LEAK", "LOST SOUL HAS TAKEN OVER", "ACCESS VIOLATION"
                ])
                txt_surf = os_buyuk_font.render(spooky_text, True, KIRMIZI)
                ekran.blit(txt_surf, (gx + 15, gy + 20))
            for _ in range(35):
                pygame.draw.line(ekran, SARI, (0, random.randint(0, OS_YUKSEKLIK)), (OS_GENISLIK, random.randint(0, OS_YUKSEKLIK)), random.randint(1, 4))
        else:
            if os_arka_plan_resmi:
                ekran.blit(os_arka_plan_resmi, (0,0))
            else:
                ekran.fill(OS_ARKA_PLAN_RENK)

            if glitch_hata_gosterimi:
                for i, metin in enumerate(glitch_hata_mesajlari):
                    metin_surf = os_baslik_font.render(metin, True, BEYAZ)
                    x = 100 + i * 150
                    y = 50 + i * 80
                    kapat_rect = pygame.Rect(x + metin_surf.get_width() - 20, y - 10, 20, 20)
                    pygame.draw.rect(ekran, (200,0,0), (x-10, y-10, metin_surf.get_width()+20, 30))
                    ekran.blit(metin_surf, (x, y))
                    pygame.draw.rect(ekran, BEYAZ, kapat_rect, 2)
                    ekran.blit(os_font.render("X", True, BEYAZ), (kapat_rect.x+5, kapat_rect.y))

            ikon_list = [
                ("COMPUTER", pygame.Rect(20,20,60,60), ikon_computer, os_config.txt("Bilgisayarim", "My Computer")),
                ("TRASH", pygame.Rect(20,110,60,60), ikon_trash, os_config.txt("Cop Kutusu", "Recycle Bin")),
                ("CAM", pygame.Rect(90,20,60,60), ikon_cam, "Kamera"),
                ("OYUNLAR", pygame.Rect(20,200,60,60), ikon_folder, os_config.txt("Oyunlar", "Games")),
                ("DUVAR", pygame.Rect(20,290,60,60), ikon_folder, os_config.txt("DuvarKagidi", "Wallpaper")),
                ("TARAYICI", pygame.Rect(20,380,60,60), ikon_explorer, os_config.txt("Tarayici", "Browser")),
                ("HESAP", pygame.Rect(20,470,60,60), ikon_cal, os_config.txt("HesapMakine", "Calculator")),
                ("NOT", pygame.Rect(20,560,60,60), ikon_not, os_config.txt("Not Defteri", "Notepad")),
                ("AYAR", pygame.Rect(OS_GENISLIK-80,20,60,60), ikon_ayar, os_config.txt("Ayarlar", "Settings"))
            ]
            if os_config.lost_soul_hatali:
                ikon_list.append(("CODE_TXT", pygame.Rect(90, 110, 60, 60), ikon_not, "code.txt"))
            
            for kimlik, rect, img, ad in ikon_list:
                ikon_ciz(ekran, rect, img, ad, kimlik)

            for p in pencere_sirasi:
                info = pencere_durumlari[p]
                if not info["acik"]:
                    continue
                w, h = {
                    "ZAR": (800,600), "TARAYICI":(800,600), "KAYIP":(800,600),
                    "DUVAR":(500,400), "NOT":(500,400), "OYUNLAR":(400,300),
                    "MAYIN":(400,400), "HESAP":(250,350), "AYAR":(300,250),
                    "HL3":(300,150), "BILGISAYAR":(400,300), "COP":(400,300),
                    "KAMERA": (320, 240)
                }.get(p, (400,300))

                baslik_surf = pygame.Surface((w, 30))
                for y in range(30):
                    renk = (max(50, 100 - y), max(80, 150 - y), max(180, 220 - y))
                    pygame.draw.line(baslik_surf, renk, (0, y), (w, y))
                ekran.blit(baslik_surf, (info["x"], info["y"]-30))
                ekran.blit(os_baslik_font.render(get_pencere_baslik(p), True, BEYAZ), (info["x"]+10, info["y"]-25))
                pygame.draw.rect(ekran, KIRMIZI, (info["x"]+w-40, info["y"]-30, 40, 30))
                ekran.blit(os_baslik_font.render("X", True, BEYAZ), (info["x"]+w-25, info["y"]-25))

                surf = pygame.Surface((w,h))
                surf.fill(BEYAZ if p not in ["AYAR","HL3","DUVAR","HESAP","MAYIN","KAYIP","ZAR","BILGISAYAR","COP"] else (230,230,230))

                if p == "TARAYICI":
                    surf.fill((210,220,230))
                    sekmeler = ["Google", os_config.txt("Haberler","News"), os_config.txt("Is Ilanlari","Jobs"), "Gmail"]
                    for i, s_ad in enumerate(sekmeler):
                        s_id = ["Google","Haberler","Is Ilanlari","Gmail"][i]
                        r = pygame.Rect(10+i*105, 5, 100, 25)
                        pygame.draw.rect(surf, BEYAZ if browser_pages.tarayici_sekme == s_id else (180,190,200), r, border_radius=5)
                        surf.blit(os_font.render(s_ad, True, SIYAH), (r.x+10, r.y+3))
                    pygame.draw.rect(surf, BEYAZ, (10,35,780,25))
                    pygame.draw.rect(surf, GRI, (10,35,780,25), 1)
                    surf.blit(os_font.render("http://www." + browser_pages.tarayici_sekme.lower().replace(" ","") + ".com", True, GRI), (15,38))
                    body = pygame.Rect(0,65,w,h-65)
                    surf.set_clip(body)
                    pygame.draw.rect(surf, BEYAZ, body)

                    if browser_pages.tarayici_sekme == "Google":
                        surf.blit(g_font.render("Google", True, (66,133,244)), (280,150))
                        imlec = "|" if suan % 1000 > 500 else ""
                        surf.blit(os_buyuk_font.render(browser_pages.tarayici_arama_metni + imlec, True, SIYAH), (160,265))
                    elif browser_pages.tarayici_sekme == "Haberler":
                        if browser_pages.secili_haber is None:
                            yh = 120 + browser_pages.tarayici_scroll
                            for bas, ic, detay in browser_pages.get_sahte_haberler():
                                pygame.draw.rect(surf, (245,245,245), (20, yh, 760, 60))
                                surf.blit(os_baslik_font.render(bas, True, KIRMIZI), (30, yh+10))
                                surf.blit(os_font.render(ic, True, SIYAH), (30, yh+35))
                                yh += 70
                        else:
                            pygame.draw.rect(surf, (230,230,230), (20,80,760,40))
                            pygame.draw.rect(surf, GRI, (30,85,80,30))
                            surf.blit(os_baslik_font.render(os_config.txt("< Geri","< Back"), True, BEYAZ), (45,90))
                            surf.blit(os_baslik_font.render(browser_pages.secili_haber[0], True, (150,0,0)), (30,140))
                            yd = 180
                            for s in browser_pages.secili_haber[2].split("\n"):
                                surf.blit(os_font.render(s, True, SIYAH), (30, yd))
                                yd += 20
                    elif browser_pages.tarayici_sekme == "Is Ilanlari":
                        if browser_pages.secili_ilan is None:
                            yi = 120 + browser_pages.tarayici_scroll
                            for ad, srk, is_hedef, detay in browser_pages.get_sahte_ilanlar():
                                pygame.draw.rect(surf, (245,245,245), (20, yi, 760, 50))
                                surf.blit(os_baslik_font.render(ad, True, SIYAH), (30, yi+5))
                                surf.blit(os_font.render(srk, True, GRI), (30, yi+25))
                                yi += 60
                        else:
                            pygame.draw.rect(surf, (230,230,230), (20,80,760,40))
                            pygame.draw.rect(surf, GRI, (30,85,80,30))
                            surf.blit(os_baslik_font.render(os_config.txt("< Geri","< Back"), True, BEYAZ), (45,90))
                            surf.blit(os_baslik_font.render(browser_pages.secili_ilan[0], True, SIYAH), (30,140))
                            yd = 180
                            for s in browser_pages.secili_ilan[3].split("\n"):
                                surf.blit(os_font.render(s, True, SIYAH), (30, yd))
                                yd += 20
                            yd_btn = yd + 20
                            if not os_config.mail_basvuruldu:
                                pygame.draw.rect(surf, (50,150,50), (30, min(yd_btn,450), 140, 40), border_radius=5)
                                surf.blit(os_baslik_font.render(os_config.txt("BASVUR","APPLY"), True, BEYAZ), (65, min(yd_btn,450)+10))
                    elif browser_pages.tarayici_sekme == "Gmail":
                        surf.fill((240,240,240))
                        pygame.draw.rect(surf, (217,48,37), (0,65,800,40))
                        surf.blit(os_buyuk_font.render("Gmail", True, BEYAZ), (20,70))
                        pygame.draw.rect(surf, (230,230,230), (0,105,150,475))
                        menuler = ["Gelen Kutusu", "Yıldızlı", "Gönderilen", "Taslaklar", "Çöp"]
                        for i, m in enumerate(menuler):
                            renk = (200,200,200) if i == 0 else (240,240,240)
                            pygame.draw.rect(surf, renk, (10, 110 + i*40, 130, 30), border_radius=5)
                            surf.blit(os_font.render(m, True, SIYAH if i==0 else GRI), (20, 115 + i*40))
                        if browser_pages.secili_mail is None:
                            ym = 120
                            for mail in browser_pages.gelen_kutusu:
                                arka = BEYAZ if mail.get("yeni") else (245,245,245)
                                pygame.draw.rect(surf, arka, (160, ym, 630, 40))
                                pygame.draw.rect(surf, GRI, (160, ym, 630, 40), 1)
                                surf.blit(os_baslik_font.render(mail["gonderen"], True, SIYAH), (170, ym+10))
                                surf.blit(os_font.render(os_config.txt(mail["konu_tr"], mail.get("konu_en","")), True, GRI), (300, ym+10))
                                ym += 50
                        else:
                            pygame.draw.rect(surf, (230,230,230), (160,105,630,40))
                            pygame.draw.rect(surf, GRI, (170,110,80,30))
                            surf.blit(os_baslik_font.render(os_config.txt("< Geri","< Back"), True, BEYAZ), (185,115))
                            surf.blit(os_buyuk_font.render(os_config.txt(browser_pages.secili_mail["konu_tr"], browser_pages.secili_mail.get("konu_en","")), True, SIYAH), (180,160))
                            surf.blit(os_baslik_font.render(os_config.txt("Kimden: ","From: ") + browser_pages.secili_mail["gonderen"], True, GRI), (180,200))
                            pygame.draw.line(surf, GRI, (180,225), (770,225), 1)
                            yc = 240
                            icerik = os_config.txt(browser_pages.secili_mail["icerik_tr"], browser_pages.secili_mail.get("icerik_en",""))
                            for s in icerik.split("\n"):
                                surf.blit(os_font.render(s, True, SIYAH), (180, yc))
                                yc += 25
                            if browser_pages.secili_mail["gonderen"] == "GIZLI YONETICI":
                                if indirme_durumu == "Yok":
                                    pygame.draw.rect(surf, (0,150,255), (180, yc+30, 150, 40))
                                    surf.blit(os_baslik_font.render("OYUNU INDIR", True, BEYAZ), (195, yc+40))
                                elif indirme_durumu == "Indiriliyor":
                                    pygame.draw.rect(surf, GRI, (180, yc+30, 300, 20))
                                    pygame.draw.rect(surf, YESIL, (180, yc+30, int(300*(indirme_yuzdesi/100)), 20))
                                    surf.blit(os_font.render(f"Indiriliyor... %{int(indirme_yuzdesi)}", True, SIYAH), (180, yc+55))
                                elif indirme_durumu == "Tamamlandi":
                                    surf.blit(os_baslik_font.render("Indirme Tamamlandi.", True, YESIL), (180, yc+30))
                            elif browser_pages.secili_mail.get("link", False):
                                if indirme_durumu == "Yok":
                                    pygame.draw.rect(surf, (0,150,255), (180, yc+30, 150, 40))
                                    surf.blit(os_baslik_font.render("DOSYAYI INDIR", True, BEYAZ), (195, yc+40))
                                elif indirme_durumu == "Indiriliyor":
                                    pygame.draw.rect(surf, GRI, (180, yc+30, 300, 20))
                                    pygame.draw.rect(surf, YESIL, (180, yc+30, int(300*(indirme_yuzdesi/100)), 20))
                                    surf.blit(os_font.render(f"Indiriliyor... %{int(indirme_yuzdesi)}", True, SIYAH), (180, yc+55))
                                elif indirme_durumu == "Tamamlandi":
                                    surf.blit(os_baslik_font.render("Yeni sürüm indirildi. Oyunu tekrar deneyin.", True, YESIL), (180, yc+30))
                        surf.set_clip(None)

                elif p == "AYAR":
                    surf.blit(os_baslik_font.render(os_config.txt("Sistem Sesi","System Volume"), True, SIYAH), (20,20))
                    pygame.draw.rect(surf, GRI, (50,50,200,10))
                    pygame.draw.rect(surf, (0,150,255), (50,50, int((os_config.os_sistem_sesi/100)*200), 10))
                    pygame.draw.circle(surf, (0,100,200), (50 + int((os_config.os_sistem_sesi/100)*200), 55), 10)
                    surf.blit(os_baslik_font.render(os_config.txt("Sistem Dili:","Language:"), True, SIYAH), (20,110))
                    dil_btn = pygame.Rect(100,150,100,40)
                    pygame.draw.rect(surf, (0,150,255), dil_btn, border_radius=5)
                    lang = os_buyuk_font.render(os_config.os_dil, True, BEYAZ)
                    surf.blit(lang, (150 - lang.get_width()//2, 155))
                    surf.blit(os_baslik_font.render(os_config.txt("Tam Ekran","Fullscreen"), True, SIYAH), (20,195))
                    tam_ekran_check = pygame.Rect(50,200,20,20)
                    pygame.draw.rect(surf, BEYAZ, tam_ekran_check, 2)
                    if getattr(os_config, "tam_ekran", False):
                        pygame.draw.rect(surf, (0,150,255), (tam_ekran_check.x+2, tam_ekran_check.y+2, 16, 16))
                    surf.blit(os_font.render(os_config.txt("İşaretle ve pencereyi yeniden aç","Check and reopen window"), True, GRI), (80,202))

                elif p == "HESAP":
                    pygame.draw.rect(surf, BEYAZ, (10,10,230,50))
                    yazi_h = os_buyuk_font.render(hesap_metni, True, SIYAH)
                    surf.blit(yazi_h, (230 - yazi_h.get_width(), 20))
                    butonlar = ["7","8","9","+","4","5","6","-","1","2","3","*","C","0","=","/"]
                    hx, hy = 10,80
                    for idx, b in enumerate(butonlar):
                        pygame.draw.rect(surf, (200,200,200), (hx,hy,50,50))
                        pygame.draw.rect(surf, SIYAH, (hx,hy,50,50),1)
                        surf.blit(os_buyuk_font.render(b, True, SIYAH), (hx+15, hy+10))
                        hx += 60
                        if (idx+1) % 4 == 0:
                            hx = 10
                            hy += 60

                elif p == "NOT":
                    yk = 10
                    for satir in not_metni.split("\n"):
                        surf.blit(os_font.render(satir, True, SIYAH), (10, yk))
                        yk += 20
                    if odak_pencere == "NOT" and abs(math.sin(suan * 0.005)) > 0.5:
                        gen = os_font.render(not_metni.split("\n")[-1], True, SIYAH).get_width()
                        pygame.draw.line(surf, SIYAH, (10+gen, yk-20), (10+gen, yk-5), 2)

                elif p == "DUVAR":
                    b_y = 20
                    for kagit in duvar_kagitlari:
                        surf.blit(kagit["kucuk"], (20, b_y))
                        surf.blit(os_baslik_font.render(kagit["isim"], True, SIYAH), (160, b_y+30))
                        b_y += 100

                elif p == "OYUNLAR":
                    ikon_ciz(surf, pygame.Rect(30,30,60,60), ikon_zar_resmi, "ZarKrali.exe", "")
                    ikon_ciz(surf, pygame.Rect(120,30,60,60), ikon_mayin, "MayinTarlasi.exe", "")
                    ikon_ciz(surf, pygame.Rect(210,30,60,60), ikon_hl3, "Half-Life 3.exe", "")
                    if os_config.oyun_kayipruh_indirildi:
                        ikon_ciz(surf, pygame.Rect(300,30,60,60), ikon_kayipruh, "KayipRuh.exe", "")

                elif p == "MAYIN":
                    for r in range(10):
                        for c in range(10):
                            pygame.draw.rect(surf, SIYAH, pygame.Rect(c*40, r*40, 40, 40), 1)
                            if mayin_gorunum[r][c] == 1:
                                pygame.draw.rect(surf, (220,220,220), (c*40+1, r*40+1, 38, 38))
                                if mayin_grid[r][c] == -1:
                                    pygame.draw.circle(surf, SIYAH, (c*40+20, r*40+20), 10)
                                elif mayin_grid[r][c] > 0:
                                    surf.blit(mayin_font.render(str(mayin_grid[r][c]), True, (0,0,200)), (c*40+13, r*40+6))
                            else:
                                pygame.draw.rect(surf, (150,150,150), (c*40+1, r*40+1, 38, 38))
                    if mayin_durum != "Oynuyor":
                        renk = KIRMIZI if mayin_durum == "Kaybettin" else YESIL
                        pygame.draw.rect(surf, renk, (100,150,200,60))
                        d_yazi = os_buyuk_font.render(mayin_durum, True, BEYAZ)
                        surf.blit(d_yazi, (200 - d_yazi.get_width()//2, 165))

                elif p == "HL3":
                    surf.blit(os_baslik_font.render(os_config.txt("Yurutulebilir dosya eksik.","Executable missing."), True, SIYAH), (150 - 150//2, 35))
                    pygame.draw.rect(surf, GRI, (100,100,100,30), 1)
                    surf.blit(os_font.render("OK", True, SIYAH), (140,105))

                elif p == "KAYIP":
                    surf.fill(SIYAH)
                    if LOST_SOUL_AVAILABLE and lost_soul_game_instance is not None:
                        lost_soul_game_instance.focused = (odak_pencere == "KAYIP")
                        try:
                            lost_soul_game_instance.update()
                            lost_soul_game_instance.draw(surf)
                        except Exception as e:
                            surf.fill(SIYAH)
                            surf.blit(os_font.render(f"Hata: {e}", True, KIRMIZI), (50, 50))
                    else:
                        surf.fill(SIYAH)
                        pygame.draw.circle(surf, KIRMIZI, (kayipruh_oyuncu_x, kayipruh_oyuncu_y), 15)
                        yazi1 = g_font.render("KAYIP RUH", True, (150,0,0))
                        surf.blit(yazi1, (400 - yazi1.get_width()//2, 100))
                        surf.blit(os_baslik_font.render(os_config.txt("W A S D ile hareket et","Use W A S D to move"), True, BEYAZ), (320,500))

                elif p == "BILGISAYAR":
                    surf.fill((240,240,240))
                    pygame.draw.rect(surf, (220,220,220), (0,0,150,h))
                    sol_klasorler = ["Giriş", "Galeri", "Kullanıcı - Kişisel", "Masaüstü", "İndirilenler", "Belgeler", "Resimler", "Müzikler", "Videolar"]
                    for i, k in enumerate(sol_klasorler):
                        pygame.draw.rect(surf, (240,240,240), (10, 20 + i*30, 130, 25))
                        surf.blit(os_font.render(k, True, SIYAH), (20, 24 + i*30))
                    surf.blit(os_buyuk_font.render("Cihazlar ve sürücüler", True, SIYAH), (170, 20))
                    disk_icon = guvenli_resim_yukle("computer.png", "windows", (32,32))
                    surf.blit(disk_icon, (180, 70))
                    surf.blit(os_baslik_font.render("Yerel Disk (C:)", True, SIYAH), (220, 75))
                    surf.blit(os_font.render("40 GB boş, 240 GB toplam", True, GRI), (220, 95))

                elif p == "COP":
                    surf.fill((240,240,240))
                    dosyalar = ["savegame.json", "story_system.py", "os_config.py", "browser_pages.py", "trash.png", "Iconshock-Vista-General-Trash.ico", "Windows Startup.wav", "LogCS","README.txt"]
                    for i, dosya in enumerate(dosyalar):
                        renk = SIYAH if i % 2 == 0 else (50,50,50)
                        surf.blit(os_font.render(dosya, True, renk), (30, 20 + i*25))

                elif p == "KAMERA":
                    if kamera_arkaplan:
                        surf.blit(kamera_arkaplan, (0, 0))
                    if kamera_karakter:
                        ofset_y = int(math.sin(suan * 0.002) * 5) + 10
                        surf.blit(kamera_karakter, (0, ofset_y))
                    else:
                        surf.blit(os_font.render("Kamera görüntüsü yok", True, BEYAZ), (20, 100))

                elif p == "ZAR":
                    surf.blit(guncel_arka_plan, (0,0))
                    if oyun_durumu == "ANA_MENU":
                        zk_ana_menuyu_ciz(surf)
                    elif oyun_durumu == "AYARLAR":
                        zk_ayarlari_ciz(surf)
                    elif oyun_durumu == "MARKET":
                        zk_marketi_ciz(surf)
                    elif oyun_durumu == "BOLUM_SECIMI":
                        zk_bolum_secim_ciz(surf)
                    elif oyun_durumu == "OYUN":
                        zk_oyun_ciz(surf, suan)
                    parcacik_ciz(surf)
                    if flas_suresi > 0:
                        flas_suresi -= 1
                        flas_yuzey = pygame.Surface((w,h), pygame.SRCALPHA)
                        flas_yuzey.fill((*flas_renk, 100))
                        surf.blit(flas_yuzey, (0,0))

                ekran.blit(surf, (info["x"], info["y"]))

        # --- GÖREV ÇUBUĞU ---
        tb_surface = pygame.Surface((OS_GENISLIK, 45), pygame.SRCALPHA)
        tb_surface.fill((20,30,40,140))
        ekran.blit(tb_surface, (0, OS_YUKSEKLIK - 45))
        ekran.blit(ikon_start, (5, OS_YUKSEKLIK - 43))

        if ikon_ag:
            ekran.blit(pygame.transform.scale(ikon_ag, (20,20)), (OS_GENISLIK - 80, OS_YUKSEKLIK - 35))
        saat_metni = pygame.time.get_ticks() // 1000
        saat_str = f"{12 + (saat_metni // 3600) % 12:02d}:{(saat_metni // 60) % 60:02d}"
        ekran.blit(os_font.render(saat_str, True, BEYAZ), (OS_GENISLIK - 50, OS_YUKSEKLIK - 33))

        tb_x = 60
        for p in pencere_sirasi:
            if not pencere_durumlari[p]["acik"]:
                continue
            tb_secim = pygame.Surface((140,35), pygame.SRCALPHA)
            if odak_pencere == p:
                tb_secim.fill((160,180,200,150))
            else:
                tb_secim.fill((100,120,140,100))
            ekran.blit(tb_secim, (tb_x, OS_YUKSEKLIK - 40))
            pygame.draw.rect(ekran, BEYAZ, (tb_x, OS_YUKSEKLIK - 40, 140, 35), 1)
            ikon_kucuk = pygame.transform.scale(ikonlar.get(p, ikon_folder), (20,20))
            ekran.blit(ikon_kucuk, (tb_x+5, OS_YUKSEKLIK - 33))
            ekran.blit(os_font.render(get_pencere_baslik(p)[:13], True, BEYAZ), (tb_x+30, OS_YUKSEKLIK - 33))
            tb_x += 145

        if os_baslat_acik:
            sm_rect = pygame.Rect(5, OS_YUKSEKLIK - 455, 380, 410)
            pygame.draw.rect(ekran, BEYAZ, (sm_rect.x, sm_rect.y, 240, sm_rect.height))
            pygame.draw.rect(ekran, (35,45,65), (sm_rect.x+240, sm_rect.y, 140, sm_rect.height))
            pygame.draw.rect(ekran, (200,210,230), (sm_rect.x, sm_rect.y+360, 380, 50))
            kapat_btn = pygame.Rect(260, OS_YUKSEKLIK - 75, 120, 25)
            pygame.draw.rect(ekran, (180,50,50) if kapat_btn.collidepoint(mouse_x,mouse_y) else (150,160,170), kapat_btn, border_radius=3)
            ekran.blit(os_baslik_font.render(os_config.txt("Ana Menu","Main Menu"), True, BEYAZ), (290, OS_YUKSEKLIK - 73))
            pygame.draw.rect(ekran, (200,200,200), (300, OS_YUKSEKLIK - 435, 64, 64))
            ekran.blit(pygame.transform.scale(ikon_login, (60,60)), (302, OS_YUKSEKLIK - 433))
            ekran.blit(os_baslik_font.render(os_config.txt("Kullanici","User"), True, BEYAZ), (285, OS_YUKSEKLIK - 360))

            p_items = [
                (os_config.txt("Zar Krali","Dice King"), ikon_zar_resmi),
                (os_config.txt("Tarayici","Browser"), ikon_explorer),
                (os_config.txt("Mayin Tarlasi","Minesweeper"), ikon_mayin),
                (os_config.txt("Hesap Makinesi","Calculator"), ikon_cal),
                (os_config.txt("Not Defteri","Notepad"), ikon_not),
                (os_config.txt("Duvar Kagidi","Wallpaper"), ikon_folder),
                (os_config.txt("Bilgisayarim","Computer"), ikon_computer),
                (os_config.txt("Cop Kutusu","Recycle Bin"), ikon_trash)
            ]
            iy = OS_YUKSEKLIK - 445
            for ad, img in p_items:
                ekran.blit(pygame.transform.scale(img, (32,32)), (15, iy))
                ekran.blit(os_baslik_font.render(ad, True, SIYAH), (60, iy+6))
                iy += 45

    elif sistem_durumu == "OYUN_SONU":
        ekran.fill(SIYAH)
        tekst = g_font.render("KAYIP RUH", True, KIRMIZI)
        alt_tekst1 = os_buyuk_font.render("SİMÜLASYON TAMAMLANDI.", True, BEYAZ)
        alt_tekst2 = os_baslik_font.render("Sistemden başarıyla çıkış yapıldı. Ruhunuz serbest.", True, GRI)
        ekran.blit(tekst, (OS_GENISLIK//2 - tekst.get_width()//2, OS_YUKSEKLIK//2 - 120))
        ekran.blit(alt_tekst1, (OS_GENISLIK//2 - alt_tekst1.get_width()//2, OS_YUKSEKLIK//2 + 20))
        ekran.blit(alt_tekst2, (OS_GENISLIK//2 - alt_tekst2.get_width()//2, OS_YUKSEKLIK//2 + 80))
        
        if suan - oyun_sonu_zamani > 5000:
            sistem_durumu = "ANA_GIRIS"
            yeni_oyun_sifirla()

    # --- BİLDİRİM ---
    if bildirim_metni:
        metin_surf = os_buyuk_font.render(bildirim_metni, True, BEYAZ)
        arka_plan = pygame.Surface((metin_surf.get_width()+20, 40))
        arka_plan.fill((0,150,0))
        arka_plan.set_alpha(220)
        ekran.blit(arka_plan, (OS_GENISLIK - metin_surf.get_width() - 30, 10))
        ekran.blit(metin_surf, (OS_GENISLIK - metin_surf.get_width() - 20, 15))

    # --- DİYALOG ---
    if story_system.dialog_aktif:
        pygame.draw.rect(ekran, (0,0,0,200), (0, OS_YUKSEKLIK-105, OS_GENISLIK, 60))
        d_yazi = os_buyuk_font.render(story_system.gosterilen_dialog, True, BEYAZ)
        ekran.blit(d_yazi, (OS_GENISLIK//2 - d_yazi.get_width()//2, OS_YUKSEKLIK-90))
        if story_system.dialog_harf_indeksi == len(story_system.dialog_metni):
            t_yazi = os_font.render(os_config.txt("(Tikla)","(Click)"), True, GRI)
            ekran.blit(t_yazi, (OS_GENISLIK - t_yazi.get_width() - 20, OS_YUKSEKLIK - 70))

    pygame.display.update()
    saat.tick(60)

pygame.quit()
sys.exit()