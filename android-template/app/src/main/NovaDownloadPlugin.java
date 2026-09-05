package com.nova.lighting;

import android.content.ContentValues;
import android.content.Context;
import android.net.Uri;
import android.os.Build;
import android.os.Environment;
import android.provider.MediaStore;
import android.util.Base64;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;

/**
 * Plugin native kecil untuk nulis file langsung ke folder Downloads PUBLIK
 * (yang kelihatan di app File Manager / aplikasi Files bawaan HP), bukan ke
 * folder privat aplikasi.
 *
 * Kenapa ini perlu dibikin sendiri (bukan pakai @capacitor/filesystem saja):
 * plugin Filesystem resmi Capacitor TIDAK punya folder Downloads publik yang
 * konsisten di semua versi Android — Directory.Documents/ExternalStorage cuma
 * jalan sampai Android 10 (dan butuh requestLegacyExternalStorage), lalu
 * terkunci ke folder privat app mulai Android 11 ke atas (scoped storage).
 *
 * Solusi di sini pakai 2 jalur supaya konsisten dari Android 5 s/d Android 15+:
 *  - Android 10+ (API 29+): tulis lewat MediaStore.Downloads (cara resmi
 *    Google untuk scoped storage, gak butuh permission runtime apapun).
 *  - Android 9 ke bawah (API < 29): tulis langsung ke
 *    Environment.DIRECTORY_DOWNLOADS (butuh WRITE_EXTERNAL_STORAGE, yang
 *    sudah dideklarasikan dengan maxSdkVersion=29 di manifest).
 */
@CapacitorPlugin(name = "NovaDownload")
public class NovaDownloadPlugin extends Plugin {

    @PluginMethod
    public void saveToDownloads(PluginCall call) {
        String filename = call.getString("filename");
        String base64Data = call.getString("data");
        String mimeType = call.getString("mimeType", "application/octet-stream");

        if (filename == null || base64Data == null) {
            call.reject("filename dan data wajib diisi");
            return;
        }

        try {
            byte[] bytes = Base64.decode(base64Data, Base64.DEFAULT);
            String resultUri;

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                resultUri = saveViaMediaStore(filename, mimeType, bytes);
            } else {
                resultUri = saveViaLegacyPath(filename, bytes);
            }

            JSObject ret = new JSObject();
            ret.put("uri", resultUri);
            ret.put("filename", filename);
            call.resolve(ret);
        } catch (Exception e) {
            call.reject("Gagal menyimpan file: " + e.getMessage(), e);
        }
    }

    private String saveViaMediaStore(String filename, String mimeType, byte[] bytes) throws Exception {
        Context ctx = getContext();
        ContentValues values = new ContentValues();
        values.put(MediaStore.Downloads.DISPLAY_NAME, filename);
        values.put(MediaStore.Downloads.MIME_TYPE, mimeType);
        values.put(MediaStore.Downloads.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS);
        values.put(MediaStore.Downloads.IS_PENDING, 1);

        Uri collection = MediaStore.Downloads.EXTERNAL_CONTENT_URI;
        Uri item = ctx.getContentResolver().insert(collection, values);
        if (item == null) {
            throw new Exception("Tidak bisa membuat entri MediaStore");
        }

        try (OutputStream out = ctx.getContentResolver().openOutputStream(item)) {
            if (out == null) throw new Exception("Tidak bisa membuka output stream");
            out.write(bytes);
            out.flush();
        }

        values.clear();
        values.put(MediaStore.Downloads.IS_PENDING, 0);
        ctx.getContentResolver().update(item, values, null, null);

        return item.toString();
    }

    private String saveViaLegacyPath(String filename, byte[] bytes) throws Exception {
        File downloadsDir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS);
        if (!downloadsDir.exists()) {
            downloadsDir.mkdirs();
        }
        File outFile = new File(downloadsDir, filename);
        try (FileOutputStream fos = new FileOutputStream(outFile)) {
            fos.write(bytes);
            fos.flush();
        }

        // Kasih tahu Android Media Scanner supaya file langsung muncul di
        // app File Manager / Files tanpa perlu restart HP.
        android.content.Intent scanIntent = new android.content.Intent(android.content.Intent.ACTION_MEDIA_SCANNER_SCAN_FILE);
        scanIntent.setData(Uri.fromFile(outFile));
        getContext().sendBroadcast(scanIntent);

        return Uri.fromFile(outFile).toString();
    }
}
