package com.nuvikshop;

import org.bukkit.Bukkit;
import org.bukkit.ChatColor;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.scheduler.BukkitRunnable;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

public class NuvikShop extends JavaPlugin {

    private String apiUrl;
    private String secretKey;
    private int checkInterval;
    private boolean isConnected = false;

    @Override
    public void onEnable() {
        saveDefaultConfig();
        loadConfig();
        
        log("&6╔════════════════════════════════════════╗");
        log("&6║  &f🛒 &bNuvikShop &f- Sistema de Pagos     &6║");
        log("&6╠════════════════════════════════════════╣");
        log("&6║  &7API: &f" + apiUrl);
        log("&6║  &7Intervalo: &f" + checkInterval + "s");
        log("&6╚════════════════════════════════════════╝");
        
        testConnection();
        startCommandChecker();
    }

    private void loadConfig() {
        apiUrl = getConfig().getString("api-url", "http://localhost:4242");
        secretKey = getConfig().getString("secret-key", "cambia-esta-clave");
        checkInterval = getConfig().getInt("check-interval-seconds", 10);
    }

    private void testConnection() {
        new BukkitRunnable() {
            @Override
            public void run() {
                try {
                    URL url = new URL(apiUrl + "/api/plugin/pending");
                    HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                    conn.setRequestMethod("GET");
                    conn.setRequestProperty("X-Plugin-Secret", secretKey);
                    conn.setConnectTimeout(5000);
                    conn.setReadTimeout(5000);

                    int responseCode = conn.getResponseCode();
                    conn.disconnect();
                    
                    if (responseCode == 200) {
                        isConnected = true;
                        log("&a✓ Conexión exitosa!");
                        log("&a✓ Listo para procesar compras.");
                    } else if (responseCode == 401) {
                        log("&c✗ Error de autenticación - verifica la secret-key");
                    }
                } catch (Exception e) {
                    log("&c✗ No se pudo conectar a: " + apiUrl);
                }
            }
        }.runTaskAsynchronously(this);
    }

    private void startCommandChecker() {
        new BukkitRunnable() {
            @Override
            public void run() {
                checkPendingCommands();
            }
        }.runTaskTimerAsynchronously(this, 20L * 5, 20L * checkInterval);
    }

    private void checkPendingCommands() {
        try {
            URL url = new URL(apiUrl + "/api/plugin/pending");
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("GET");
            conn.setRequestProperty("X-Plugin-Secret", secretKey);
            conn.setConnectTimeout(5000);
            conn.setReadTimeout(5000);

            if (conn.getResponseCode() == 200) {
                if (!isConnected) {
                    isConnected = true;
                    log("&a✓ Reconectado!");
                }
                
                BufferedReader reader = new BufferedReader(new InputStreamReader(conn.getInputStream()));
                StringBuilder response = new StringBuilder();
                String line;
                while ((line = reader.readLine()) != null) {
                    response.append(line);
                }
                reader.close();
                processResponse(response.toString());
            }
            conn.disconnect();
        } catch (Exception e) {
            if (isConnected) {
                log("&e⚠ Conexión perdida");
                isConnected = false;
            }
        }
    }

    private void processResponse(String jsonResponse) {
        try {
            JsonObject json = JsonParser.parseString(jsonResponse).getAsJsonObject();
            if (json.get("success").getAsBoolean()) {
                JsonArray commands = json.getAsJsonArray("commands");
                
                for (JsonElement element : commands) {
                    JsonObject cmd = element.getAsJsonObject();
                    String commandId = cmd.get("id").getAsString();
                    String command = cmd.get("command").getAsString();
                    String username = cmd.get("username").getAsString();
                    String productId = cmd.get("product_id").getAsString();
                    
                    log("&6╔═══════════════════════════════════════╗");
                    log("&6║  &a💰 &f&lNUEVA COMPRA!                   &6║");
                    log("&6║  &7Usuario: &b" + username);
                    log("&6║  &7Producto: &e" + productId);
                    log("&6╚═══════════════════════════════════════╝");
                    
                    NuvikShop plugin = this;
                    new BukkitRunnable() {
                        @Override
                        public void run() {
                            try {
                                Bukkit.dispatchCommand(Bukkit.getConsoleSender(), command);
                                log("&a✓ Comando ejecutado para &b" + username);
                                confirmCommandAsync(commandId);
                            } catch (Exception e) {
                                log("&c✗ Error: " + e.getMessage());
                            }
                        }
                    }.runTask(plugin);
                }
            }
        } catch (Exception e) {
            log("&c✗ Error JSON: " + e.getMessage());
        }
    }

    private void confirmCommandAsync(String commandId) {
        new BukkitRunnable() {
            @Override
            public void run() {
                try {
                    URL url = new URL(apiUrl + "/api/plugin/confirm");
                    HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                    conn.setRequestMethod("POST");
                    conn.setRequestProperty("X-Plugin-Secret", secretKey);
                    conn.setRequestProperty("Content-Type", "application/json");
                    conn.setDoOutput(true);

                    String jsonBody = "{\"command_id\": \"" + commandId + "\"}";
                    try (OutputStream os = conn.getOutputStream()) {
                        os.write(jsonBody.getBytes(StandardCharsets.UTF_8));
                    }
                    conn.getResponseCode();
                    conn.disconnect();
                } catch (Exception e) {}
            }
        }.runTaskAsynchronously(this);
    }
    
    private void log(String message) {
        Bukkit.getConsoleSender().sendMessage(ChatColor.translateAlternateColorCodes('&', "[NuvikShop] " + message));
    }

    @Override
    public void onDisable() {
        log("&c✗ NuvikShop deshabilitado");
    }
}
