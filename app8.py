#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 18 14:01:07 2025

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
    .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .main-header { text-align: center; padding: 2rem 0; margin-bottom: 2rem; }
    .main-title { font-size: 3rem; font-weight: 800; color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); margin-bottom: 0.5rem; }
    .main-subtitle { font-size: 1.2rem; color: rgba(255,255,255,0.9); font-weight: 300; }
    .form-card { background: rgba(255,255,255,0.95); backdrop-filter: blur(10px); border-radius: 20px; padding: 2rem; margin: 1rem 0; box-shadow: 0 8px 32px rgba(0,0,0,0.1); border: 1px solid rgba(255,255,255,0.2); }
    .section-header { font-size: 1.5rem; font-weight: 700; color: #2c3e50; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 3px solid #667eea; }
    .info-box { background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 1rem; border-radius: 15px; margin: 1rem 0; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
    .cargo-detail { background: #f8f9fa; border-radius: 12px; padding: 1.5rem; margin: 1rem 0; border-left: 4px solid #667eea; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

# =========================
# VERİ OKUMA VE FONKSİYONLAR
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
    if mesafe < 1: return "Şehiriçi"
    elif mesafe <= 200: return "Yakın Mesafe"
    elif mesafe <= 600: return "Kısa Mesafe"
    elif mesafe <= 1000: return "Orta Mesafe"
    else: return "Uzak Mesafe"

FIYAT_DOSYALAR = {
    "Yurtiçi Kargo": "yk_for_kg.xlsx",
    "Aras Kargo"   : "aras_for_kg.xlsx",
    "DHLeCommerce" : "dhl_ecommerce.xlsx",
    "Sürat Kargo"  : "surat_for_kg.xlsx",
}


EK_HIZMET_DOSYALAR = {
    "Yurtiçi Kargo":{"Telefon":28.89,"SMS":12.45},
    "Sürat Kargo"   : {"Telefon":7.00,"SMS":3.50},
    "DHLeCommerce" : {"Telefon":18.00,"SMS":4.00},
    "Aras Kargo"  : {"SMS":1.00},
}

def oku_fiyat(dosya):
    dfp = pd.read_excel(dosya, header=0)
    dfp = dfp.dropna(axis=1, how="all").dropna(axis=0, how="all")
    dfp.columns = dfp.columns.astype(str).str.strip().str.lower()
    if "kg/desi" in dfp.columns:
        dfp["kg/desi"] = pd.to_numeric(dfp["kg/desi"], errors="coerce")
    return dfp

def standard_bedel_bul(firma, hat_adi, kg_desi_deger, deger_turu_local):
    dfp = oku_fiyat(FIYAT_DOSYALAR[firma])
    hat_col = hat_adi.strip().lower()
    mask = (dfp["kg/desi"] == kg_desi_deger)
    price = float(dfp.loc[mask, hat_col].values[0])
    return price  

def agir_tasima_bedeli(firma, deger_turu_local, kg_desi_deger):
    bedel = 0.0
    if deger_turu_local == "ağırlık":
        if firma == "Aras Kargo" and kg_desi_deger > 100: bedel = 5120
        elif firma == "Yurtiçi Kargo" and kg_desi_deger > 100: bedel = 3950
        elif firma == "Sürat Kargo" and kg_desi_deger > 100: bedel = 3500
        elif firma == "DHLeCommerce" and kg_desi_deger > 30: bedel = (kg_desi_deger - 30) * 74.99
    else:
        if firma == "DHLeCommerce" and kg_desi_deger > 50:
            ekstra_desi = kg_desi_deger - 50
            bedel = (ekstra_desi // 3) * 74.99
    return bedel

def vergileri_hesapla(firma, ara_toplam, deger_turu_local, kg_desi_deger):
    posta = 0.0
    if firma != "Aras Kargo":
        if deger_turu_local == "ağırlık" and kg_desi_deger <= 30:
            posta = ara_toplam * 0.0235
        elif deger_turu_local == "desi" and kg_desi_deger <= 100:
            posta = ara_toplam * 0.0235
    kdv=(ara_toplam+posta)*0.20
    return kdv, posta

def ek_hizmet_bedelleri(firma, kg_desi_deger, ek_hizmetler):
    kalemler = {"Adresten Alım": 0.0, "Adresten Teslim": 0.0, "Telefon": 0.0, "SMS": 0.0}
    if not ek_hizmetler:
        return kalemler

    firma_clean = firma.strip().upper()
    dfp = oku_fiyat(FIYAT_DOSYALAR[firma])

    # 📌 Adresten Alım / Teslim kolonlarını kontrol et (küçük harfli!)
    if any(h in ek_hizmetler for h in ["Adresten Alım", "Adresten Teslim"]):
        row = dfp.loc[dfp["kg/desi"] == kg_desi_deger].iloc[0]
        for h in ["Adresten Alım", "Adresten Teslim"]:
            col_name = h.lower()  # <-- lowercase ile eşleştir
            if h in ek_hizmetler and col_name in row.index:
                kalemler[h] = float(row[col_name]) if pd.notna(row[col_name]) else 0.0

    # 📌 Telefon & SMS ücretleri sabit sözlükten
    for h in ["Telefon", "SMS"]:
        if h in ek_hizmetler:
            for key, value in EK_HIZMET_DOSYALAR.items():
                if key.strip().upper() == firma_clean:
                    kalemler[h] = float(value.get(h, 0.0))

    return kalemler


# =========================
# MODERN ARAYÜZ
# =========================
st.markdown("""
    <div class="main-header">
        <h1 class="main-title">📦 Kargo Fiyat Hesaplama</h1>
        <p class="main-subtitle">Türkiye'nin en hızlı kargo fiyat karşılaştırma platformu</p>
    </div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="form-card">', unsafe_allow_html=True)
    
    # Gönderi rotası
    st.markdown('<h2 class="section-header">🗺️ Gönderi Rotası</h2>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        nereden = st.selectbox("🚀 Nereden:", sorted(iller_satir), key="nereden")
    with col2:
        nereye = st.selectbox("🎯 Nereye:", sorted(iller_sutun), key="nereye")
    mesafe = mesafe_bul(nereden, nereye)
    if mesafe:
        hat = hat_belirle(mesafe)
        st.markdown(f"""
            <div class="info-box"><h3>📏 Rota Bilgileri</h3>
            <p><strong>Mesafe:</strong> {mesafe} km</p>
            <p><strong>Hat Türü:</strong> {hat}</p></div>
        """, unsafe_allow_html=True)
    else:
        st.error("❌ Mesafe bulunamadı!")
        st.stop()

    # Kargo detayları
    st.markdown('<h2 class="section-header">📦 Kargo Detayları</h2>', unsafe_allow_html=True)
    kargo_tipi = st.selectbox("Kargo tipini seçin:", ["Dosya", "Paket/Koli"])
    tasima_degeri, deger_turu = 0, "ağırlık"

    if kargo_tipi.lower() in ["paket/koli", "paket", "koli"]:
        kargo_sayisi = st.number_input("📦 Kaç adet kargo?", 1, 5, 1)
        toplam_desi, toplam_agirlik = 0, 0
        for i in range(int(kargo_sayisi)):
            with st.expander(f"📦 {i+1}. Kargo Detayları", expanded=(i==0)):
                en = st.number_input(f"En (cm)", 0.0, step=1.0, key=f"en_{i}")
                boy = st.number_input(f"Boy (cm)", 0.0, step=1.0, key=f"boy_{i}")
                yuk = st.number_input(f"Yükseklik (cm)", 0.0, step=1.0, key=f"yuk_{i}")
                ag = st.number_input(f"Ağırlık (kg)", 0.0, step=0.1, key=f"ag_{i}")
                if en>0 and boy>0 and yuk>0:
                    desi = en*boy*yuk/3000
                    toplam_desi += desi; toplam_agirlik += ag
        if toplam_desi>0 or toplam_agirlik>0:
            tasima_degeri = int(max(toplam_desi, toplam_agirlik))
            deger_turu = "ağırlık" if toplam_agirlik>=toplam_desi else "desi"

    elif kargo_tipi.lower()=="dosya":
        kargo_sayisi = st.number_input("📄 Kaç dosya?", 1, 5, 1)
        tasima_degeri = 0
        deger_turu = "ağırlık"

    # Ek hizmetler
    st.markdown('<h2 class="section-header">⚡ Ek Hizmetler</h2>', unsafe_allow_html=True)
    ek_hizmetler = st.multiselect("Ek hizmetler:", ["Adresten Alım", "Adresten Teslim", "Telefon", "SMS"])
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# HESAPLAMA VE SONUÇ
# =========================
if st.button("💰 Fiyatları Hesapla", type="primary"):
    standart_bedeller = {}
    for firma in FIYAT_DOSYALAR.keys():
        try:
            standart_bedeller[firma] = standard_bedel_bul(firma, hat, tasima_degeri, deger_turu)
        except Exception as e:
            st.warning(f"⚠️ {firma} fiyat hesaplanamadı: {e}")

    if standart_bedeller:
        st.markdown('<br><h2 style="text-align:center;color:white;font-size:2.5rem;">💰 Fiyat Karşılaştırması</h2>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        firma_renkleri = {
            "Yurtiçi Kargo":"linear-gradient(135deg, #1976D2, #1565C0)",
            "Aras Kargo":"linear-gradient(135deg, #D32F2F, #C62828)",
            "DHLeCommerce":"linear-gradient(135deg, #F9A825, #F57F17)",
            "Sürat Kargo":"linear-gradient(135deg, #1A237E, #0D47A1)"
        }
        for i,(firma,standart_bedel) in enumerate(standart_bedeller.items()):
            agir_bedel = agir_tasima_bedeli(firma, deger_turu, tasima_degeri)
            kalemler = ek_hizmet_bedelleri(firma, tasima_degeri, ek_hizmetler)
            ek_hizmet_toplam = sum(kalemler.values())
            ara_toplam = standart_bedel + ek_hizmet_toplam + agir_bedel
            kdv, posta = vergileri_hesapla(firma, ara_toplam, deger_turu, tasima_degeri)
            genel_toplam = ara_toplam + posta + kdv
            renk = firma_renkleri.get(firma,"linear-gradient(135deg,#333,#555)")
            column = col1 if i%2==0 else col2
            with column:
                st.markdown(f"<div style='background:{renk};padding:15px;border-radius:10px;color:white;text-align:center;'><h3>{firma}</h3></div>", unsafe_allow_html=True)
                st.markdown("<div style='background:white;padding:15px;border-radius:10px;'>", unsafe_allow_html=True)
                st.markdown(f"**💼 Standart Bedel:** {standart_bedel:.2f} TL")
                if agir_bedel>0: st.markdown(f"**⚖️ Ağır Taşıma Bedeli:** {agir_bedel:.2f} TL")
                if ek_hizmetler:
                    st.markdown("**🔧 Ek Hizmetler:**")
                    for h,v in kalemler.items():
                        if h in ek_hizmetler and v>0: st.markdown(f"• **{h.upper()}:** {v:.2f} TL")
                    st.markdown(f"**Toplam Ek Hizmet:** {ek_hizmet_toplam:.2f} TL")
                else: st.markdown("**🔧 Ek hizmet yok**")
                st.markdown(f"**📊 KDV (Posta dahil):** {kdv:.2f} TL")

                # ✅ Yurtiçi Kargo için %20 indirim
                if firma == "Yurtiçi Kargo":
                    indirimli_fiyat = genel_toplam * 0.8
                    st.markdown(f"""
                        <div style='background:{renk};color:white;padding:15px;border-radius:10px;text-align:center;'>
                            <h2>💰 <span style="text-decoration:line-through;opacity:0.7;">{genel_toplam:.2f} TL</span></h2>
                            <h2>✨ İndirimli Fiyat: {indirimli_fiyat:.2f} TL</h2>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='background:{renk};color:white;padding:15px;border-radius:10px;text-align:center;'><h2>💰 {genel_toplam:.2f} TL</h2></div>", unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error("❌ Hiçbir firma için fiyat hesaplanamadı!")

# Footer
st.markdown("<div style='text-align:center;margin-top:3rem;color:rgba(255,255,255,0.7);'>📦 Kargo Fiyat Hesaplama Sistemi</div>", unsafe_allow_html=True)
# =========================
# DİPNOTLAR / AÇIKLAMALAR
# =========================
st.markdown("""
    <div style="background:rgba(255,255,255,0.85); 
                padding:15px; 
                border-radius:12px; 
                margin-top:40px; 
                font-size:0.9rem; 
                color:#2c3e50; 
                box-shadow:0 2px 10px rgba(0,0,0,0.1);">
        <p>* KKTC gönderileri dikkate alınmamıştır.</p>
        <p>** DHL E-Commerce web sitesindeki gibi 20 kg’ın üstündeki ürünler için fiyat bilgisi sunmamaktadır.</p>
        <p>*** Mesafe bilgileri şehir merkezleri arasındaki mesafe (km) baz alınarak hesaplanmıştır.</p>
        <p>**** Girilen adrese bağlı olarak Adresten Alım ve Adrese Teslim hizmetleri kargo firmaları arasında değişkenlik gösterebilir.</p>
        <p>***** Firmaların web sitelerinden yayınlanan Ocak 2025 tarihli fiyatlar dikkate alınmıştır. KDV (%20) ve Evrensel Posta Hizmet Bedeli (%2.35) dahildir.</p>
        <p>****** Ödenecek net tutar şubede yapılacak olan ölçüm ve diğer kalemlere göre belirlenecektir.</p>
    </div>
""", unsafe_allow_html=True)
