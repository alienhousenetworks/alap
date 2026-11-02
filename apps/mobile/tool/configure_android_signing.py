from pathlib import Path
import re
import sys

gradle = Path("android/app/build.gradle.kts")
if not gradle.exists():
    raise SystemExit("android/app/build.gradle.kts not found; run flutter create first")
source = gradle.read_text()
if 'create("release")' not in source:
    marker = "android {"
    if marker not in source:
        raise SystemExit("Unsupported Flutter Gradle template: android block not found")
    signing = '''
val keystoreProperties = java.util.Properties()
val keystorePropertiesFile = rootProject.file("key.properties")
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(java.io.FileInputStream(keystorePropertiesFile))
}

'''
    source = source.replace(marker, signing + marker, 1)
    source = source.replace(
        "android {",
        '''android {
    signingConfigs {
        create("release") {
            keyAlias = keystoreProperties["keyAlias"] as String
            keyPassword = keystoreProperties["keyPassword"] as String
            storeFile = file(keystoreProperties["storeFile"] as String)
            storePassword = keystoreProperties["storePassword"] as String
        }
    }
''',
        1,
    )
source, count = re.subn(
    r"signingConfig\s*=\s*signingConfigs\.getByName\(\"debug\"\)",
    'signingConfig = signingConfigs.getByName("release")',
    source,
)
if count == 0 and 'signingConfig = signingConfigs.getByName("release")' not in source:
    raise SystemExit("Could not safely replace generated debug signing configuration")
gradle.write_text(source)
print("Android release signing configured.")
