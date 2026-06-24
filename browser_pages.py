# browser_pages.py
import os_config
from datetime import datetime

# --- SAHTE İLANLAR ---
def get_sahte_ilanlar():
    if os_config.mail_basvuruldu:
        return []
    return [
        (os_config.txt("Satis Danismani", "Sales Consultant"), os_config.txt("Magazacilik A.S. - 22.000 TL", "Retail Inc. - $2.200"), False, os_config.txt("Sektorde oncu firmamizin yeni acilacak magazasi icin dinamik takim arkadaslari ariyoruz.\nTercihen perakende satis konusunda en az 2 yil deneyimli.", "Seeking dynamic teammates for our new retail store.")),
        (os_config.txt("Muhasebe Uzmani", "Accounting Expert"), os_config.txt("ABC Sirketi - 35.000 TL", "ABC Corp - $3.500"), False, os_config.txt("Finans departmaninda gorevlendirilmek uzere Muhasebe Uzmani ariyoruz.", "Looking for an Accounting Expert.")),
        (os_config.txt("Cagri Merkezi Temsilcisi", "Call Center Agent"), os_config.txt("NetCall - 20.000 TL", "NetCall - $2.000"), False, os_config.txt("Diksiyonu duzgun calisma arkadaslari ariyoruz.\nVardiyali sistemde calismaya engel durumu olmayan.", "Looking for call center agents.")),
        (os_config.txt("Grafik Tasarimci", "Graphic Designer"), os_config.txt("ReklamAjans - 25.000 TL", "AdAgency - $2.500"), False, os_config.txt("Yaratici ekibimize katilacak Grafik Tasarimci ariyoruz.\nAdobe Photoshop, Illustrator ve InDesign programlarina ileri seviyede hakim.", "Looking for a Graphic Designer.")),
        (os_config.txt("Oyun Test Uzmani", "Game Tester"), os_config.txt("Gizli Sirket - ???", "Secret Corp - ???"), True, os_config.txt("TECRUBE ISTENMIYOR! Yeni nesil bir korku projesi icin test uzmanlari ariyoruz.\nEvden esnek saatlerde calisabilirsiniz.\nSadece gonderecegimiz sifreli dosyalari oynayin.\nProje gizlidir, oyun ici goruntu paylasmak yasaktir.", "NO EXPERIENCE NEEDED! Looking for testers for a new horror project."))
    ]

# --- SAHTE HABERLER ---
def get_sahte_haberler():
    return [
        (os_config.txt("Kripto Piyasalari Coktu!", "Crypto Markets Crashed!"), os_config.txt("Dun gece yasanan inanilmaz dusus yatirimcilari panikletti.", "Last night's massive drop panicked investors."), os_config.txt("Dunya genelinde kripto para piyasalari cokuse sahne oldu.", "Worldwide crypto markets witnessed a historic crash.")),
        (os_config.txt("Bilinmeyen Oyun Salgini", "Unknown Game Epidemic"), os_config.txt("Bir oyun hakkinda internet uzerinde gariplikler artiyor...", "Weirdness increases on the internet about a specific game..."), os_config.txt("Derin web forumlarinda 'Kayip Ruh' isimli oyunu oynayanlar paranoid hezeyanlar yasiyor.", "Players of a game called 'Lost Soul' are experiencing paranoid delusions.")),
        (os_config.txt("Genc Yazilimci Kayip", "Young Developer Missing"), os_config.txt("Evinden ciktiktan sonra bir daha haber alinamadi.", "He hasn't been heard from since leaving his house."), os_config.txt("24 yasindaki oyun gelistiricisi Yasin Y. kayboldu. Masasinda 'Sadece test ediyordum' yazili bir not bulundu.", "24-year-old developer Yasin Y. is missing."))
    ]

# --- GMAIL GELEN KUTUSU ---
gelen_kutusu = [
    {"gonderen": "Trendyol", "konu_tr": "Sepetinizdeki urunlerin fiyati dustu!", "konu_en": "Prices dropped in your cart!", "icerik_tr": "Hemen sitemize girip sepetinizi onaylayin.\nKampanyalar cok kisa sureli!", "icerik_en": "Check your cart now.", "yeni": False},
    {"gonderen": "Steam", "konu_tr": "Istek listenizdeki oyunlarda %50 indirim", "konu_en": "50% off on your wishlist", "icerik_tr": "Zar Krali ve bircok oyunda inanilmaz bahar indirimleri basladi.", "icerik_en": "Incredible spring sales have started for Dice King.", "yeni": False},
    {"gonderen": "Garanti Bankasi", "konu_tr": "Hesap ozetiniz hazir", "konu_en": "Your account statement is ready", "icerik_tr": "Sayin musterimiz, Mart ayi hesap ozetiniz ekte sunulmustur.\nDetaylar icin mobil uygulamayi ziyaret edin.", "icerik_en": "Dear customer, your March account statement is attached.", "yeni": True},
    {"gonderen": "Kargo Takip", "konu_tr": "Paketiniz yolda", "konu_en": "Your package is on the way", "icerik_tr": "Siparis numaraniz: 123456\nTahmini teslimat: 2 is gunu icerisinde.", "icerik_en": "Order number: 123456\nEstimated delivery within 2 business days.", "yeni": True},
    {"gonderen": "LinkedIn", "konu_tr": "Sizin icin 5 yeni is ilani", "konu_en": "5 new job offers for you", "icerik_tr": "Profilinize uygun yeni is ilanlari listelendi.\nHemen inceleyin ve basvurun.", "icerik_en": "New job offers matching your profile are listed.\nCheck them now.", "yeni": True},
    {"gonderen": "Netflix", "konu_tr": "Yeni sezon geliyor!", "konu_en": "New season coming!", "icerik_tr": "En cok izlediginiz dizinin yeni sezonu 15 Nisan'da yayinda.\nHatirlatma ayarlayin.", "icerik_en": "The new season of your favorite show is coming on April 15.\nSet a reminder.", "yeni": True},
    {"gonderen": "Spotify", "konu_tr": "Haftalik keşif listesi", "konu_en": "Weekly discovery playlist", "icerik_tr": "Bu hafta sizin icin secilen sarkilar listelendi.\nDinlemeye baslayin.", "icerik_en": "Your weekly discovery playlist is ready.\nStart listening.", "yeni": True}
]

if os_config.mail_geldi and "GIZLI YONETICI" not in [m["gonderen"] for m in gelen_kutusu]:
    gelen_kutusu.insert(0, {
        "gonderen": "GIZLI YONETICI",
        "konu_tr": "TEST ONAYLANDI.",
        "konu_en": "TEST APPROVED.",
        "icerik_tr": "Başvurun Onaylandı. \nGönderilen oyun dosyasını indir ve test et.\nHataları bize bildir ve evde yanlız olduğundan emin ol.",
        "icerik_en": "Test phase completed. \nDownload 'LostSoul' game below.\nWARNING: Be careful.",
        "yeni": False
    })

# --- TARAYICI DEĞİŞKENLERİ ---
secili_mail = None
tarayici_sekme = "Google"
tarayici_scroll = 0
tarayici_arama_metni = ""

# Güncelleme indirme için (main.py'de kullanılır)
chat_dosya_gonderildi = False