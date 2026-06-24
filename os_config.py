# os_config.py
import json
import os

OS_GENISLIK = 1280
OS_YUKSEKLIK = 720

BEYAZ = (255, 255, 255)
SIYAH = (0, 0, 0)
KIRMIZI = (220, 20, 60)
YESIL = (50, 205, 50)
GRI = (100, 100, 100)
TURUNCU = (255, 140, 0)
SARI = (255, 215, 0)
MOR = (148, 0, 211)

OS_ARKA_PLAN_RENK = (0, 100, 150)
OS_PENCERE_BASLIK = (150, 180, 220)

os_dil = "TR"
os_sistem_sesi = 50

hikaye_asamasi = 0
mail_basvuruldu = False
mail_geldi = False
oyun_kayipruh_indirildi = False
lost_soul_unlocked = False
lost_soul_hatali = False
lost_soul_ikinci_bolum = False

# Masaüstü txt'den okunan kod
lost_soul_code = ""
lost_soul_txt_path = ""

# Zamanlayıcı (10 saniye sonra mail için)
lost_soul_mail_zamani = 0
lost_soul_mail_bekleniyor = False

toplam_altin = 100
zar_seviyesi = 1
alan_seviyesi = 1
kilit_acik_bolum = 1

not_metni = ""
hesap_metni = ""

def txt(tr, en):
    return tr if os_dil == "TR" else en

class SaveManager:
    def __init__(self, dosya_adi="savegame.json"):
        self.dosya_adi = dosya_adi

    def kaydet(self):
        veri = {
            "altin": toplam_altin,
            "zar_seviyesi": zar_seviyesi,
            "alan_seviyesi": alan_seviyesi,
            "kilit_acik_bolum": kilit_acik_bolum,
            "hikaye_asamasi": hikaye_asamasi,
            "mail_basvuruldu": mail_basvuruldu,
            "mail_geldi": mail_geldi,
            "oyun_kayipruh_indirildi": oyun_kayipruh_indirildi,
            "lost_soul_unlocked": lost_soul_unlocked,
            "lost_soul_hatali": lost_soul_hatali,
            "lost_soul_ikinci_bolum": lost_soul_ikinci_bolum,
            "lost_soul_code": lost_soul_code,
            "lost_soul_txt_path": lost_soul_txt_path,
            "not_metni": not_metni,
            "hesap_metni": hesap_metni
        }
        try:
            with open(self.dosya_adi, 'w', encoding='utf-8') as f:
                json.dump(veri, f, indent=4)
        except:
            pass

    def yukle(self):
        global toplam_altin, zar_seviyesi, alan_seviyesi, kilit_acik_bolum
        global hikaye_asamasi, mail_basvuruldu, mail_geldi, oyun_kayipruh_indirildi
        global not_metni, hesap_metni, lost_soul_unlocked, lost_soul_hatali, lost_soul_ikinci_bolum
        global lost_soul_code, lost_soul_txt_path
        if os.path.exists(self.dosya_adi):
            try:
                with open(self.dosya_adi, 'r', encoding='utf-8') as f:
                    veri = json.load(f)
                    toplam_altin = veri.get("altin", 100)
                    zar_seviyesi = veri.get("zar_seviyesi", 1)
                    alan_seviyesi = veri.get("alan_seviyesi", 1)
                    kilit_acik_bolum = veri.get("kilit_acik_bolum", 1)
                    hikaye_asamasi = veri.get("hikaye_asamasi", 0)
                    mail_basvuruldu = veri.get("mail_basvuruldu", False)
                    mail_geldi = veri.get("mail_geldi", False)
                    oyun_kayipruh_indirildi = veri.get("oyun_kayipruh_indirildi", False)
                    lost_soul_unlocked = veri.get("lost_soul_unlocked", False)
                    lost_soul_hatali = veri.get("lost_soul_hatali", False)
                    lost_soul_ikinci_bolum = veri.get("lost_soul_ikinci_bolum", False)
                    lost_soul_code = veri.get("lost_soul_code", "")
                    lost_soul_txt_path = veri.get("lost_soul_txt_path", "")
                    not_metni = veri.get("not_metni", "")
                    hesap_metni = veri.get("hesap_metni", "")
            except:
                pass

kayit_sistemi = SaveManager()
kayit_sistemi.yukle()