pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
        maven { url = uri("https://jitpack.io") }
        // Solana Mobile SDK official Maven repository
        maven {
            url = uri("https://maven.solanamobile.com")
        }
    }
}

rootProject.name = "BillionsBounty"
include(":app")
