# iOS App Store and Google Play release gates

The repository's CI debug APK is not a store release. Store submission must be performed by an authorized account owner using the official Apple and Google developer accounts.

## Android / Google Play

- Generate a dedicated upload keystore. Keep it outside the repository and back it up in a password manager/secrets vault.
- Configure `key.properties` locally (never commit it) and Android Gradle signing configuration in the generated native project.
- Set the production API base URL and unique release version/build number.
- Build an Android App Bundle (`.aab`) with release signing; verify signature, package ID, version code and install/update behavior.
- Test on physical devices across supported Android versions, screen sizes and network conditions.
- Complete Play Console app content: privacy policy URL, Data safety form, ads declaration, target audience/age rating, content rating, app access instructions, account deletion URL/process and AI-generated content disclosures.
- Provide reviewer credentials and a working demo path where required. Do not use real user data.
- Upload to internal testing first; complete pre-launch report and crash review before staged rollout.

## iOS / App Store

- Create the app identifier and distribution certificate/profile in the Apple Developer account.
- Configure signing in Xcode or CI using protected certificate and provisioning-profile secrets.
- Build and export a signed IPA with the production API URL and release version/build number.
- Test on physical iPhones and supported iOS versions, including login, account deletion, memory controls, generated media playback, permissions, network loss and background/foreground transitions.
- Complete App Store Connect privacy nutrition labels, age rating, content rights, AI-generated content disclosures, account deletion, support URL, privacy policy and review notes.
- Confirm all third-party SDK privacy manifests and required-reason API declarations are present in the final generated native project.
- Submit to TestFlight before App Review.

## ALAP-specific release policy

- Publish clear rules for fictional characters and user-generated content, reporting, blocking, moderation and appeals.
- Enforce age eligibility and prevent sexual content involving minors or age-ambiguous characters.
- Provide user-facing AI disclosure; do not represent generated characters as real humans.
- Make memory opt-in and provide inspection/deletion controls. Explain provider processing and retention.
- Disclose generated images and synthetic voices; do not support voice cloning or impersonation without a separately reviewed consent and rights process.
- Ensure account deletion also removes associated media objects, memories, conversations and queued jobs.
- Complete billing and restore-purchase flows before selling subscriptions or consumable credits.
- Obtain qualified legal review of privacy policy, terms, content policy, copyright/voice rights and regional obligations.

No store submission or approval is implied by this checklist. Store review decisions belong to Apple and Google.
