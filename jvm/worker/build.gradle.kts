plugins {
    kotlin("jvm") version "1.8.22"
    application
}

group = "mc.editkit"
version = "1.0-SNAPSHOT"

repositories {
    mavenCentral()
}

dependencies {
    // Hephaistos - NBT + MCA (Anvil) library
    implementation("io.github.jglrxavpok.hephaistos:common:2.2.0")
    
    // JSON parsing
    implementation("org.json:json:20231013")
    
    // Logging
    implementation("org.slf4j:slf4j-simple:2.0.9")
}

kotlin {
    jvmToolchain(17)
}

application {
    mainClass.set("mc.editkit.worker.MainKt")
}

tasks.jar {
    manifest {
        attributes["Main-Class"] = "mc.editkit.worker.MainKt"
    }
    from(configurations.runtimeClasspath.get().map { 
        if (it.isDirectory) it else zipTree(it) 
    })
    duplicatesStrategy = DuplicatesStrategy.EXCLUDE
}
