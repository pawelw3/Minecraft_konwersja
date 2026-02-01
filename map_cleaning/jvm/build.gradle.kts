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
