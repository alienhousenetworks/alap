import os
from pathlib import Path

project = Path("ios/Runner.xcodeproj/project.pbxproj")
if not project.exists():
    raise SystemExit("Run flutter create --platforms=ios before signing setup")
team = os.environ["IOS_TEAM_ID"]
bundle = os.environ["IOS_BUNDLE_ID"]
profile = os.environ["IOS_PROFILE_NAME"]
source = project.read_text()
source = source.replace(
    "PRODUCT_BUNDLE_IDENTIFIER = com.alienhousenetworks.alap;",
    f"PRODUCT_BUNDLE_IDENTIFIER = {bundle};",
)
source = source.replace('DEVELOPMENT_TEAM = "";', f"DEVELOPMENT_TEAM = {team};")
source = source.replace(
    "CODE_SIGN_STYLE = Automatic;",
    f'CODE_SIGN_STYLE = Manual; CODE_SIGN_IDENTITY = "Apple Distribution"; PROVISIONING_PROFILE_SPECIFIER = "{profile}";',
)
if f"PRODUCT_BUNDLE_IDENTIFIER = {bundle};" not in source:
    raise SystemExit("Could not set the requested iOS bundle identifier")
if f"PROVISIONING_PROFILE_SPECIFIER = \"{profile}\";" not in source:
    raise SystemExit("Could not set the provisioning profile")
project.write_text(source)

export = Path("ios/ExportOptions.plist")
export.write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>method</key><string>app-store-connect</string>
<key>teamID</key><string>{team}</string>
<key>signingStyle</key><string>manual</string>
<key>provisioningProfiles</key><dict><key>{bundle}</key><string>{profile}</string></dict>
<key>stripSwiftSymbols</key><true/>
</dict></plist>''')
