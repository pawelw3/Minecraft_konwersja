plugins {
    kotlin("jvm") version "1.8.0"
    application
}

group = "mc.mapcleaner"
version = "1.0-SNAPSHOT"

repositories {
    mavenCentral()
}

dependencies {
    // Hephaistos - NBT + MCA (Anvil) library
    implementation("io.github.jglrxavpok.hephaistos:common:2.2.0")
    
    // Gson dla JSON
    implementation("com.google.code.gson:gson:2.10.1")
    
    // Kotlinx Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
    
    testImplementation(kotlin("test"))
}

kotlin {
    jvmToolchain(17)
}

application {
    mainClass.set("mapcleaner.MainKt")
}

tasks.jar {
    manifest {
        attributes["Main-Class"] = "mapcleaner.MainKt"
    }
    from(configurations.runtimeClasspath.get().map { 
        if (it.isDirectory) it else zipTree(it) 
    })
    duplicatesStrategy = DuplicatesStrategy.EXCLUDE
}

tasks.withType<JavaExec> {
    jvmArgs = listOf("-Xmx2G", "-XX:+UseG1GC")
}
