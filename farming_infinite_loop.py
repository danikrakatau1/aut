python
import os
import sys
import time
import random
import string
import json
import re
from curl_cffi import requests as cr
sys.path.append(os.getcwd())
try:
    import muke
except ImportError:
    print("[error] muke.py tidak ditemukan di folder yang sama!")
    sys.exit(1)
CELANA_DOMAINS = ["celana-ar-store.my.id", "dini-faqih.my.id"]
def surel_celana_anyar():
    local = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    domain = random.choice(CELANA_DOMAINS)
    return f"{local}@{domain}"
def candak_kotak_celana(surel):
    try:
        r = cr.get(f"https://mail.celana-ar-store.my.id/api/inbox?address={surel}", timeout=15)
        data = r.json()
        return data.get("emails", [])
    except Exception as e:
        print(f"[celana] Error fetching inbox: {e}")
        return []
def antos_otp_celana(surel, timeout=150):
    print(f"[otp] Menunggu email OTP di {surel} ({timeout}s)...", flush=True)
    tenggat = time.time() + timeout
    while time.time() < tenggat:
        emails = candak_kotak_celana(surel)
        for m in emails:
            mail_id = m.get("id")
            try:
                r = cr.get(f"https://mail.celana-ar-store.my.id/api/read?address={surel}&id={mail_id}", timeout=15)
                detail = r.json()
                body = detail.get("body", "") + " " + detail.get("subject", "")
                for pola in (r'Confirmation code (\d{6})', r'Use code (\d{6})', r'\b(\d{6})\b', r'code is (\d{6})', r'kode (\d{6})'):
                    match = re.search(pola, body, re.IGNORECASE)
                    if match:
                        otp = match.group(1)
                        print(f"[otp] Kode OTP ditemukan: {otp}")
                        return otp
            except Exception:
                pass
        time.sleep(5)
    raise Exception("OTP timeout")
def run_farm_loop():
    print("=== FARMING SCRIPT STARTED ===", flush=True)
    main_email = input("Masukkan email akun utama: ").strip()
    if "@" not in main_email:
        print("Email tidak valid.")
        return
    reff_code = input("Masukkan kode referral (default FO3DHT): ").strip() or "FO3DHT"
    print(f"\n[farming] Main Account: {main_email} | Reff: {reff_code}", flush=True)
    cycles = 5
    for i in range(1, cycles + 1):
        print(f"\n==============================")
        print(f"       [CYCLE {i} / {cycles}]        ")
        print(f"==============================")
        try:
            api, csrf = muke.mimitian_alur()
            print(f"\n📩 Silakan cek inbox email utama ({main_email}) untuk kode OTP login.")
            token, _ = muke._asup_biasa(api, csrf, main_email)
            if not token:
                print(f"[farming] Gagal login akun utama {main_email}")
                break
            muke.jieun_sesi(api, token)
            print(f"[farming] Login sukses: {main_email}")
            print(f"[farming] Mengklaim kode referral {reff_code}...")
            res = muke.tebus_kode(api, reff_code)
            print(f"[farming] Redeem result: {res}")
            temp_email = surel_celana_anyar()
            print(f"[farming] Mengganti email utama ke temp email: {temp_email}")
            sesi, tokens = muke._ac_pastikeun_sesi(api, False)
            daptar_cp, _ = muke._ac_daptar_coba(sesi, tokens)
            daptar_surel = muke._ac_saring_surel(daptar_cp)
            heubeul = None
            for c in daptar_surel:
                if (c.get('email') or '').lower() == main_email.lower():
                    heubeul = c
                    break
            if not heubeul:
                print(f"[farming] Email utama tidak ditemukan di Accounts Center")
                continue
            id_alat = muke._ac_acak(20, 'abcdefghijklmnopqrstuvwxyz_')
            sae, pesen, normal = muke._ac_nambah(sesi, tokens, id_alat, temp_email)
            if not sae:
                print(f"[farming] Gagal tambah email baru: {pesen}")
                continue
            tujuan = normal or temp_email
            print(f"[farming] OTP dikirim ke temp email {tujuan} (via celana-ar-store), menunggu...")
            pin = antos_otp_celana(tujuan)
            sae, pesen = muke._ac_verifikasi(sesi, tokens, id_alat, tujuan, pin)
            if not sae:
                print(f"[farming] Verifikasi email baru gagal: {pesen}")
                continue
            print(f"[farming] Email baru terverifikasi!")
            sae, pesen = muke._ac_pupus(sesi, tokens, id_alat, heubeul['id'])
            if not sae:
                print(f"[farming] Gagal unbind email lama: {pesen}")
                continue
            print(f"[farming] ✅ Cycle {i} sukses! Email utama {main_email} sudah di-unbind dan siap dipakai ulang.")
        except Exception as e:
            print(f"[farming] Error in cycle {i}: {e}")
        if i < cycles:
            cooldown = random.randint(15, 25)
            print(f"\n⏳ Cooldown aktif: Menunggu {cooldown} detik sebelum cycle berikutnya...")
            time.sleep(cooldown)
if name == "main":
    run_farm_loop()
