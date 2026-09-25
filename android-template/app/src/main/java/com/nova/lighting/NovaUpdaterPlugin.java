package com.nova.lighting;

import android.util.Log;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

import java.io.File;

/**
 * NovaUpdater — plugin native kecil untuk "hot update" konten web (index.html)
 * TANPA perlu rebuild/reinstall APK baru (web-to-app auto-update offline).
 *
 * Cara kerja: Capacitor Android sudah menyediakan mekanisme resmi untuk
 * mengganti folder yang disajikan sebagai root web (https://localhost/) saat
 * runtime, lewat Bridge.setServerBasePath(path) + Bridge.reload() — ini
 * persis mekanisme yang dipakai plugin "live update" komersial (mis. Capgo
 * capacitor-updater). Kedua method itu ada di com.getcapacitor.Bridge tapi
 * TIDAK diexpose otomatis ke JavaScript, jadi kita bungkus jadi plugin kecil
 * ini supaya bisa dipanggil dari window.Capacitor.Plugins.NovaUpdater.
 *
 * Alur dari sisi JS (lihat index.html, fungsi novaCheckForContentUpdate):
 *  1. JS download index.html versi terbaru (teks HTML biasa) dari GitHub.
 *  2. JS simpan teks itu lewat @capacitor/filesystem ke Directory.Data
 *     (folder ini = getFilesDir() di Android), path "nova_web/index.html".
 *  3. JS panggil NovaUpdater.applyUpdate({ path: 'nova_web' }).
 *  4. Plugin ini set base path WebView ke folder itu lalu reload —
 *     WebView langsung menyajikan index.html BARU, offline sejak saat itu.
 *
 * NovaUpdater.resetToBundled() mengembalikan ke versi bawaan APK (assets
 * "public/" yang dibundel saat build) — dipakai JS sebagai fallback
 * otomatis kalau versi hasil update ternyata gagal boot (app blank/error
 * terus tiap dibuka), lihat novaContentSafetyCheck() di index.html.
 */
@CapacitorPlugin(name = "NovaUpdater")
public class NovaUpdaterPlugin extends Plugin {

    @PluginMethod
    public void applyUpdate(PluginCall call) {
        final String relPath = call.getString("path");
        if (relPath == null || relPath.trim().isEmpty()) {
            call.reject("path kosong");
            return;
        }
        try {
            File dir = new File(getContext().getFilesDir(), relPath);
            File indexFile = new File(dir, "index.html");
            if (!dir.exists() || !indexFile.exists()) {
                call.reject("Folder/index.html tidak ditemukan: " + dir.getAbsolutePath());
                return;
            }
            final String absPath = dir.getAbsolutePath();
            getActivity().runOnUiThread(() -> {
                try {
                    getBridge().setServerBasePath(absPath);
                    JSObject ret = new JSObject();
                    ret.put("applied", true);
                    ret.put("path", absPath);
                    call.resolve(ret);
                    // Reload PALING TERAKHIR — setelah reload, context JS lama
                    // (termasuk promise call ini) langsung ditinggalkan karena
                    // WebView memuat ulang index.html dari folder baru.
                    getBridge().reload();
                } catch (Exception e) {
                    Log.e("NovaUpdater", "applyUpdate gagal", e);
                    call.reject("applyUpdate gagal: " + e.getMessage());
                }
            });
        } catch (Exception e) {
            call.reject("applyUpdate error: " + e.getMessage());
        }
    }

    @PluginMethod
    public void resetToBundled(PluginCall call) {
        try {
            getActivity().runOnUiThread(() -> {
                try {
                    // "public" adalah nilai khusus bawaan Capacitor yang berarti
                    // "kembali ke assets bawaan APK" (bukan nama folder biasa).
                    getBridge().setServerBasePath("public");
                    JSObject ret = new JSObject();
                    ret.put("applied", true);
                    call.resolve(ret);
                    getBridge().reload();
                } catch (Exception e) {
                    Log.e("NovaUpdater", "resetToBundled gagal", e);
                    call.reject("resetToBundled gagal: " + e.getMessage());
                }
            });
        } catch (Exception e) {
            call.reject("resetToBundled error: " + e.getMessage());
        }
    }

    @PluginMethod
    public void getServerBasePath(PluginCall call) {
        try {
            JSObject ret = new JSObject();
            ret.put("path", getBridge().getServerBasePath());
            call.resolve(ret);
        } catch (Exception e) {
            call.reject("getServerBasePath error: " + e.getMessage());
        }
    }
}
