package mc.editkit.worker

import java.nio.file.Path
import kotlin.io.path.*

/**
 * Launcher serwera Minecraft z pre-flight validation
 * Sprawdza mapę przed uruchomieniem i blokuje start jeśli są błędy
 */
class ServerLauncher(
    private val serverDir: Path,
    private val javaPath: String = DEFAULT_JAVA_PATH,
    private val javaOpts: String = DEFAULT_JAVA_OPTS
) {
    data class LaunchConfig(
        val worldName: String,
        val port: Int = 25565,
        val onlineMode: Boolean = false,
        val enableCommandBlocks: Boolean = true,
        val gameMode: String = "1",  // Creative
        val allowFlight: Boolean = true,
        val spawnProtection: Int = 0
    )
    
    data class LaunchResult(
        val success: Boolean,
        val process: Process? = null,
        val message: String,
        val validationResult: WorldValidator.ValidationResult? = null
    )
    
    /**
     * Uruchom serwer z pre-flight validation
     */
    fun launch(config: LaunchConfig, skipValidation: Boolean = false): LaunchResult {
        val worldPath = serverDir.resolve(config.worldName)
        
        // 1. Sprawdź czy świat istnieje
        if (!worldPath.exists()) {
            return LaunchResult(
                success = false,
                message = "Świat nie istnieje: $worldPath"
            )
        }
        
        // 2. Pre-flight validation (jeśli są metadane)
        if (!skipValidation) {
            val metadata = EditMetadata.load(worldPath)
            if (metadata != null) {
                println("[Pre-flight] Znaleziono metadane edycji, rozpoczynam weryfikację...")
                println("[Pre-flight] Tool: ${metadata.toolName}")
                println("[Pre-flight] Opis: ${metadata.description}")
                println("[Pre-flight] Chunki do sprawdzenia: ${metadata.modifiedChunks.size}")
                println("[Pre-flight] Zmiany do zweryfikowania: ${metadata.expectedChanges.size}")
                
                val validator = WorldValidator(worldPath)
                val result = validator.validate(metadata)
                
                println()
                println(result.formatReport())
                
                if (!result.isValid) {
                    return LaunchResult(
                        success = false,
                        message = "WERYFIKACJA NIE POWIODŁA SIĘ! Serwer nie zostanie uruchomiony.",
                        validationResult = result
                    )
                }
                
                println("[Pre-flight] ✅ Weryfikacja pomyślna, kontynuuję uruchamianie serwera...")
                println()
            } else {
                println("[Pre-flight] Brak metadanych edycji, pomijam weryfikację")
            }
        }
        
        // 3. Przygotuj server.properties
        prepareServerProperties(config)
        
        // 4. Uruchom serwer
        return try {
            val serverJar = findServerJar()
                ?: return LaunchResult(
                    success = false,
                    message = "Nie znaleziono pliku serwera (forge-*-universal.jar)"
                )
            
            val pb = ProcessBuilder(
                javaPath,
                *javaOpts.split(" ").toTypedArray(),
                "-jar", serverJar.fileName.toString(),
                "nogui"
            )
            pb.directory(serverDir.toFile())
            pb.inheritIO()
            
            val process = pb.start()
            
            LaunchResult(
                success = true,
                process = process,
                message = "Serwer uruchomiony (PID: ${process.pid()})",
                validationResult = null
            )
            
        } catch (e: Exception) {
            LaunchResult(
                success = false,
                message = "Błąd uruchamiania serwera: ${e.message}"
            )
        }
    }
    
    /**
     * Uruchom serwer i czekaj na gotowość (Done)
     */
    fun launchAndWait(
        config: LaunchConfig,
        skipValidation: Boolean = false,
        timeoutSeconds: Int = 120
    ): LaunchResult {
        val result = launch(config, skipValidation)
        
        if (!result.success || result.process == null) {
            return result
        }
        
        println("Czekam na inicjalizację serwera (timeout: ${timeoutSeconds}s)...")
        
        val logFile = serverDir.resolve("logs/latest.log")
        val startTime = System.currentTimeMillis()
        
        while ((System.currentTimeMillis() - startTime) / 1000 < timeoutSeconds) {
            Thread.sleep(2000)
            
            // Sprawdź czy proces nadal działa
            if (!result.process.isAlive) {
                return LaunchResult(
                    success = false,
                    message = "Serwer nieoczekiwanie się zamknął"
                )
            }
            
            // Sprawdź logi
            if (logFile.exists()) {
                val content = logFile.readText()
                
                // Sukces
                if (content.contains("Done") && content.contains("For help")) {
                    val time = (System.currentTimeMillis() - startTime) / 1000
                    return LaunchResult(
                        success = true,
                        process = result.process,
                        message = "Serwer gotowy! (startup: ${time}s, PID: ${result.process.pid()})"
                    )
                }
                
                // Błąd portu
                if (content.contains("FAILED TO BIND TO PORT")) {
                    result.process.destroyForcibly()
                    return LaunchResult(
                        success = false,
                        message = "Port ${config.port} jest zajęty!"
                    )
                }
                
                // Crash
                if (content.contains("A fatal error has occurred")) {
                    result.process.destroyForcibly()
                    return LaunchResult(
                        success = false,
                        message = "Serwer crashował podczas startupu"
                    )
                }
            }
            
            print(".")
        }
        
        // Timeout
        result.process.destroyForcibly()
        return LaunchResult(
            success = false,
            message = "Timeout - serwer nie wystartował w ${timeoutSeconds}s"
        )
    }
    
    private fun prepareServerProperties(config: LaunchConfig) {
        val props = serverDir.resolve("server.properties")
        
        val content = buildString {
            appendLine("server-port=${config.port}")
            appendLine("online-mode=${config.onlineMode}")
            appendLine("level-name=${config.worldName}")
            appendLine("enable-command-block=${config.enableCommandBlocks}")
            appendLine("gamemode=${config.gameMode}")
            appendLine("allow-flight=${config.allowFlight}")
            appendLine("spawn-protection=${config.spawnProtection}")
            appendLine("max-players=10")
            appendLine("motd=EditKit Test Server")
        }
        
        props.writeText(content)
    }
    
    private fun findServerJar(): Path? {
        return serverDir.listDirectoryEntries("forge-*-universal.jar").firstOrNull()
            ?: serverDir.listDirectoryEntries("*.jar").firstOrNull { 
                it.fileName.toString().contains("forge") || 
                it.fileName.toString().contains("server") 
            }
    }
    
    companion object {
        const val DEFAULT_JAVA_PATH = "java"
        const val DEFAULT_JAVA_OPTS = "-Xms2G -Xmx4G -XX:+UseG1GC -Dfml.queryResult=confirm"
    }
}
