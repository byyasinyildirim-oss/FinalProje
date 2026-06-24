# lost_soul_game.py
import pygame
import random
import os
import math
import json
import sys
import os_config

# Renkler
SIYAH = (0, 0, 0)
KIRMIZI = (180, 0, 0)
KAN_KIRMIZI = (100, 0, 0)
BEYAZ = (200, 200, 200)
GRI = (80, 80, 80)
KARANLIK = (10, 5, 5)
YESIL = (0, 200, 0)
SARI = (255, 255, 0)
TURUNCU = (255, 140, 0)

class LostSoulGame:
    def __init__(self, genislik=800, yukseklik=600, bolum=1):
        if not pygame.get_init():
            pygame.init()
        
        self.genislik = genislik
        self.yukseklik = yukseklik
        self.ekran_genislik = genislik
        self.ekran_yukseklik = yukseklik
        self.bolum = bolum
        
        # Oyun durumları
        self.menu_active = True
        self.oyun_active = False
        self.ayarlar_active = False
        self.pause_active = False
        self.running = True
        self.focused = True  # Pencere odağı kontrolü (main.py tarafından güncellenecek)
        
        # ========= BÖLÜM 2 ÖZEL & MATRİS LABİRENT =========
        self.labirent_aktif = False
        self.panel_kod_aktif = False
        self.panel_kod = ["0", "0", "0", "0", "0"]
        self.panel_kod_indeks = 0
        self.panel_kod_dogru = os_config.lost_soul_code if hasattr(os_config, 'lost_soul_code') and os_config.lost_soul_code else "00000"
        self.labirent_grid = []
        self.labirent_boyut = 15
        self.labirent_duvarlar = []
        self.labirent_baslangic = (1, 1)
        self.labirent_cikis = (13, 13)
        self.beast_labirent_pos = (13, 1)  # Başlangıçta canavar en uzak üst köşede doğar
        self.beast_hareket_suresi = 0
        self.beast_hareket_aralik = 270  # Karakterden hızlı dengeli peşleme hızı
        self.labirent_kazandi = False
        self.hak_sayisi = 3  # Labirent için toplam 3 hak
        
        # ========= SES =========
        self.settings_dosyasi = "lostsoul_settings.json"
        self.ses_seviyesi = self._settings_yukle()
        self.muzik_caliniyor = False
        self.locked_ses = None
        self.unlock_ses = None
        self.pickup_ses = None
        self.footsteps_ses = None
        self.glitch_ses = None
        self.error_ses = None
        self.laugh_ses = None
        self._load_sounds()
        
        # ========= IŞIK =========
        self.isik_yaricap = 90
        
        # ========= BAŞLANGIÇ YAZISI =========
        self.baslangic_yazisi_aktif = False
        self.baslangic_yazisi_suresi = 0
        self.baslangic_yazisi_baslangic = 0
        self.baslangic_yazisi_alpha = 255
        self.baslangic_yazisi_goster = False
        self.baslangic_yazisi_siyah_arkaplan = False
        if bolum == 2:
            self.baslangic_yazisi_metni = "Geri Dönüş"
        else:
            self.baslangic_yazisi_metni = "Uyanış"
        
        # ========= KARAKTER =========
        self.oyuncu_w = 64
        self.oyuncu_h = 64
        self.oyuncu_hiz = 4
        self.carpisma_w = 44
        self.carpisma_h = 44
        self.oyuncu_rect = pygame.Rect(0, 0, self.carpisma_w, self.carpisma_h)
        self.yon = "down"
        self.hareket_ediyor = False
        self.animasyon_sayaci = 0
        self.animasyon_hizi = 8
        self.mevcut_kare = 0
        
        # ========= SPRITE'LAR =========
        self.sprite_animasyonlar = self._load_sprites()
        self.zemin_dokusu = self._load_ground_texture()
        self.canavar_sprite = self._load_beast_sprites()
        
        # ========= HARİTA =========
        self.duvarlar = []
        self.kapilar = []
        self.odalar = []
        self._harita_olustur()
        
        # ========= ANAHTARLAR =========
        self.anahtar1_rect = None
        self.anahtar1_toplandi = False
        self.anahtar_bulmaca_zeminde = False
        self.anahtar_bulmaca_x = 0
        self.anahtar_bulmaca_y = 0
        self.anahtar_bulmaca_envanterde = False
        self.anahtar_panel_zeminde = False
        self.anahtar_panel_x = 0
        self.anahtar_panel_y = 0
        self.anahtar_panel_envanterde = False
        
        self._anahtar1_olustur()
        
        # ========= BULMACA =========
        self.bulmaca_kareleri = []
        self.bulmaca_aktif = False
        self.bulmaca_cozuldu = False
        
        # ========= SEMBOL PANELİ (Bölüm 1) =========
        self.panel_aktif = False
        self.panel_semboller = ["♦", "♥", "♠", "♣"]
        self.dogru_sira = ["♦", "♥", "♠", "♣"]
        self.girilen_sira = []
        self.panel_sembol_goster = 0
        self.panel_cozuldu = False
        
        # ========= GLITCH (Beast) =========
        self.glitch_aktif = False
        self.glitch_baslangic = 0
        self.glitch_suresi = 2000
        self.glitch_item_aktif = True
        
        # Canavarı kapının hemen dibine değil, odanın en arka ucuna yerleştirir (+180 ofset)
        sag_oda2_kapi = next(k for k in self.kapilar if k["id"] == "sag_oda2_kapi")
        kapi_rect = sag_oda2_kapi["rect"]
        beast_boyut = 80
        self.glitch_item_rect = pygame.Rect(
            kapi_rect.x + kapi_rect.width + 180,
            kapi_rect.centery - beast_boyut // 2,
            beast_boyut, beast_boyut
        )
        
        # ========= BÖLÜM 2 HAZIRLIK =========
        if bolum == 2:
            self._bolum2_hazirlik()
            self._labirent_olustur()
        
        # ========= OYUNCU SPAWN =========
        baslangic_oda = next(o for o in self.odalar if o["id"] == self.baslangic_oda_id)
        spawn_x = baslangic_oda["rect"].centerx - self.carpisma_w // 2
        spawn_y = baslangic_oda["rect"].centery - self.carpisma_h // 2
        self.oyuncu_rect = pygame.Rect(spawn_x, spawn_y, self.carpisma_w, self.carpisma_h)
        
        # ========= KAMERA =========
        hedef_kamera_x = self.oyuncu_rect.centerx - (self.ekran_genislik // 2)
        hedef_kamera_y = self.oyuncu_rect.centery - (self.ekran_yukseklik // 2)
        self.kamera_x, self.kamera_y = self._kamera_sinirla(hedef_kamera_x, hedef_kamera_y)
        
        # ========= FONT =========
        self.font = pygame.font.SysFont("arial", 32)
        self.buyuk_font = pygame.font.SysFont("arial", 72, bold=True)
        self.kucuk_font = pygame.font.SysFont("arial", 24)
        self.baslik_font = pygame.font.SysFont("arial", 90, bold=True)
        self.mesaj_font = pygame.font.SysFont("arial", 36, bold=True)
        self.glitch_font = pygame.font.SysFont("courier", 28, bold=True)
        
        # ========= MENÜ =========
        self.menu_secenekleri = ["Oyna", "Ayarlar", "Çıkış"]
        self.secili_indeks = 0
        self.pause_secenekleri = ["Oyuna Dön", "Ayarlar", "Ana Menü"]
        self.pause_indeks = 0
        
        # ========= KAPI MESAJLARI =========
        self.kapi_mesaji = ""
        self.kapi_mesaji_goster = False
        self.son_locked_ses_zamani = 0
        
        self.sembol_odalar = {}
        self._sembolleri_yerlestir()
    
    # ----------------------------------------------------------------
    # BÖLÜM 2 HAZIRLIK
    # ----------------------------------------------------------------
    def _bolum2_hazirlik(self):
        for kapi in self.kapilar:
            kapi["acik"] = True
            kapi["kilitli"] = False

        self.sembol_odalar = {}
        self.bulmaca_aktif = False
        self.bulmaca_cozuldu = True
        self.glitch_item_aktif = False

        # Sayısal Kod Paneli Başlangıçta Kapalı
        self.panel_kod_aktif = False
        self.panel_kod = ["0", "0", "0", "0", "0"]
        self.panel_kod_indeks = 0
    
    # ----------------------------------------------------------------
    # MATRİS LABİRENT (Paylaşılan görseldeki temiz matrise uyarlandı)
    # ----------------------------------------------------------------
    def _labirent_olustur(self):
        labirent = [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,1,0,0,0,0,0,0,0,1,0,1],
            [1,1,1,0,1,0,1,1,1,1,1,0,1,0,1],
            [1,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
            [1,0,1,1,1,1,1,1,0,1,1,1,1,0,1],
            [1,0,1,0,0,0,0,1,0,0,0,0,1,0,1],
            [1,0,1,0,1,1,0,1,1,1,1,1,1,0,1],
            [1,0,0,0,1,0,0,0,0,0,0,0,1,0,1],
            [1,1,1,1,1,0,1,1,1,1,1,1,1,0,1],
            [1,0,0,0,1,0,1,0,0,0,1,0,0,0,1],
            [1,0,1,0,1,0,1,0,1,0,1,0,1,1,1],
            [1,0,1,0,0,0,0,0,1,0,1,0,0,0,1],
            [1,0,1,1,1,1,1,1,1,0,1,1,1,0,1],
            [1,0,0,0,0,0,0,0,0,0,1,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
        ]
        self.labirent_grid = labirent
        self.labirent_boyut = 15
        self.labirent_duvarlar = []
        for r in range(self.labirent_boyut):
            for c in range(self.labirent_boyut):
                if labirent[r][c] == 1:
                    self.labirent_duvarlar.append((c, r))
        
        self.labirent_baslangic = (1, 1)
        self.labirent_cikis = (13, 13)
        self.beast_labirent_pos = (13, 1)
        self.beast_hareket_suresi = pygame.time.get_ticks()
    
    def _labirent_duvar_kontrol(self, x, y):
        if x < 0 or y < 0 or x >= self.labirent_boyut or y >= self.labirent_boyut:
            return True
        return self.labirent_grid[y][x] == 1
    
    def _labirent_cikis_kontrol(self, x, y):
        return (x, y) == self.labirent_cikis
    
    def _beast_labirent_hareket(self):
        now = pygame.time.get_ticks()
        if now - self.beast_hareket_suresi < self.beast_hareket_aralik:
            return
        
        oyuncu_x = (self.oyuncu_rect.centerx - 100) // 50
        oyuncu_y = (self.oyuncu_rect.centery - 100) // 50
        bx, by = self.beast_labirent_pos
        
        dx = oyuncu_x - bx
        dy = oyuncu_y - by
        
        # Doğrudan kovalama algoritması (Mesafe şartı kaldırıldı)
        if abs(dx) > abs(dy):
            adim_x = 1 if dx > 0 else -1
            if not self._labirent_duvar_kontrol(bx + adim_x, by):
                self.beast_labirent_pos = (bx + adim_x, by)
            elif not self._labirent_duvar_kontrol(bx, by + (1 if dy > 0 else -1)):
                self.beast_labirent_pos = (bx, by + (1 if dy > 0 else -1))
        else:
            adim_y = 1 if dy > 0 else -1
            if not self._labirent_duvar_kontrol(bx, by + adim_y):
                self.beast_labirent_pos = (bx, by + adim_y)
            elif not self._labirent_duvar_kontrol(bx + (1 if dx > 0 else -1), by):
                self.beast_labirent_pos = (bx + (1 if dx > 0 else -1), by)
                
        self.beast_hareket_suresi = now
    
    def _labirent_baslat(self):
        # Oyuncunun merkezlenmesi için hücre ortasına (+25 piksel) ofset eklendi
        oyuncu_x = self.labirent_baslangic[0] * 50 + 100 + 25
        oyuncu_y = self.labirent_baslangic[1] * 50 + 100 + 25
        self.oyuncu_rect.x = oyuncu_x - self.carpisma_w // 2
        self.oyuncu_rect.y = oyuncu_y - self.carpisma_h // 2
        
        self.beast_labirent_pos = (13, 1) # Canavar en uzak üst köşede başlar
        self.beast_hareket_suresi = pygame.time.get_ticks()
        self.labirent_kazandi = False
        
        # Kamera sınırlarını labirent boyutuna göre doğru şekilde set ediyoruz
        duvar_boyut = 50
        labirent_genislik = self.labirent_boyut * duvar_boyut + 200
        labirent_yukseklik = self.labirent_boyut * duvar_boyut + 200
        hedef_kamera_x = self.oyuncu_rect.centerx - (self.ekran_genislik // 2)
        hedef_kamera_y = self.oyuncu_rect.centery - (self.ekran_yukseklik // 2)
        self.kamera_x = max(0, min(hedef_kamera_x, labirent_genislik - self.ekran_genislik))
        self.kamera_y = max(0, min(hedef_kamera_y, labirent_yukseklik - self.ekran_yukseklik))

    # ----------------------------------------------------------------
    # PANEL KOD (Sayısal - Bölüm 2 Yön Kontrolleri Düzeltildi)
    # ----------------------------------------------------------------
    def _panel_kod_ciz(self, surface):
        w, h = surface.get_width(), surface.get_height()
        karartma = pygame.Surface((w, h), pygame.SRCALPHA)
        karartma.fill((0, 0, 0, 200))
        surface.blit(karartma, (0, 0))
        
        panel_w, panel_h = 500, 300
        panel_x = w//2 - panel_w//2
        panel_y = h//2 - panel_h//2
        pygame.draw.rect(surface, (30, 30, 30), (panel_x, panel_y, panel_w, panel_h))
        pygame.draw.rect(surface, BEYAZ, (panel_x, panel_y, panel_w, panel_h), 3)
        
        baslik = self.buyuk_font.render("KODU GİR", True, BEYAZ)
        surface.blit(baslik, baslik.get_rect(center=(w//2, panel_y + 40)))
        
        for i in range(5):
            x = panel_x + 80 + i * 70
            y = panel_y + 100
            pygame.draw.rect(surface, SIYAH, (x, y, 50, 60))
            pygame.draw.rect(surface, BEYAZ, (x, y, 50, 60), 2)
            yazi = self.buyuk_font.render(self.panel_kod[i], True, SARI if i == self.panel_kod_indeks else BEYAZ)
            surface.blit(yazi, yazi.get_rect(center=(x+25, y+30)))
            if i == self.panel_kod_indeks:
                pygame.draw.rect(surface, YESIL, (x, y, 50, 60), 4)
        
        kontrol = self.kucuk_font.render("W/S: Değeri değiştir  A/D: Hane seç  SPACE: Onayla", True, GRI)
        surface.blit(kontrol, kontrol.get_rect(center=(w//2, panel_y + panel_h - 30)))
        kod_str = "Kod: " + "".join(self.panel_kod)
        kod_yazi = self.kucuk_font.render(kod_str, True, BEYAZ)
        surface.blit(kod_yazi, (panel_x + 20, panel_y + 210))
    
    def _panel_kod_isle(self):
        dosya_yolu = os.path.join("Assets", "desktop", "code.txt")
        if os.path.exists(dosya_yolu):
            with open(dosya_yolu, 'r') as f:
                dogru_kod = f.read().strip()
        else:
            dogru_kod = None

        girilen = "".join(self.panel_kod)

        if dogru_kod and girilen == dogru_kod:
            self.panel_kod_aktif = False
            self.labirent_aktif = True
            self._labirent_baslat()
            self._ses_oynat(self.unlock_ses)
            return True
        else:
            self._ses_oynat(self.error_ses)
            return False
    
    # ----------------------------------------------------------------
    # ANAHTAR1
    # ----------------------------------------------------------------
    def _anahtar1_olustur(self):
        oda = next(o for o in self.odalar if o["id"] == "sol_oda3")
        self.anahtar1_rect = pygame.Rect(oda["rect"].centerx - 16, oda["rect"].centery - 16, 32, 32)
        self.anahtar1_toplandi = False
    
    # ----------------------------------------------------------------
    # SES YÜKLEME
    # ----------------------------------------------------------------
    def _load_sounds(self):
        try:
            self.locked_ses = pygame.mixer.Sound(os.path.join("Assets", "soundeffect", "lostsoul", "locked.mp3"))
            self.locked_ses.set_volume(self.ses_seviyesi / 100)
        except:
            self.locked_ses = None
        try:
            self.unlock_ses = pygame.mixer.Sound(os.path.join("Assets", "soundeffect", "lostsoul", "unlock.mp3"))
            self.unlock_ses.set_volume(self.ses_seviyesi / 100)
        except:
            self.unlock_ses = None
        try:
            self.pickup_ses = pygame.mixer.Sound(os.path.join("Assets", "soundeffect", "lostsoul", "pickup.mp3"))
            self.pickup_ses.set_volume(self.ses_seviyesi / 100)
        except:
            self.pickup_ses = None
        try:
            self.footsteps_ses = pygame.mixer.Sound(os.path.join("Assets", "soundeffect", "lostsoul", "footsteps.mp3"))
            self.footsteps_ses.set_volume(self.ses_seviyesi / 100)
        except:
            self.footsteps_ses = None
        try:
            self.glitch_ses = pygame.mixer.Sound(os.path.join("Assets", "soundeffect", "lostsoul", "glitch.mp3"))
            self.glitch_ses.set_volume(self.ses_seviyesi / 100)
        except:
            self.glitch_ses = None
        try:
            self.error_ses = pygame.mixer.Sound(os.path.join("Assets", "soundeffect", "lostsoul", "error.mp3"))
            self.error_ses.set_volume(self.ses_seviyesi / 100)
        except:
            self.error_ses = None
        try:
            self.laugh_ses = pygame.mixer.Sound(os.path.join("Assets", "soundeffect", "lostsoul", "laugh.mp3"))
            self.laugh_ses.set_volume(self.ses_seviyesi / 100)
        except:
            self.laugh_ses = None
        try:
            self.lostsong_muzik = os.path.join("Assets", "soundeffect", "lostsoul", "lostsong.mp3")
        except:
            self.lostsong_muzik = None
    
    def _ses_oynat(self, ses):
        if ses:
            ses.set_volume(self.ses_seviyesi / 100)
            ses.play()
    
    def _ses_stop(self, ses):
        if ses:
            ses.stop()
    
    def _ses_guncelle(self):
        if self.muzik_caliniyor:
            pygame.mixer.music.set_volume(self.ses_seviyesi / 100)
        for ses in [self.footsteps_ses, self.locked_ses, self.unlock_ses, self.pickup_ses, self.glitch_ses, self.error_ses, self.laugh_ses]:
            if ses:
                ses.set_volume(self.ses_seviyesi / 100)
    
    def _settings_yukle(self):
        try:
            with open(self.settings_dosyasi, 'r') as f:
                data = json.load(f)
                return data.get("ses_seviyesi", 50)
        except:
            return 50
    
    def _settings_kaydet(self):
        try:
            with open(self.settings_dosyasi, 'w') as f:
                json.dump({"ses_seviyesi": self.ses_seviyesi}, f)
        except:
            pass
    
    # ----------------------------------------------------------------
    # MÜZİK
    # ----------------------------------------------------------------
    def _muzik_play(self):
        if self.lostsong_muzik and not self.muzik_caliniyor:
            try:
                pygame.mixer.music.load(self.lostsong_muzik)
                pygame.mixer.music.set_volume(self.ses_seviyesi / 100)
                pygame.mixer.music.play(-1)
                self.muzik_caliniyor = True
            except:
                pass
    
    def _muzik_pause(self):
        if self.muzik_caliniyor:
            pygame.mixer.music.pause()
    
    def _muzik_unpause(self):
        if self.muzik_caliniyor:
            pygame.mixer.music.unpause()
    
    def _muzik_stop(self):
        if self.muzik_caliniyor:
            pygame.mixer.music.stop()
            self.muzik_caliniyor = False
    
    def oynat_ses(self):
        self._muzik_play()
    
    def durdur_ses(self):
        self._muzik_stop()
        if self.footsteps_ses:
            self.footsteps_ses.stop()
    
    # ----------------------------------------------------------------
    # HARİTA
    # ----------------------------------------------------------------
    def _kapili_duvar_olustur(self, sabit_baslangic, sabit_kalinlik,
                                degisken_baslangic, degisken_bitis,
                                kapi_merkez, kapi_genislik, dikey=True):
        kapi_bas = kapi_merkez - kapi_genislik / 2
        kapi_son = kapi_merkez + kapi_genislik / 2
        parcalar = []
        if dikey:
            if kapi_bas > degisken_baslangic:
                parcalar.append(pygame.Rect(int(sabit_baslangic), int(degisken_baslangic),
                                             int(sabit_kalinlik), int(kapi_bas - degisken_baslangic)))
            if kapi_son < degisken_bitis:
                parcalar.append(pygame.Rect(int(sabit_baslangic), int(kapi_son),
                                             int(sabit_kalinlik), int(degisken_bitis - kapi_son)))
            kapi_rect = pygame.Rect(int(sabit_baslangic), int(kapi_bas),
                                     int(sabit_kalinlik), int(kapi_genislik))
        else:
            if kapi_bas > degisken_baslangic:
                parcalar.append(pygame.Rect(int(degisken_baslangic), int(sabit_baslangic),
                                             int(kapi_bas - degisken_baslangic), int(sabit_kalinlik)))
            if kapi_son < degisken_bitis:
                parcalar.append(pygame.Rect(int(kapi_son), int(sabit_baslangic),
                                             int(degisken_bitis - kapi_son), int(sabit_kalinlik)))
            kapi_rect = pygame.Rect(int(kapi_bas), int(sabit_baslangic),
                                     int(kapi_genislik), int(sabit_kalinlik))
        return parcalar, kapi_rect

    def _harita_olustur(self):
        self.duvarlar = []
        self.kapilar = []
        self.odalar = []

        k = 40
        dk = 20
        oda_g = 280
        oda_y = 220
        kapi_duvar_kalinlik = 20
        koridor_g = 140
        kapi_h = 70

        sol_oda_x = k
        sol_kapi_duvar_x = sol_oda_x + oda_g
        koridor_x1 = sol_kapi_duvar_x + kapi_duvar_kalinlik
        koridor_x2 = koridor_x1 + koridor_g
        sag_kapi_duvar_x = koridor_x2
        sag_oda_x = sag_kapi_duvar_x + kapi_duvar_kalinlik

        self.dunya_genisligi = sag_oda_x + oda_g + k

        satir_sinirlari = []
        y = k
        for idx in range(3):
            satir_sinirlari.append((y, y + oda_y))
            y += oda_y
            if idx < 2:
                y += dk
        self.dunya_yuksekligi = y + k

        w = self.dunya_genisligi
        h = self.dunya_yuksekligi

        self.duvarlar.append(pygame.Rect(0, 0, w, k))
        self.duvarlar.append(pygame.Rect(0, h - k, w, k))
        self.duvarlar.append(pygame.Rect(0, 0, k, h))
        self.duvarlar.append(pygame.Rect(w - k, 0, k, h))

        kilit_durumlari = {
            "sol_oda1_kapi": False,
            "sol_oda2_kapi": True,
            "sol_oda3_kapi": False,
            "sag_oda1_kapi": False,
            "sag_oda2_kapi": True,
            "sag_oda3_kapi": True
        }

        for idx, (y_bas, y_son) in enumerate(satir_sinirlari):
            kapi_merkez = (y_bas + y_son) / 2
            oda_no = idx + 1

            sol_oda_rect = pygame.Rect(sol_oda_x, y_bas, oda_g, y_son - y_bas)
            parcalar, kapi_rect = self._kapili_duvar_olustur(
                sabit_baslangic=sol_kapi_duvar_x, sabit_kalinlik=kapi_duvar_kalinlik,
                degisken_baslangic=y_bas, degisken_bitis=y_son,
                kapi_merkez=kapi_merkez, kapi_genislik=kapi_h, dikey=True
            )
            kapi_id = f"sol_oda{oda_no}_kapi"
            self.duvarlar.extend(parcalar)
            self.kapilar.append({
                "id": kapi_id,
                "rect": kapi_rect,
                "kilitli": kilit_durumlari.get(kapi_id, True),
                "oda": f"sol_oda{oda_no}",
                "acik": False,
                "duvar_parcalari": parcalar[:]
            })
            self.odalar.append({"id": f"sol_oda{oda_no}", "rect": sol_oda_rect})

            sag_oda_rect = pygame.Rect(sag_oda_x, y_bas, oda_g, y_son - y_bas)
            parcalar2, kapi_rect2 = self._kapili_duvar_olustur(
                sabit_baslangic=sag_kapi_duvar_x, sabit_kalinlik=kapi_duvar_kalinlik,
                degisken_baslangic=y_bas, degisken_bitis=y_son,
                kapi_merkez=kapi_merkez, kapi_genislik=kapi_h, dikey=True
            )
            kapi_id2 = f"sag_oda{oda_no}_kapi"
            self.duvarlar.extend(parcalar2)
            self.kapilar.append({
                "id": kapi_id2,
                "rect": kapi_rect2,
                "kilitli": kilit_durumlari.get(kapi_id2, True),
                "oda": f"sag_oda{oda_no}",
                "acik": False,
                "duvar_parcalari": parcalar2[:]
            })
            self.odalar.append({"id": f"sag_oda{oda_no}", "rect": sag_oda_rect})

            if idx < len(satir_sinirlari) - 1:
                ara_y = y_son
                self.duvarlar.append(pygame.Rect(sol_oda_x, ara_y, oda_g, dk))
                self.duvarlar.append(pygame.Rect(sag_oda_x, ara_y, oda_g, dk))

        self.baslangic_oda_id = "sol_oda1"
    
    def _sembolleri_yerlestir(self):
        self.sembol_odalar = {
            "sol_oda1": "♦",
            "sol_oda2": "♥",
            "sag_oda1": "♠",
            "sag_oda2": "♣",
            "sol_oda3": "?"
        }
    
    # ----------------------------------------------------------------
    # KAPI AÇMA
    # ----------------------------------------------------------------
    def _kapi_ac(self, kapi):
        if kapi["acik"]:
            return
        kapi["acik"] = True
        kapi["kilitli"] = False
        if kapi["id"] == "sol_oda2_kapi":
            self.bulmaca_aktif = True
            self._bulmaca_baslat()
    
    # ----------------------------------------------------------------
    # BULMACA
    # ----------------------------------------------------------------
    def _bulmaca_baslat(self):
        self.bulmaca_kareleri = []
        self.bulmaca_cozuldu = False
        self.anahtar_bulmaca_zeminde = False
        self.anahtar_bulmaca_envanterde = False
        oda = next(o for o in self.odalar if o["id"] == "sol_oda2")
        rect = oda["rect"]
        kare_boyut = 40
        toplam_genislik = 5 * kare_boyut + 4 * 10
        baslangic_x = rect.centerx - toplam_genislik // 2
        baslangic_y = rect.centery - kare_boyut // 2 - 30
        for i in range(5):
            kare_rect = pygame.Rect(baslangic_x + i * (kare_boyut + 10), baslangic_y, kare_boyut, kare_boyut)
            durum = (i % 2 == 0)
            self.bulmaca_kareleri.append({"rect": kare_rect, "durum": durum})
    
    def _bulmaca_kare_bas(self, index):
        if self.bulmaca_cozuldu or not self.bulmaca_aktif:
            return
        for i in range(max(0, index-1), min(5, index+2)):
            self.bulmaca_kareleri[i]["durum"] = not self.bulmaca_kareleri[i]["durum"]
        if all(kare["durum"] for kare in self.bulmaca_kareleri):
            self.bulmaca_cozuldu = True
            self.bulmaca_aktif = False
            self.anahtar_bulmaca_zeminde = True
            oda = next(o for o in self.odalar if o["id"] == "sol_oda2")
            self.anahtar_bulmaca_x = oda["rect"].centerx
            self.anahtar_bulmaca_y = oda["rect"].y + 45
            self._ses_oynat(self.unlock_ses)
    
    # ----------------------------------------------------------------
    # SEMBOL PANELİ (Bölüm 1)
    # ----------------------------------------------------------------
    def _panel_ac(self):
        if not self.panel_aktif:
            self.panel_aktif = True
            self.girilen_sira = []
            self.panel_sembol_goster = 0
    
    def _panel_kapat(self):
        self.panel_aktif = False
    
    def _panel_sembol_ekle(self):
        if len(self.girilen_sira) < 4:
            self.girilen_sira.append(self.panel_semboller[self.panel_sembol_goster])
            if len(self.girilen_sira) == 4:
                if self.girilen_sira == self.dogru_sira:
                    self.panel_cozuldu = True
                    self.anahtar_panel_zeminde = True
                    oda = next(o for o in self.odalar if o["id"] == "sag_oda3")
                    self.anahtar_panel_x = oda["rect"].centerx
                    self.anahtar_panel_y = oda["rect"].centery - 60
                    self._ses_oynat(self.unlock_ses)
                    self._panel_kapat()
                else:
                    self.girilen_sira = []
                    self._ses_oynat(self.error_ses)
    
    def _panel_secimi_degistir(self, yon):
        self.panel_sembol_goster = (self.panel_sembol_goster + yon) % len(self.panel_semboller)
    
    # ----------------------------------------------------------------
    # KAMERA / IŞIK
    # ----------------------------------------------------------------
    def _kamera_sinirla(self, x, y):
        if self.dunya_genisligi <= self.ekran_genislik:
            x = -(self.ekran_genislik - self.dunya_genisligi) // 2
        else:
            x = max(0, min(x, self.dunya_genisligi - self.ekran_genislik))
        if self.dunya_yuksekligi <= self.ekran_yukseklik:
            y = -(self.ekran_yukseklik - self.dunya_yuksekligi) // 2
        else:
            y = max(0, min(y, self.dunya_yuksekligi - self.ekran_yukseklik))
        return x, y

    def _gorus_poligonu(self, merkez_x, merkez_y, yaricap, isik_kutusu):
        nokta_sayisi = 120
        engeller = [d for d in self.duvarlar if d.colliderect(isik_kutusu)]
        poligon = []
        for i in range(nokta_sayisi):
            aci = (2 * math.pi) * i / nokta_sayisi
            dx = math.cos(aci)
            dy = math.sin(aci)
            uzak_x = merkez_x + dx * yaricap
            uzak_y = merkez_y + dy * yaricap
            en_yakin = yaricap
            for engel in engeller:
                kesisim = engel.clipline(merkez_x, merkez_y, uzak_x, uzak_y)
                if kesisim:
                    (x1, y1), (x2, y2) = kesisim
                    for (kx, ky) in ((x1, y1), (x2, y2)):
                        mesafe = math.hypot(kx - merkez_x, ky - merkez_y)
                        if mesafe < en_yakin:
                            en_yakin = mesafe
            poligon.append((merkez_x + dx * en_yakin, merkez_y + dy * en_yakin))
        return poligon

    def _gorus_poligonu_labirent(self, merkez_x, merkez_y, yaricap, isik_kutusu):
        nokta_sayisi = 120
        duvar_boyut = 50
        engeller = []
        for (x, y) in self.labirent_duvarlar:
            rect = pygame.Rect(x * duvar_boyut + 100, y * duvar_boyut + 100, duvar_boyut, duvar_boyut)
            if rect.colliderect(isik_kutusu):
                engeller.append(rect)
        poligon = []
        for i in range(nokta_sayisi):
            aci = (2 * math.pi) * i / nokta_sayisi
            dx = math.cos(aci)
            dy = math.sin(aci)
            uzak_x = merkez_x + dx * yaricap
            uzak_y = merkez_y + dy * yaricap
            en_yakin = yaricap
            for engel in engeller:
                kesisim = engel.clipline(merkez_x, merkez_y, uzak_x, uzak_y)
                if kesisim:
                    (x1, y1), (x2, y2) = kesisim
                    for (kx, ky) in ((x1, y1), (x2, y2)):
                        mesafe = math.hypot(kx - merkez_x, ky - merkez_y)
                        if mesafe < en_yakin:
                            en_yakin = mesafe
            poligon.append((merkez_x + dx * en_yakin - self.kamera_x, merkez_y + dy * en_yakin - self.kamera_y))
        return poligon
    
    # ----------------------------------------------------------------
    # SPRITE YÜKLEME
    # ----------------------------------------------------------------
    def _load_sprites(self):
        animasyonlar = {}
        tipler = ["Idle", "Run", "Death"]
        yonler = ["Down", "Up", "Side"]
        base_path = os.path.join("Assets", "images", "lostsoul", "char")
        for tip in tipler:
            klasor = os.path.join(base_path, f"{tip}_Base")
            if not os.path.exists(klasor):
                continue
            for yon in yonler:
                dosya_adi = f"{tip}_{yon}-Sheet.png"
                tam_yol = os.path.join(klasor, dosya_adi)
                if not os.path.exists(tam_yol):
                    continue
                try:
                    sheet = pygame.image.load(tam_yol).convert_alpha()
                    genislik = sheet.get_width()
                    kare_sayisi = genislik // self.oyuncu_w
                    if kare_sayisi == 0:
                        kare_sayisi = 4
                    kareler = []
                    for i in range(kare_sayisi):
                        kare = sheet.subsurface((i * self.oyuncu_w, 0, self.oyuncu_w, self.oyuncu_h))
                        kareler.append(kare)
                    anahtar = f"{tip.lower()}_{yon.lower()}"
                    animasyonlar[anahtar] = kareler
                except Exception as e:
                    print(f"Sprite yüklenemedi: {tam_yol} - {e}")
        if not animasyonlar:
            return None
        return animasyonlar
    
    def _load_ground_texture(self):
        yol = os.path.join("Assets", "images", "lostsoul", "ground.png")
        if os.path.exists(yol):
            try:
                img = pygame.image.load(yol).convert_alpha()
                kare = img.subsurface((0, 0, 159, 159))
                return pygame.transform.scale(kare, (16, 16))
            except:
                pass
        return None
    
    def _load_beast_sprites(self):
        yol = os.path.join("Assets", "images", "lostsoul", "beast.png")
        if os.path.exists(yol):
            try:
                sheet = pygame.image.load(yol).convert_alpha()
                sprites = []
                for i in range(3):
                    sprite = sheet.subsurface((i * 143, 0, 143, 205))
                    sprite = pygame.transform.scale(sprite, (80, 80))
                    sprites.append(sprite)
                return sprites
            except:
                pass
        return None
    
    # ----------------------------------------------------------------
    # BAŞLANGIÇ YAZISI
    # ----------------------------------------------------------------
    def baslangic_yazisi_baslat(self):
        self.baslangic_yazisi_aktif = True
        self.baslangic_yazisi_baslangic = pygame.time.get_ticks()
        self.baslangic_yazisi_suresi = 5000
        self.baslangic_yazisi_alpha = 255
        self.baslangic_yazisi_goster = True
        self.baslangic_yazisi_siyah_arkaplan = True
    
    # ----------------------------------------------------------------
    # GLITCH
    # ----------------------------------------------------------------
    def _glitch_baslat(self):
        if self.glitch_aktif:
            return
        self.glitch_aktif = True
        self.glitch_baslangic = pygame.time.get_ticks()
        self._ses_oynat(self.glitch_ses)
        self._ses_oynat(self.error_ses)
        self._muzik_stop()
        if self.footsteps_ses:
            self.footsteps_ses.stop()
    
    # ----------------------------------------------------------------
    # OLAY YÖNETİMİ
    # ----------------------------------------------------------------
    def handle_event(self, event):
        if not self.running:
            return False
        
        # Bölüm 2 panel kodu aktifse (Yön Tuşu kontrolleri swap edildi)
        if self.panel_kod_aktif:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.panel_kod_aktif = False
                elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    self.panel_kod_indeks = (self.panel_kod_indeks - 1) % 5  # sola geç
                elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    self.panel_kod_indeks = (self.panel_kod_indeks + 1) % 5  # sağa geç
                elif event.key == pygame.K_w or event.key == pygame.K_UP:
                    self.panel_kod[self.panel_kod_indeks] = str((int(self.panel_kod[self.panel_kod_indeks]) + 1) % 10)  # sayıyı artır
                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    self.panel_kod[self.panel_kod_indeks] = str((int(self.panel_kod[self.panel_kod_indeks]) - 1) % 10)  # sayıyı azalt
                elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    self._panel_kod_isle()
            return False
        
        if self.pause_active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.pause_indeks = (self.pause_indeks - 1) % len(self.pause_secenekleri)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.pause_indeks = (self.pause_indeks + 1) % len(self.pause_secenekleri)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if self.pause_indeks == 0:
                        self.pause_active = False
                        self.oyun_active = True
                    elif self.pause_indeks == 1:
                        self.pause_active = False
                        self.ayarlar_active = True
                    elif self.pause_active == 2:
                        self.pause_active = False
                        self.oyun_active = False
                        self.menu_active = True
                        self._muzik_stop()
                        if self.footsteps_ses:
                            self.footsteps_ses.stop()
                        self.baslangic_yazisi_aktif = False
                elif event.key == pygame.K_ESCAPE:
                    self.pause_active = False
                    self.oyun_active = True
            return False
        
        if self.menu_active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.secili_indeks = (self.secili_indeks - 1) % len(self.menu_secenekleri)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.secili_indeks = (self.secili_indeks + 1) % len(self.menu_secenekleri)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if self.secili_indeks == 0:
                        self.menu_active = False
                        self.oyun_active = True
                        self.baslangic_yazisi_baslat()
                        self.oynat_ses()
                    elif self.secili_indeks == 1:
                        self.menu_active = False
                        self.ayarlar_active = True
                    elif self.secili_indeks == 2:
                        self.running = False
                        return True
            return False
        
        if self.ayarlar_active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                    self.ayarlar_active = False
                    if self.oyun_active:
                        self.pause_active = True
                    else:
                        self.menu_active = True
                    self._settings_kaydet()
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.ses_seviyesi = max(0, self.ses_seviyesi - 5)
                    self._ses_guncelle()
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.ses_seviyesi = min(100, self.ses_seviyesi + 5)
                    self._ses_guncelle()
            return False
        
        if self.oyun_active:
            if self.panel_aktif:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self._panel_kapat()
                    elif event.key == pygame.K_w or event.key == pygame.K_UP:
                        self._panel_secimi_degistir(-1)
                    elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        self._panel_secimi_degistir(1)
                    elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self._panel_sembol_ekle()
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.pause_active = True
                    if self.footsteps_ses:
                        self.footsteps_ses.stop()
                    self.hareket_ediyor = False
                if event.key == pygame.K_SPACE:
                    self._space_etkilesim()
                if self.baslangic_yazisi_aktif:
                    return False
            return False
        
        return False
    
    def _space_etkilesim(self):
        # Eğer labirent aktifse space'e basınca kazanma mesajını kapat
        if self.labirent_aktif and self.labirent_kazandi:
            self.running = False
            return
        
        # Bölüm 2: Panel etkileşimi (Eski canavar odasında panel açma)
        if self.bolum == 2 and not self.labirent_aktif and not self.panel_kod_aktif:
            oda_sag2 = next(o for o in self.odalar if o["id"] == "sag_oda2")
            if math.hypot(oda_sag2["rect"].centerx - self.oyuncu_rect.centerx,
                          oda_sag2["rect"].centery - self.oyuncu_rect.centery) < 80:
                self.panel_kod_aktif = True
                self.panel_kod = ["0", "0", "0", "0", "0"]
                self.panel_kod_indeks = 0
                return
        
        # Bölüm 1: normal etkileşim
        if self.bolum == 1:
            oda_sag3 = next(o for o in self.odalar if o["id"] == "sag_oda3")
            if self.oyuncu_rect.colliderect(oda_sag3["rect"]):
                for kapi in self.kapilar:
                    if kapi["id"] == "sag_oda3_kapi" and kapi["acik"]:
                        self._panel_ac()
                        return
            
            for kapi in self.kapilar:
                if kapi["acik"]:
                    continue
                kapi_merkez = kapi["rect"].center
                if math.hypot(kapi_merkez[0] - self.oyuncu_rect.centerx,
                              kapi_merkez[1] - self.oyuncu_rect.centery) < 80:
                    if kapi["id"] == "sol_oda2_kapi":
                        if self.anahtar1_toplandi:
                            self.anahtar1_toplandi = False
                            self._kapi_ac(kapi)
                            return
                        else:
                            if pygame.time.get_ticks() - self.son_locked_ses_zamani > 1000:
                                self._ses_oynat(self.locked_ses)
                                self.son_locked_ses_zamani = pygame.time.get_ticks()
                            return
                    elif kapi["id"] == "sag_oda3_kapi":
                        if self.anahtar_bulmaca_envanterde:
                            self.anahtar_bulmaca_envanterde = False
                            self._kapi_ac(kapi)
                            return
                        else:
                            if pygame.time.get_ticks() - self.son_locked_ses_zamani > 1000:
                                self._ses_oynat(self.locked_ses)
                                self.son_locked_ses_zamani = pygame.time.get_ticks()
                            return
                    elif kapi["id"] == "sag_oda2_kapi":
                        if self.anahtar_panel_envanterde:
                            self.anahtar_panel_envanterde = False
                            self._kapi_ac(kapi)
                            return
                        else:
                            if pygame.time.get_ticks() - self.son_locked_ses_zamani > 1000:
                                self._ses_oynat(self.locked_ses)
                                self.son_locked_ses_zamani = pygame.time.get_ticks()
                            return
                    else:
                        self._kapi_ac(kapi)
                        return
            
            if self.bulmaca_aktif and not self.bulmaca_cozuldu:
                for i, kare in enumerate(self.bulmaca_kareleri):
                    kare_merkez = kare["rect"].center
                    if math.hypot(kare_merkez[0] - self.oyuncu_rect.centerx,
                                  kare_merkez[1] - self.oyuncu_rect.centery) < 80:
                        self._bulmaca_kare_bas(i)
                        break
    
    # ----------------------------------------------------------------
    # UPDATE
    # ----------------------------------------------------------------
    def update(self):
        if self.pause_active or not self.oyun_active:
            return
        if self.panel_aktif:
            return
        if self.panel_kod_aktif:
            return
        
        # ODAK KONTROLÜ: Pencere aktif değilse klavye girdilerini engeller
        if not getattr(self, 'focused', True):
            self.hareket_ediyor = False
            if self.footsteps_ses:
                self.footsteps_ses.stop()
            return
        
        if self.glitch_aktif:
            if pygame.time.get_ticks() - self.glitch_baslangic > self.glitch_suresi:
                self.running = False
            return
        
        # --- LABİRENT MODU (Bölüm 2) ---
        if self.labirent_aktif:
            self._update_labirent()
            return
        
        # --- NORMAL HARİTA MODU (Bölüm 1 veya Bölüm 2 başlangıcı) ---
        # Beast çarpışma ve kovalama (Bölüm 1)
        if self.bolum == 1 and self.glitch_item_aktif and self.glitch_item_rect:
            oda_sag2 = next(o for o in self.odalar if o["id"] == "sag_oda2")
            
            # Eğer oyuncu sağ oda 2'ye adım atarsa canavar hızlıca kovalamaya başlar
            if self.oyuncu_rect.colliderect(oda_sag2["rect"]):
                dx = self.oyuncu_rect.centerx - self.glitch_item_rect.centerx
                dy = self.oyuncu_rect.centery - self.glitch_item_rect.centery
                dist = math.hypot(dx, dy)
                if dist > 0:
                    speed = 6.0  # Oyuncu hızı 4 olduğu için canavar 6 hızıyla hızlıca üzerine koşar
                    self.glitch_item_rect.x += int((dx / dist) * speed)
                    self.glitch_item_rect.y += int((dy / dist) * speed)

            if self.oyuncu_rect.colliderect(self.glitch_item_rect):
                self._glitch_baslat()
        
        # Başlangıç yazısı
        if self.baslangic_yazisi_aktif:
            gecen = pygame.time.get_ticks() - self.baslangic_yazisi_baslangic
            if gecen > self.baslangic_yazisi_suresi:
                self.baslangic_yazisi_goster = False
                self.baslangic_yazisi_aktif = False
                self.baslangic_yazisi_siyah_arkaplan = False
            elif gecen > self.baslangic_yazisi_suresi - 1500:
                oran = (gecen - (self.baslangic_yazisi_suresi - 1500)) / 1500
                self.baslangic_yazisi_alpha = int(255 * (1 - oran))
            else:
                self.baslangic_yazisi_alpha = 255
            return
        
        # Hareket
        tuslar = pygame.key.get_pressed()
        dx, dy = 0, 0
        if tuslar[pygame.K_w] or tuslar[pygame.K_UP]:
            dy = -self.oyuncu_hiz
            self.yon = "up"
        if tuslar[pygame.K_s] or tuslar[pygame.K_DOWN]:
            dy = self.oyuncu_hiz
            self.yon = "down"
        if tuslar[pygame.K_a] or tuslar[pygame.K_LEFT]:
            dx = -self.oyuncu_hiz
            self.yon = "left"
        if tuslar[pygame.K_d] or tuslar[pygame.K_RIGHT]:
            dx = self.oyuncu_hiz
            self.yon = "right"
        
        onceki_hareket = self.hareket_ediyor
        self.hareket_ediyor = (dx != 0 or dy != 0)

        if self.hareket_ediyor and not onceki_hareket:
            if self.footsteps_ses:
                self.footsteps_ses.set_volume(self.ses_seviyesi / 100)
                self.footsteps_ses.play(-1)
        elif not self.hareket_ediyor and onceki_hareket:
            if self.footsteps_ses:
                self.footsteps_ses.stop()
        
        engeller = self.duvarlar[:]
        for kapi in self.kapilar:
            if not kapi["acik"]:
                engeller.append(kapi["rect"])
        
        if dx != 0:
            self.oyuncu_rect.x += dx
            for engel in engeller:
                if self.oyuncu_rect.colliderect(engel):
                    if dx > 0:
                        self.oyuncu_rect.right = engel.left
                    elif dx < 0:
                        self.oyuncu_rect.left = engel.right
        
        if dy != 0:
            self.oyuncu_rect.y += dy
            for engel in engeller:
                if self.oyuncu_rect.colliderect(engel):
                    if dy > 0:
                        self.oyuncu_rect.bottom = engel.top
                    elif dy < 0:
                        self.oyuncu_rect.top = engel.bottom
        
        if self.hareket_ediyor:
            self.animasyon_sayaci += 1
            if self.animasyon_sayaci >= self.animasyon_hizi:
                self.animasyon_sayaci = 0
                self.mevcut_kare = (self.mevcut_kare + 1) % 4
        else:
            self.mevcut_kare = 0
            self.animasyon_sayaci = 0
        
        # Anahtar toplama
        if self.anahtar1_rect and not self.anahtar1_toplandi:
            if self.oyuncu_rect.colliderect(self.anahtar1_rect):
                self.anahtar1_toplandi = True
                self.anahtar1_rect = None
                self._ses_oynat(self.pickup_ses)
        
        if self.anahtar_bulmaca_zeminde and not self.anahtar_bulmaca_envanterde:
            anahtar_rect = pygame.Rect(self.anahtar_bulmaca_x - 8, self.anahtar_bulmaca_y - 8, 16, 16)
            if self.oyuncu_rect.colliderect(anahtar_rect):
                self.anahtar_bulmaca_zeminde = False
                self.anahtar_bulmaca_envanterde = True
                self._ses_oynat(self.pickup_ses)
        
        if self.anahtar_panel_zeminde and not self.anahtar_panel_envanterde:
            anahtar_rect = pygame.Rect(self.anahtar_panel_x - 8, self.anahtar_panel_y - 8, 16, 16)
            if self.oyuncu_rect.colliderect(anahtar_rect):
                self.anahtar_panel_zeminde = False
                self.anahtar_panel_envanterde = True
                self._ses_oynat(self.pickup_ses)
        
        # Kamera
        hedef_kamera_x = self.oyuncu_rect.centerx - (self.ekran_genislik // 2)
        hedef_kamera_y = self.oyuncu_rect.centery - (self.ekran_yukseklik // 2)
        self.kamera_x, self.kamera_y = self._kamera_sinirla(hedef_kamera_x, hedef_kamera_y)
    
    def _update_labirent(self):
        if self.labirent_kazandi:
            return
        
        # ODAK KONTROLÜ: Pencere aktif değilse klavye girdilerini engeller
        if not getattr(self, 'focused', True):
            self.hareket_ediyor = False
            if self.footsteps_ses:
                self.footsteps_ses.stop()
            return
        
        tuslar = pygame.key.get_pressed()
        dx, dy = 0, 0
        hiz = self.oyuncu_hiz
        if tuslar[pygame.K_w] or tuslar[pygame.K_UP]:
            dy = -hiz
            self.yon = "up"
        if tuslar[pygame.K_s] or tuslar[pygame.K_DOWN]:
            dy = hiz
            self.yon = "down"
        if tuslar[pygame.K_a] or tuslar[pygame.K_LEFT]:
            dx = -hiz
            self.yon = "left"
        if tuslar[pygame.K_d] or tuslar[pygame.K_RIGHT]:
            dx = hiz
            self.yon = "right"
        
        onceki_hareket = self.hareket_ediyor
        self.hareket_ediyor = (dx != 0 or dy != 0)
        if self.hareket_ediyor and not onceki_hareket:
            if self.footsteps_ses:
                self.footsteps_ses.set_volume(self.ses_seviyesi / 100)
                self.footsteps_ses.play(-1)
        elif not self.hareket_ediyor and onceki_hareket:
            if self.footsteps_ses:
                self.footsteps_ses.stop()
        
        if self.hareket_ediyor:
            self.animasyon_sayaci += 1
            if self.animasyon_sayaci >= self.animasyon_hizi:
                self.animasyon_sayaci = 0
                self.mevcut_kare = (self.mevcut_kare + 1) % 4
        else:
            self.mevcut_kare = 0
            self.animasyon_sayaci = 0
        
        duvar_boyut = 50
        self.oyuncu_rect.x += dx
        for (wx, wy) in self.labirent_duvarlar:
            duvar_rect = pygame.Rect(wx * duvar_boyut + 100, wy * duvar_boyut + 100, duvar_boyut, duvar_boyut)
            if self.oyuncu_rect.colliderect(duvar_rect):
                if dx > 0:
                    self.oyuncu_rect.right = duvar_rect.left
                elif dx < 0:
                    self.oyuncu_rect.left = duvar_rect.right
        
        self.oyuncu_rect.y += dy
        for (wx, wy) in self.labirent_duvarlar:
            duvar_rect = pygame.Rect(wx * duvar_boyut + 100, wy * duvar_boyut + 100, duvar_boyut, duvar_boyut)
            if self.oyuncu_rect.colliderect(duvar_rect):
                if dy > 0:
                    self.oyuncu_rect.bottom = duvar_rect.top
                elif dy < 0:
                    self.oyuncu_rect.top = duvar_rect.bottom
        
        oyuncu_x = (self.oyuncu_rect.centerx - 100) // duvar_boyut
        oyuncu_y = (self.oyuncu_rect.centery - 100) // duvar_boyut
        if self._labirent_cikis_kontrol(oyuncu_x, oyuncu_y):
            self.labirent_kazandi = True
            self._ses_oynat(self.unlock_ses)
        
        self._beast_labirent_hareket()
        
        bx, by = self.beast_labirent_pos
        beast_rect = pygame.Rect(bx * duvar_boyut + 100, by * duvar_boyut + 100, duvar_boyut, duvar_boyut)
        if self.oyuncu_rect.colliderect(beast_rect):
            # Dokunulduğunda sesleri çalar ve 1 hak azaltır
            self._ses_oynat(self.glitch_ses)
            self._ses_oynat(self.laugh_ses)
            
            self.hak_sayisi -= 1
            if self.hak_sayisi <= 0:
                self._glitch_baslat()  # Hak kalmadıysa glitch çöküşünü tetikler
            else:
                # Oyuncu başlangıç noktasına (ofsetli olarak), canavar labirentin en uzak üst köşesine (13, 1) ışınlanır
                self.oyuncu_rect.x = self.labirent_baslangic[0] * 50 + 125 - self.carpisma_w // 2
                self.oyuncu_rect.y = self.labirent_baslangic[1] * 50 + 125 - self.carpisma_h // 2
                self.beast_labirent_pos = (13, 1)
                self.beast_hareket_suresi = pygame.time.get_ticks()
        
        labirent_genislik = self.labirent_boyut * duvar_boyut + 200
        labirent_yukseklik = self.labirent_boyut * duvar_boyut + 200
        hedef_kamera_x = self.oyuncu_rect.centerx - (self.ekran_genislik // 2)
        hedef_kamera_y = self.oyuncu_rect.centery - (self.ekran_yukseklik // 2)
        self.kamera_x = max(0, min(hedef_kamera_x, labirent_genislik - self.ekran_genislik))
        self.kamera_y = max(0, min(hedef_kamera_y, labirent_yukseklik - self.ekran_yukseklik))
    
    # ----------------------------------------------------------------
    # DRAW
    # ----------------------------------------------------------------
    def draw(self, surface):
        if self.menu_active:
            self._draw_menu(surface)
        elif self.ayarlar_active:
            self._draw_ayarlar(surface)
        elif self.pause_active:
            self._draw_pause(surface)
        elif self.oyun_active:
            if self.labirent_aktif:
                self._draw_labirent(surface)
            else:
                self._draw_oyun(surface)
            if self.panel_kod_aktif:
                self._panel_kod_ciz(surface)
        if self.glitch_aktif:
            self._draw_glitch(surface)
    
    def _draw_labirent(self, surface):
        surface.fill(KARANLIK)
        duvar_boyut = 50
        for (x, y) in self.labirent_duvarlar:
            ekran_x = x * duvar_boyut + 100 - self.kamera_x
            ekran_y = y * duvar_boyut + 100 - self.kamera_y
            if -duvar_boyut < ekran_x < self.ekran_genislik + duvar_boyut and -duvar_boyut < ekran_y < self.ekran_yukseklik + duvar_boyut:
                pygame.draw.rect(surface, (60, 50, 50), (ekran_x, ekran_y, duvar_boyut, duvar_boyut))
                pygame.draw.rect(surface, (100, 80, 80), (ekran_x, ekran_y, duvar_boyut, duvar_boyut), 2)
        
        bx, by = self.beast_labirent_pos
        ekran_x = bx * duvar_boyut + 100 - self.kamera_x
        ekran_y = by * duvar_boyut + 100 - self.kamera_y
        if self.canavar_sprite and len(self.canavar_sprite) > 2:
            sprite_indeks = (pygame.time.get_ticks() // 300) % 3
            surface.blit(self.canavar_sprite[sprite_indeks], (ekran_x - 8, ekran_y - 8))
        else:
            pygame.draw.rect(surface, KIRMIZI, (ekran_x, ekran_y, duvar_boyut, duvar_boyut))
            pygame.draw.rect(surface, BEYAZ, (ekran_x, ekran_y, duvar_boyut, duvar_boyut), 2)
        
        cx, cy = self.labirent_cikis
        ekran_x = cx * duvar_boyut + 100 - self.kamera_x
        ekran_y = cy * duvar_boyut + 100 - self.kamera_y
        pygame.draw.rect(surface, YESIL, (ekran_x, ekran_y, duvar_boyut, duvar_boyut))
        pygame.draw.rect(surface, BEYAZ, (ekran_x, ekran_y, duvar_boyut, duvar_boyut), 3)
        yazi = self.buyuk_font.render("ÇIKIŞ", True, SIYAH)
        surface.blit(yazi, yazi.get_rect(center=(ekran_x + duvar_boyut//2, ekran_y + duvar_boyut//2)))
        
        kx, ky = self.oyuncu_rect.x - self.kamera_x, self.oyuncu_rect.y - self.kamera_y
        sprite_x = kx - (self.oyuncu_w - self.carpisma_w) // 2
        sprite_y = ky - (self.oyuncu_h - self.carpisma_h) // 2
        if self.sprite_animasyonlar:
            durum = "run" if self.hareket_ediyor else "idle"
            yon = self.yon
            if yon in ["left", "right"]:
                yon = "side"
            anahtar = f"{durum}_{yon}"
            kareler = self.sprite_animasyonlar.get(anahtar, [])
            if kareler:
                kare_indeksi = self.mevcut_kare % len(kareler)
                sprite = kareler[kare_indeksi]
                if self.yon == "left":
                    sprite = pygame.transform.flip(sprite, True, False)
                surface.blit(sprite, (sprite_x, sprite_y))
            else:
                self._ciz_dikdortgen_karakter(surface, sprite_x, sprite_y)
        else:
            self._ciz_dikdortgen_karakter(surface, sprite_x, sprite_y)
        
        # Hak Göstergesi HUD (Karanlık maske blit edilmeden hemen önce çizilir)
        hak_yazi = self.kucuk_font.render(f"HAK: {self.hak_sayisi}/3", True, KIRMIZI)
        surface.blit(hak_yazi, (self.ekran_genislik - 140, 20))

        karartma = pygame.Surface((self.ekran_genislik, self.ekran_yukseklik), pygame.SRCALPHA)
        karartma.fill((0, 0, 0, 255))
        merkez_x, merkez_y = self.oyuncu_rect.centerx, self.oyuncu_rect.centery
        isik_kutusu = pygame.Rect(merkez_x - self.isik_yaricap, merkez_y - self.isik_yaricap,
                                   self.isik_yaricap * 2, self.isik_yaricap * 2)
        poligon = self._gorus_poligonu_labirent(merkez_x, merkez_y, self.isik_yaricap, isik_kutusu)
        if len(poligon) >= 3:
            isik_yuzey = pygame.Surface((self.ekran_genislik, self.ekran_yukseklik), pygame.SRCALPHA)
            pygame.draw.polygon(isik_yuzey, (0, 0, 0, 255), poligon)
            karartma.blit(isik_yuzey, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
        surface.blit(karartma, (0, 0))
        
        if self.labirent_kazandi:
            mesaj = self.buyuk_font.render("KAZANDIN!", True, YESIL)
            surface.blit(mesaj, mesaj.get_rect(center=(self.ekran_genislik//2, self.ekran_yukseklik//2)))
            alt = self.kucuk_font.render("[SPACE] Menüye dön", True, BEYAZ)
            surface.blit(alt, alt.get_rect(center=(self.ekran_genislik//2, self.ekran_yukseklik//2 + 60)))
    
    # ----------------------------------------------------------------
    # DİĞER ÇİZİM METODLARI
    # ----------------------------------------------------------------
    def _draw_glitch(self, surface):
        w, h = surface.get_width(), surface.get_height()
        karartma = pygame.Surface((w, h), pygame.SRCALPHA)
        karartma.fill((0, 0, 0, 220))
        surface.blit(karartma, (0, 0))
        
        for _ in range(50):
            x = random.randint(0, w)
            y = random.randint(0, h)
            gen = random.randint(30, 300)
            pygame.draw.line(surface, (255, 0, 0), (x, y), (x + gen, y + random.randint(-20, 20)), random.randint(2, 6))
        
        for _ in range(25):
            x = random.randint(0, w-60)
            y = random.randint(0, h-30)
            renk = random.choice([(255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,0,255)])
            pygame.draw.rect(surface, renk, (x, y, random.randint(30, 120), random.randint(10, 40)))
        
        for _ in range(10):
            x = random.randint(0, w-200)
            y = random.randint(0, h-100)
            rect = pygame.Rect(x, y, random.randint(100, 300), random.randint(20, 80))
            surf = surface.subsurface(rect).copy()
            surf = pygame.transform.rotate(surf, random.choice([-10, 10, -20, 20]))
            surface.blit(surf, (x + random.randint(-30, 30), y + random.randint(-20, 20)))
        
        hata_metinleri = [
            "CRITICAL ERROR: Kayıp Ruh çöktü!",
            "MEMORY ACCESS VIOLATION at 0x7F8A3C",
            "SYSTEM CRASH IMMINENT - KERNEL PANIC",
            "GLITCH DETECTED IN MAIN LOOP",
            "CORRUPTED SAVE DATA DETECTED",
            "FATAL EXCEPTION: ACCESS_VIOLATION",
            "FILE NOT FOUND: lost_soul.exe",
            "RUNTIME ERROR: OUT OF BOUNDS"
        ]
        for i, metin in enumerate(hata_metinleri):
            yazi = self.glitch_font.render(metin, True, (255, 0, 0))
            yazi2 = self.glitch_font.render(metin, True, (0, 255, 0))
            yazi3 = self.glitch_font.render(metin, True, (0, 0, 255))
            x = 30 + random.randint(-10, 10)
            y_pos = 30 + i * 35 + random.randint(-5, 5)
            if random.random() > 0.3:
                surface.blit(yazi, (x, y_pos))
            else:
                surface.blit(yazi2, (x + 3, y_pos + 2))
                surface.blit(yazi3, (x - 3, y_pos - 2))
        
        for _ in range(5):
            yazi = self.buyuk_font.render("FATAL", True, (255, 0, 0))
            x = random.randint(0, w - yazi.get_width())
            y = random.randint(0, h - yazi.get_height())
            surface.blit(yazi, (x, y))
    
    def _draw_menu(self, surface):
        w, h = surface.get_width(), surface.get_height()
        surface.fill(KARANLIK)
        baslik = self.buyuk_font.render("KAYIP RUH", True, KIRMIZI)
        surface.blit(baslik, baslik.get_rect(center=(w//2, h//2 - 120)))
        for i, secenek in enumerate(self.menu_secenekleri):
            renk = KIRMIZI if i == self.secili_indeks else BEYAZ
            yazi = self.buyuk_font.render(secenek, True, renk) if i == self.secili_indeks else self.font.render(secenek, True, renk)
            surface.blit(yazi, yazi.get_rect(center=(w//2, h//2 + i * 80)))
        alt = self.kucuk_font.render("W/S ile gezin, SPACE ile seç", True, GRI)
        surface.blit(alt, alt.get_rect(center=(w//2, h - 60)))
    
    def _draw_ayarlar(self, surface):
        w, h = surface.get_width(), surface.get_height()
        surface.fill(KARANLIK)
        yazi = self.buyuk_font.render("AYARLAR", True, KIRMIZI)
        surface.blit(yazi, yazi.get_rect(center=(w//2, h//2 - 100)))
        ses_yazi = self.font.render(f"Ses Seviyesi: %{self.ses_seviyesi}", True, BEYAZ)
        surface.blit(ses_yazi, ses_yazi.get_rect(center=(w//2, h//2)))
        bar_x, bar_y = w//2 - 100, h//2 + 40
        pygame.draw.rect(surface, GRI, (bar_x, bar_y, 200, 10))
        pygame.draw.rect(surface, KIRMIZI, (bar_x, bar_y, int(200 * self.ses_seviyesi / 100), 10))
        kontrol = self.kucuk_font.render("A/D ile ayarla, SPACE ile geri", True, GRI)
        surface.blit(kontrol, kontrol.get_rect(center=(w//2, h//2 + 100)))
    
    def _draw_pause(self, surface):
        self._draw_oyun(surface, pause=True)
        w, h = surface.get_width(), surface.get_height()
        karartma = pygame.Surface((w, h), pygame.SRCALPHA)
        karartma.fill((0, 0, 0, 180))
        surface.blit(karartma, (0, 0))
        for i, secenek in enumerate(self.pause_secenekleri):
            renk = KIRMIZI if i == self.pause_indeks else BEYAZ
            yazi = self.buyuk_font.render(secenek, True, renk) if i == self.pause_indeks else self.font.render(secenek, True, renk)
            surface.blit(yazi, yazi.get_rect(center=(w//2, h//2 + i * 80 - 40)))
        alt = self.kucuk_font.render("W/S ile gezin, SPACE ile seç", True, GRI)
        surface.blit(alt, alt.get_rect(center=(w//2, h - 60)))
    
    def _draw_oyun(self, surface, pause=False):
        w, h = surface.get_width(), surface.get_height()
        self.ekran_genislik = w
        self.ekran_yukseklik = h
        
        surface.fill(KARANLIK)
        
        if self.zemin_dokusu and not self.baslangic_yazisi_siyah_arkaplan:
            tex_w, tex_h = 16, 16
            for y in range(0, self.dunya_yuksekligi, tex_h):
                for x in range(0, self.dunya_genisligi, tex_w):
                    ekran_x, ekran_y = x - self.kamera_x, y - self.kamera_y
                    if ekran_x > -16 and ekran_x < w + 16 and ekran_y > -16 and ekran_y < h + 16:
                        surface.blit(self.zemin_dokusu, (ekran_x, ekran_y))
        
        for duvar in self.duvarlar:
            ekran_x, ekran_y = duvar.x - self.kamera_x, duvar.y - self.kamera_y
            pygame.draw.rect(surface, (40, 30, 30), (ekran_x, ekran_y, duvar.width, duvar.height))
            pygame.draw.rect(surface, (100, 50, 50), (ekran_x, ekran_y, duvar.width, duvar.height), 2)
        
        for kapi in self.kapilar:
            if kapi["acik"]:
                continue
            rect = kapi["rect"]
            ekran_x, ekran_y = rect.x - self.kamera_x, rect.y - self.kamera_y
            pygame.draw.rect(surface, (70, 50, 30), (ekran_x, ekran_y, rect.width, rect.height))
            pygame.draw.rect(surface, (150, 110, 60), (ekran_x, ekran_y, rect.width, rect.height), 2)
            kol_x = ekran_x + rect.width - 8
            kol_y = ekran_y + rect.height//2
            pygame.draw.circle(surface, (180, 180, 180), (kol_x, kol_y), 4)
            if kapi["kilitli"]:
                pygame.draw.circle(surface, (210, 180, 40), (ekran_x + rect.width//2, ekran_y + rect.height//2), 5)
                pygame.draw.rect(surface, (210, 180, 40), (ekran_x + rect.width//2 - 4, ekran_y + rect.height//2 - 6, 8, 6))
                pygame.draw.rect(surface, (210, 180, 40), (ekran_x + rect.width//2 - 3, ekran_y + rect.height//2 - 10, 6, 4))
        
        if self.anahtar1_rect:
            ekran_x = self.anahtar1_rect.x - self.kamera_x
            ekran_y = self.anahtar1_rect.y - self.kamera_y
            pygame.draw.rect(surface, SARI, (ekran_x, ekran_y, 32, 32))
            pygame.draw.rect(surface, TURUNCU, (ekran_x, ekran_y, 32, 32), 2)
            key_text = self.kucuk_font.render("🔑", True, SIYAH)
            surface.blit(key_text, (ekran_x + 4, ekran_y + 4))
        
        if self.anahtar_bulmaca_zeminde:
            ekran_x = self.anahtar_bulmaca_x - self.kamera_x
            ekran_y = self.anahtar_bulmaca_y - self.kamera_y
            pygame.draw.circle(surface, SARI, (int(ekran_x), int(ekran_y)), 10)
            pygame.draw.circle(surface, TURUNCU, (int(ekran_x), int(ekran_y)), 10, 2)
        
        if self.anahtar_panel_zeminde:
            ekran_x = self.anahtar_panel_x - self.kamera_x
            ekran_y = self.anahtar_panel_y - self.kamera_y
            pygame.draw.circle(surface, SARI, (int(ekran_x), int(ekran_y)), 10)
            pygame.draw.circle(surface, TURUNCU, (int(ekran_x), int(ekran_y)), 10, 2)
        
        # Bölüm 2'de eski canavar odasına (sag_oda2) etkileşim paneli çizme
        if self.bolum == 2 and not self.labirent_aktif:
            oda_sag2 = next(o for o in self.odalar if o["id"] == "sag_oda2")
            panel_x = oda_sag2["rect"].centerx - 30
            panel_y = oda_sag2["rect"].centery - 20
            ekran_panel_x = panel_x - self.kamera_x
            ekran_panel_y = panel_y - self.kamera_y
            pygame.draw.rect(surface, GRI, (ekran_panel_x, ekran_panel_y, 60, 40))
            pygame.draw.rect(surface, BEYAZ, (ekran_panel_x, ekran_panel_y, 60, 40), 2)
            panel_yazi = self.kucuk_font.render("KOD", True, BEYAZ)
            surface.blit(panel_yazi, (ekran_panel_x + 10, ekran_panel_y + 10))
        
        if self.glitch_item_aktif and self.glitch_item_rect and self.bolum == 1:
            ekran_x = self.glitch_item_rect.x - self.kamera_x
            ekran_y = self.glitch_item_rect.y - self.kamera_y
            if self.canavar_sprite and len(self.canavar_sprite) > 2:
                surface.blit(self.canavar_sprite[2], (ekran_x, ekran_y))
            else:
                pygame.draw.rect(surface, KIRMIZI, (ekran_x, ekran_y, 80, 80))
                pygame.draw.rect(surface, BEYAZ, (ekran_x, ekran_y, 80, 80), 2)
                pygame.draw.circle(surface, BEYAZ, (ekran_x + 20, ekran_y + 25), 10)
                pygame.draw.circle(surface, BEYAZ, (ekran_x + 60, ekran_y + 25), 10)
                pygame.draw.circle(surface, SIYAH, (ekran_x + 22, ekran_y + 25), 5)
                pygame.draw.circle(surface, SIYAH, (ekran_x + 62, ekran_y + 25), 5)
                pygame.draw.arc(surface, BEYAZ, (ekran_x + 15, ekran_y + 35, 50, 25), 0, math.pi, 3)
                glitch_text = self.kucuk_font.render("!", True, KIRMIZI)
                surface.blit(glitch_text, (ekran_x + 35, ekran_y + 60))
        
        for oda_id, sembol in self.sembol_odalar.items():
            if self.bolum == 2:  # Bölüm 2'deyken sembolleri gizler
                continue
            if oda_id == "sol_oda2" and self.bulmaca_aktif:
                continue
            oda = next(o for o in self.odalar if o["id"] == oda_id)
            rect = oda["rect"]
            ekran_x = rect.centerx - self.kamera_x
            ekran_y = rect.centery - self.kamera_y
            yazi = self.font.render(sembol, True, BEYAZ)
            surface.blit(yazi, (ekran_x - 10, ekran_y - 10))
            if sembol in self.dogru_sira:
                sira_no = self.dogru_sira.index(sembol) + 1
                no_yazi = self.kucuk_font.render(str(sira_no), True, SARI)
                surface.blit(no_yazi, (ekran_x - 10, ekran_y - 35))
        
        if self.bulmaca_aktif and not self.bulmaca_cozuldu:
            for kare in self.bulmaca_kareleri:
                ekran_x, ekran_y = kare["rect"].x - self.kamera_x, kare["rect"].y - self.kamera_y
                renk = YESIL if kare["durum"] else KIRMIZI
                pygame.draw.rect(surface, renk, (ekran_x, ekran_y, kare["rect"].width, kare["rect"].height))
                pygame.draw.rect(surface, BEYAZ, (ekran_x, ekran_y, kare["rect"].width, kare["rect"].height), 2)
        
        oda_sag3 = next(o for o in self.odalar if o["id"] == "sag_oda3")
        for kapi in self.kapilar:
            if kapi["id"] == "sag_oda3_kapi" and kapi["acik"]:
                panel_x = oda_sag3["rect"].centerx - 30
                panel_y = oda_sag3["rect"].centery - 20
                ekran_panel_x = panel_x - self.kamera_x
                ekran_panel_y = panel_y - self.kamera_y
                pygame.draw.rect(surface, GRI, (ekran_panel_x, ekran_panel_y, 60, 40))
                pygame.draw.rect(surface, BEYAZ, (ekran_panel_x, ekran_panel_y, 60, 40), 2)
                soru = self.font.render("?", True, BEYAZ)
                surface.blit(soru, (ekran_panel_x + 22, ekran_panel_y + 6))
                break
        
        if not self.baslangic_yazisi_siyah_arkaplan:
            kx, ky = self.oyuncu_rect.x - self.kamera_x, self.oyuncu_rect.y - self.kamera_y
            sprite_x = kx - (self.oyuncu_w - self.carpisma_w) // 2
            sprite_y = ky - (self.oyuncu_h - self.carpisma_h) // 2
            if self.sprite_animasyonlar:
                durum = "run" if self.hareket_ediyor else "idle"
                yon = self.yon
                if yon in ["left", "right"]:
                    yon = "side"
                anahtar = f"{durum}_{yon}"
                kareler = self.sprite_animasyonlar.get(anahtar, [])
                if kareler:
                    kare_indeksi = self.mevcut_kare % len(kareler)
                    sprite = kareler[kare_indeksi]
                    if self.yon == "left":
                        sprite = pygame.transform.flip(sprite, True, False)
                    surface.blit(sprite, (sprite_x, sprite_y))
                else:
                    self._ciz_dikdortgen_karakter(surface, sprite_x, sprite_y)
            else:
                self._ciz_dikdortgen_karakter(surface, sprite_x, sprite_y)
        
        karartma = pygame.Surface((w, h), pygame.SRCALPHA)
        karartma.fill((0, 0, 0, 255))
        if not self.baslangic_yazisi_siyah_arkaplan:
            merkez_x, merkez_y = self.oyuncu_rect.centerx, self.oyuncu_rect.centery
            isik_kutusu = pygame.Rect(merkez_x - self.isik_yaricap, merkez_y - self.isik_yaricap,
                                       self.isik_yaricap * 2, self.isik_yaricap * 2)
            poligon = self._gorus_poligonu(merkez_x, merkez_y, self.isik_yaricap, isik_kutusu)
            poligon_ekran = [(px - self.kamera_x, py - self.kamera_y) for px, py in poligon]
            if len(poligon_ekran) >= 3:
                isik_yuzey = pygame.Surface((w, h), pygame.SRCALPHA)
                pygame.draw.polygon(isik_yuzey, (0, 0, 0, 255), poligon_ekran)
                karartma.blit(isik_yuzey, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
        surface.blit(karartma, (0, 0))
        
        if self.baslangic_yazisi_goster:
            yazi = self.baslik_font.render(self.baslangic_yazisi_metni, True, (200, 50, 50))
            yazi.set_alpha(self.baslangic_yazisi_alpha)
            surface.blit(yazi, yazi.get_rect(center=(w//2, h//2 - 50)))
            alt = self.kucuk_font.render("...", True, (150, 50, 50))
            alt.set_alpha(self.baslangic_yazisi_alpha)
            surface.blit(alt, alt.get_rect(center=(w//2, h//2 + 40)))
        
        if not pause:
            hud = self.kucuk_font.render(f"X:{self.oyuncu_rect.x} Y:{self.oyuncu_rect.y}", True, GRI)
            surface.blit(hud, (10, 10))
            etk = self.kucuk_font.render("SPACE: Etkileşim", True, GRI)
            surface.blit(etk, (w - 200, 10))
        
        if self.panel_aktif:
            self._draw_panel(surface)
    
    def _draw_panel(self, surface):
        w, h = surface.get_width(), surface.get_height()
        karartma = pygame.Surface((w, h), pygame.SRCALPHA)
        karartma.fill((0, 0, 0, 200))
        surface.blit(karartma, (0, 0))
        panel_w, panel_h = 400, 300
        panel_x = w//2 - panel_w//2
        panel_y = h//2 - panel_h//2
        pygame.draw.rect(surface, (30, 30, 30), (panel_x, panel_y, panel_w, panel_h))
        pygame.draw.rect(surface, BEYAZ, (panel_x, panel_y, panel_w, panel_h), 3)
        baslik = self.buyuk_font.render("Sembol Sırasını Gir", True, BEYAZ)
        surface.blit(baslik, baslik.get_rect(center=(w//2, panel_y + 40)))
        for i in range(4):
            x = panel_x + 50 + i * 80
            y = panel_y + 100
            pygame.draw.rect(surface, SIYAH, (x, y, 60, 60))
            pygame.draw.rect(surface, BEYAZ, (x, y, 60, 60), 2)
            if i < len(self.girilen_sira):
                yazi = self.buyuk_font.render(self.girilen_sira[i], True, SARI)
                surface.blit(yazi, yazi.get_rect(center=(x+30, y+30)))
            elif i == len(self.girilen_sira):
                yazi = self.buyuk_font.render(self.panel_semboller[self.panel_sembol_goster], True, YESIL)
                surface.blit(yazi, yazi.get_rect(center=(x+30, y+30)))
                pygame.draw.rect(surface, YESIL, (x, y, 60, 60), 4)
        kontrol = self.kucuk_font.render("W/S: Sembol değiştir  SPACE: Ekle  ESC: Çık", True, GRI)
        surface.blit(kontrol, kontrol.get_rect(center=(w//2, panel_y + panel_h - 30)))
        sira_str = "Sıra: " + " → ".join(self.girilen_sira) if self.girilen_sira else "Sıra: Boş"
        sira_yazi = self.kucuk_font.render(sira_str, True, BEYAZ)
        surface.blit(sira_yazi, (panel_x + 20, panel_y + 200))
    
    def _ciz_dikdortgen_karakter(self, surface, x, y):
        pygame.draw.rect(surface, BEYAZ, (x - 2, y - 2, self.oyuncu_w + 4, self.oyuncu_h + 4))
        pygame.draw.rect(surface, KIRMIZI, (x, y, self.oyuncu_w, self.oyuncu_h))
        pygame.draw.circle(surface, BEYAZ, (x + 12, y + 14), 6)
        pygame.draw.circle(surface, BEYAZ, (x + self.oyuncu_w - 12, y + 14), 6)
        pygame.draw.circle(surface, SIYAH, (x + 14, y + 14), 2)
        pygame.draw.circle(surface, SIYAH, (x + self.oyuncu_w - 10, y + 14), 2)
    
    # ----------------------------------------------------------------
    # RUN
    # ----------------------------------------------------------------
    def run(self):
        self.screen = pygame.display.set_mode((self.genislik, self.yukseklik))
        pygame.display.set_caption("Kayip Ruh")
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._settings_kaydet()
                    self.running = False
                self.handle_event(event)
            self.update()
            self.draw(self.screen)
            pygame.display.flip()
            clock.tick(60)
        pygame.quit()