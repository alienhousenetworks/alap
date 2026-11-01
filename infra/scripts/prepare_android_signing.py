from pathlib import Path

gradle = Path("android/app/build.gradle.kts")
if not gradle.exists():
    raise SystemExit("Run flutter create --platforms=android before signing setup")
source = gradle.read_text()
marker = "    buildTypes {"
if marker not in source:
    raise SystemExit("Flutter Gradle buildTypes block not found")
signing = """    signingConfigs {
        create("release") {
            val props = java.util.Properties().apply { load(rootProject.file("key.properties").inputStream()) }
            keyAlias = props["keyAlias"] as String
            keyPassword = props["keyPassword"] as String
            storeFile = file("upload-keystore.jks")
            storePassword = props["storePassword"] as String
        }
    }
"""
if 'create("release")' not in source:
    source = source.replace(marker, signing + marker)
source = source.replace(
    'signingConfig = signingConfigs.getByName("debug")',
    'signingConfig = signingConfigs.getByName("release")',
)
if 'signingConfig = signingConfigs.getByName("release")' not in source:
    raise SystemExit("Release signing configuration was not applied")
gradle.write_text(source)
