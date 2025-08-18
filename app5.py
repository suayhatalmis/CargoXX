#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 18 08:15:36 2025

@author: suayhatalmis
"""

import streamlit as st 
import pandas as pd

# Sayfa yapılandırması
st.set_page_config(
    page_title="Kargo Fiyat Hesaplama",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern CSS stilleri
st.markdown("""
    <style>
    /* Ana tema ve renk paleti */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Ana başlık */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
    }
    
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        margin-bottom: 0.5rem;
    }
    
    .main-subtitle {
        font-size: 1.2rem;
        color: rgba(255,255,255,0.9);
        font-weight: 300;
    }
    
    /* Form kartı */
    .form-card {
        background: rgba(255,255,255,0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    /* Bölüm başlıkları */
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
    }
    
    /* Bilgi kutuları */
    .info-box {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* Kargo detay kutuları */
    .cargo-detail {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* Firma kartları */
    .firma-card {
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        color: white;
        box-shadow: 0px 8px 25px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .firma-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, rgba(255,255,255,0.1), rgba(255,255,255,0));
        pointer-events: none;
    }
    
    .firma-card:hover {
        transform: translateY(-5px);
        box-shadow: 0px 12px 35px rgba(0,0,0,0.25);
    }
    
    .firma-title {
        font-size: 1.4rem;
        font-weight: bold;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .price-detail {
        margin: 0.5rem 0;
        padding: 0.3rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.2);
    }
    
    .price-detail:last-child {
        border-bottom: none;
    }
    
    .genel-toplam {
        font-size: 1.8rem;
        font-weight: bold;
        margin-top: 1rem;
        padding: 1rem;
        background: rgba(255,255,255,0.2);
        border-radius: 10px;
        text-align: center;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    /* Buton stilleri */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    
    /* Selectbox ve input stilleri */
    .stSelectbox > div > div {
        background: white;
        border-radius: 10px;
        border: 2px solid #e1e5e9;
        transition: border-color 0.3s ease;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stNumberInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e1e5e9;
        transition: border-color 0.3s ease;
    }
    
    .stNumberInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Multiselect */
    .stMultiSelect > div {
        background: white;
        border-radius: 10px;
    }
    
    /* Responsive tasarım */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2rem;
        }
        
        .form-card {
            margin: 0.5rem;
            padding: 1rem;
        }
        
        .firma-card {
            margin-bottom: 1rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

# =========================
# VERİ OKUMA VE FONKSİYONLAR (DEĞİŞTİRİLMEDİ)
# =========================
ILMESAFE_DOSYA = "ilmesafe.xlsx"

df = pd.read_excel(ILMESAFE_DOSYA, header=None)
iller_sutun = df.iloc[1, 2:].astype(str).str.strip().str.upper().values
iller_satir = df.iloc[2:, 1].astype(str).str.strip().str.upper().values
mesafe_df = df.iloc[2:, 2:]
mesafe_df.index = iller_satir
mesafe_df.columns = iller_sutun
mesafe_df = mesafe_df.apply(pd.to_numeric, errors='coerce').fillna(0)

def mesafe_bul(kaynak: str, hedef: str):
    kaynak = str(kaynak).strip().upper()
    hedef  = str(hedef).strip().upper()
    try:
        return mesafe_df.loc[kaynak, hedef]
    except KeyError:
        return None

def hat_belirle(mesafe: float) -> str:  
    if mesafe < 1: 
        return "Şehiriçi"
    elif mesafe <= 200:
        return "Yakın Mesafe"
    elif mesafe <= 600:
        return "Kısa Mesafe"
    elif mesafe <= 1000:
        return "Orta Mesafe"
    else:
        return "Uzak Mesafe"

FIYAT_DOSYALAR = {
    "Yurtiçi Kargo": "yk_for_kg.xlsx",
    "Aras Kargo"   : "Aras_for_kg.xlsx",
    "DHLeCommerce" : "DHL E-COMMERCE.xlsx",
    "Sürat Kargo"  : "Sürat_for_kg.xlsx",
}

EK_HIZMET_DOSYALAR = {
    "Yurtiçi Kargo":{"Telefon":28.89,"SMS":12.45},
    "Sürat Kargo"   : {"Telefon":7.00,"SMS":3.50},
    "DHLeCommerce" : {"Telefon":18.00,"SMS":4.00},
    "Aras Kargo"  : {"SMS":1.00},
}

def oku_fiyat(dosya):
    dfp = pd.read_excel(dosya)
    dfp = dfp.dropna(axis=1, how="all").dropna(axis=0, how="all")
    dfp.columns = dfp.columns.astype(str).str.strip().str.lower()
    return dfp

def standard_bedel_bul(firma, hat_adi, kg_desi_deger, deger_turu_local):
    dfp = oku_fiyat(FIYAT_DOSYALAR[firma])
    hat_col = hat_adi.strip().lower()
    mask = (dfp["kg/desi"] == kg_desi_deger)
    price = float(dfp.loc[mask, hat_col].values[0])

    if deger_turu_local == "ağırlık":
        if firma == "Aras Kargo" and kg_desi_deger > 100:
            price += 5120
        elif firma == "Yurtiçi Kargo" and kg_desi_deger > 100:
            price += 3950
        elif firma == "Sürat Kargo" and kg_desi_deger > 100:
            price += 3500
        elif firma == "DHLeCommerce" and kg_desi_deger > 30:
            price += (kg_desi_deger - 30) * 74.99
    else:
        if firma == "DHLeCommerce" and kg_desi_deger > 50:
            ekstra_desi = kg_desi_deger - 50
            price += (ekstra_desi // 3) * 74.99

    return price

def vergileri_hesapla(firma, ara_toplam, deger_turu_local, kg_desi_deger):
    kdv = ara_toplam * 0.20
    posta = 0.0
    if firma != "Aras Kargo":
        if deger_turu_local == "ağırlık" and kg_desi_deger <= 30:
            posta = ara_toplam * 0.0235
        elif deger_turu_local == "desi" and kg_desi_deger <= 100:
            posta = ara_toplam * 0.0235
            
    kdv=(ara_toplam+posta)*0.20
    return kdv, posta

def ek_hizmet_bedelleri(firma, kg_desi_deger, ek_hizmetler):
    kalemler = {"aa": 0.0, "at": 0.0, "Telefon": 0.0, "SMS": 0.0}

    if not ek_hizmetler:
        return kalemler

    firma_clean = firma.strip().upper()

    dfp = oku_fiyat(FIYAT_DOSYALAR[firma])
    if any(h in ek_hizmetler for h in ["aa", "at"]):
        row = dfp.loc[dfp["kg/desi"] == kg_desi_deger].iloc[0]
        for h in ["aa", "at"]:
            if h in ek_hizmetler and h in row.index:
                try:
                    kalemler[h] = float(row[h]) if pd.notna(row[h]) else 0.0
                except:
                    kalemler[h] = 0.0

    for h in ["Telefon", "SMS"]:
        if h in ek_hizmetler:
            for key, value in EK_HIZMET_DOSYALAR.items():
                if key.strip().upper() == firma_clean:
                    kalemler[h] = float(value.get(h, 0.0))

    return kalemler

# =========================
# MODERN ARAYÜZ
# =========================

# Ana başlık
st.markdown("""
    <div class="main-header">
        <h1 class="main-title">📦 Kargo Fiyat Hesaplama</h1>
        <p class="main-subtitle">Türkiye'nin en hızlı kargo fiyat karşılaştırma platformu</p>
    </div>
""", unsafe_allow_html=True)

# Ana form kartı
with st.container():
    st.markdown('<div class="form-card">', unsafe_allow_html=True)
    
    # Mesafe bilgileri bölümü
    st.markdown('<h2 class="section-header">🗺️ Gönderi Rotası</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🚀 Nereden**")
        nereden = st.selectbox("Çıkış şehri seçin:", sorted(iller_satir), key="nereden")
        
    with col2:
        st.markdown("**🎯 Nereye**")
        nereye = st.selectbox("Varış şehri seçin:", sorted(iller_sutun), key="nereye")

    # Mesafe bilgisi
    mesafe = mesafe_bul(nereden, nereye)
    if mesafe:
        hat = hat_belirle(mesafe)
        st.markdown(f"""
            <div class="info-box">
                <h3>📏 Rota Bilgileri</h3>
                <p><strong>Mesafe:</strong> {mesafe} km</p>
                <p><strong>Hat Türü:</strong> {hat}</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.error("❌ Mesafe bulunamadı! Lütfen farklı şehirler seçin.")
        st.stop()

    # Kargo tipi bölümü
    st.markdown('<h2 class="section-header">📦 Kargo Detayları</h2>', unsafe_allow_html=True)
    
    kargo_tipi = st.selectbox(
        "Kargo tipini seçin:",
        ["Dosya", "Paket/Koli"],
        help="Dosya: Evrak, belge vb. | Paket/Koli: Fiziksel ürünler"
    )
    
    tasima_degeri = 0
    deger_turu = "ağırlık"
    
    # Paket/Koli detayları
    if kargo_tipi.lower() in ["paket/koli", "paket", "koli"]:
        st.markdown('<div class="cargo-detail">', unsafe_allow_html=True)
        
        kargo_sayisi = st.number_input(
            "📦 Kaç adet kargo göndereceksiniz?", 
            1, 5, 1,
            help="Maksimum 5 adet kargo hesaplanabilir"
        )
        
        toplam_desi = 0.0
        toplam_agirlik = 0.0
        
        # Her kargo için detaylar
        for i in range(int(kargo_sayisi)):
            with st.expander(f"📦 {i+1}. Kargo Detayları", expanded=(i==0)):
                col1, col2 = st.columns(2)
                with col1:
                    en = st.number_input(f"En (cm)", 0.0, step=1.0, key=f"en_{i}")
                    boy = st.number_input(f"Boy (cm)", 0.0, step=1.0, key=f"boy_{i}")
                with col2:
                    yukseklik = st.number_input(f"Yükseklik (cm)", 0.0, step=1.0, key=f"yukseklik_{i}")
                    agirlik = st.number_input(f"Ağırlık (kg)", 0.0, step=0.1, key=f"agirlik_{i}")
                
                if en > 0 and boy > 0 and yukseklik > 0:
                    desi = en * boy * yukseklik / 3000
                    st.success(f"✅ {i+1}. Kargo Desi: {desi:.2f}")
                    toplam_desi += desi
                    toplam_agirlik += agirlik
        
        if toplam_desi > 0 or toplam_agirlik > 0:
            tasima_degeri = int(max(toplam_desi, toplam_agirlik))
            deger_turu = "ağırlık" if toplam_agirlik >= toplam_desi else "desi"
            
            st.markdown(f"""
                <div class="info-box">
                    <h4>📊 Toplam Hesaplama</h4>
                    <p><strong>Toplam Desi:</strong> {toplam_desi:.2f}</p>
                    <p><strong>Toplam Ağırlık:</strong> {toplam_agirlik:.2f} kg</p>
                    <p><strong>Faturalama:</strong> {tasima_degeri} ({deger_turu})</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Dosya detayları
    elif kargo_tipi.lower() == "dosya":
        st.markdown('<div class="cargo-detail">', unsafe_allow_html=True)
        
        kargo_sayisi = st.number_input(
            "📄 Kaç adet dosya göndereceksiniz?", 
            1, 5, 1,
            help="Maksimum 5 adet dosya hesaplanabilir"
        )
        
        tasima_degeri = int(kargo_sayisi)
        deger_turu = "ağırlık"
        
        st.markdown(f"""
            <div class="info-box">
                <h4>📄 Dosya Bilgileri</h4>
                <p><strong>Adet:</strong> {kargo_sayisi} dosya</p>
                <p><strong>Faturalama:</strong> {tasima_degeri} kg</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Ek hizmetler bölümü
    st.markdown('<h2 class="section-header">⚡ Ek Hizmetler</h2>', unsafe_allow_html=True)
    
    ek_hizmetler = st.multiselect(
        "İstediğiniz ek hizmetleri seçin:",
        ["aa", "at", "Telefon", "SMS"],
        help="aa: Alıcı adreste arama, at: Alıcı telefonla arama, Telefon: Telefon bildirimi, SMS: SMS bildirimi"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

# Hesaplama butonu
st.markdown('<br>', unsafe_allow_html=True)
if st.button("💰 Fiyatları Hesapla", type="primary"):
    
    # Fiyat hesaplamaları
    standart_bedeller = {}
    for firma in FIYAT_DOSYALAR.keys():
        try:
            standart_bedeller[firma] = standard_bedel_bul(
                firma, hat, tasima_degeri, deger_turu
            )
        except Exception as e:
            st.warning(f"⚠️ {firma} fiyat hesaplanamadı: {e}")

    if standart_bedeller:
        st.markdown('<br><h2 style="text-align: center; color: white; font-size: 2.5rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">💰 Fiyat Karşılaştırması</h2>', unsafe_allow_html=True)
        
        # Firma renk temaları
        firma_renkleri = {
            "Yurtiçi Kargo": "linear-gradient(135deg, #1976D2, #1565C0)",
            "Aras Kargo": "linear-gradient(135deg, #D32F2F, #C62828)",
            "DHLeCommerce": "linear-gradient(135deg, #F9A825, #F57F17)",
            "Sürat Kargo": "linear-gradient(135deg, #1A237E, #0D47A1)"
        }
        
        # Firma ikonları
        firma_ikonlari = {
            "Yurtiçi Kargo": "🟦",
            "Aras Kargo": "🟥",
            "DHLeCommerce": "🟨",
            "Sürat Kargo": "🟦"
        }

        # Kutuları yan yana göstermek için sütunlar
        col1, col2 = st.columns(2)

        # Firma kutularını oluşturma
        for i, (firma, standart_bedel) in enumerate(standart_bedeller.items()):
            kalemler = ek_hizmet_bedelleri(firma, tasima_degeri, ek_hizmetler)
            ek_hizmet_toplam = sum(kalemler.values())
            ara_toplam = standart_bedel + ek_hizmet_toplam
            kdv, posta = vergileri_hesapla(firma, ara_toplam, deger_turu, tasima_degeri)
            genel_toplam = ara_toplam + posta + kdv

            renk = firma_renkleri.get(firma, "linear-gradient(135deg, #333, #555)")
            ikon = firma_ikonlari.get(firma, "📦")

            # Firma kartları tamamen Streamlit ile
            column = col1 if i % 2 == 0 else col2
            
            with column:
                # Her firma için tam genişlikte renkli container
                st.markdown(f"""
                <div style="background: {renk}; border-radius: 15px; padding: 20px; margin-bottom: 20px; 
                            box-shadow: 0 4px 15px rgba(0,0,0,0.2); width: 100%;">
                    <h3 style="color: white; margin: 0; font-size: 1.5rem; text-align: center;">
                        {ikon} {firma}
                    </h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Fiyat bilgileri beyaz arka plan ile - tam genişlik
                st.markdown("""
                <div style="background: white; border-radius: 10px; padding: 20px; margin-top: -10px; 
                            box-shadow: 0 2px 10px rgba(0,0,0,0.1); width: 100%; box-sizing: border-box;">
                """, unsafe_allow_html=True)
                
                st.markdown(f"**💼 Standart Bedel:** {standart_bedel:.2f} TL")
                
                if ek_hizmetler:
                    st.markdown("**🔧 Ek Hizmetler:**")
                    for h, v in kalemler.items():
                        if h in ek_hizmetler and v > 0:
                            st.markdown(f"• **{h.upper()}:** {v:.2f} TL")
                    st.markdown(f"**Toplam Ek Hizmet:** {ek_hizmet_toplam:.2f} TL")
                    st.divider()
                else:
                    st.markdown("**🔧** Ek hizmet yok")
                    st.divider()
                
                st.markdown(f"**📊 KDV (Posta Vergisi dahil):** {kdv:.2f} TL")
                
                # Toplam fiyat vurgusu - tam genişlik
                renk_parcalari = renk.replace('linear-gradient(135deg, ', '').replace(')', '').split(', ')
                st.markdown(f"""
                <div style="background: {renk}; color: white; padding: 15px; 
                            border-radius: 10px; text-align: center; margin-top: 15px; width: 100%;">
                    <h2 style="margin: 0; font-size: 1.8rem;">💰 {genel_toplam:.2f} TL</h2>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
        
    else:
        st.error("❌ Hiçbir firma için fiyat hesaplanamadı!")

# Footer
st.markdown("""
    <div style="text-align: center; margin-top: 3rem; color: rgba(255,255,255,0.7);">
        <p>📦 Kargo Fiyat Hesaplama Sistemi | Güncel fiyatlar için lütfen kargo firmalarını arayın</p>
    </div>
""", unsafe_allow_html=True)