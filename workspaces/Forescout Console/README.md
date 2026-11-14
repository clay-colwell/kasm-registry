
# Forescout Console Kasm workspace

Drop either of these into `workspaces/Forescout Console/console/` (the actual
folder name contains a space, not `%20`):

- A vendor installer with its original name, for example
  `Forescout-Console-setup-Linux-9.1.7-269.run`. Older names such as
  `CounterACT-Console-setup-Linux-8.5.6-126_Upgrade_from_8.3.0-233_upward.run`
  are also supported.
- A prepared `<version>.tar.gz`, for example `8.5.6.tar.gz`, containing one
  top-level folder named `Forescout Console`.

Keep **one source per Console version**. If both formats or multiple installer
builds exist for the same version, validation fails with a message to remove
one. Both formats use Git LFS because they exceed GitHub's normal file limit.
Install Git LFS before committing these files (`git lfs install`).

For `.run` inputs, the workflow runs the vendor installer with
`--mode unattended --unattendedmodeui none --prefix "/home/kasm-user/Forescout Console"`
in a disposable amd64 Debian container with networking disabled. No GUI or
manual repackaging is needed. It checks the installed version, launcher, and
bundled Java runtime, clears initial login preferences/fingerprints, and creates
an ignored `.prepared/<version>.tar.gz` for the existing Dockerfile. The original
installer is preserved; the temporary archive is not committed. Only use
trusted vendor installers, since conversion executes their code.

To convert an installer locally, including on macOS with Docker running:

```bash
python3 scripts/prepare_forescout_console.py \
  'workspaces/Forescout Console/console/Forescout-Console-setup-Linux-9.1.7-269.run'
```

The helper prints the output path. Use `--output /path/to/9.1.7.tar.gz` to create
a standalone archive elsewhere. It refuses to overwrite an existing output;
remove that generated file explicitly before rerunning. Prepared archives pass
through validation unchanged. For a manual Docker build, run this helper first
and pass `CONSOLE_ARCHIVE=.prepared/9.1.7.tar.gz` (or the original archive filename).
The Dockerfile consumes normalized archives; GitHub Actions performs conversion
automatically.

On a matching push, GitHub Actions:

1. discovers each source and validates selected build inputs and generates one registry workspace per version;
2. builds an amd64 image for each Kasm/base-image combination;
3. publishes one GHCR repository per Console version, using explicit Kasm tags
   such as `ghcr.io/clay-colwell/forescout-console-8.5.5:1.19.0-rolling-weekly`;
   and
4. commits the generated workspace metadata, which triggers the existing
   registry site deployment.

The same workflow checks the upstream rolling-weekly images every Monday at
07:00 UTC (03:00 EDT, or 02:00 EST after the winter clock change). It compares
the current base manifest digest with the digest recorded on the published
image and skips unchanged combinations.
A source-only push builds only the Console versions whose `.tar.gz` or `.run`
files changed. Changes to shared image inputs rebuild every Console version.
Workspace image sizes are estimates calculated from the Console archive's
uncompressed contents plus a calibrated per-Kasm image overhead; published
images are not downloaded again solely for size measurement.
Docker's `DISK USAGE` column includes both compressed content and unpacked
snapshot storage and should not be used directly as `uncompressed_size_mb`.

The repository must allow GitHub Actions to read/write repository contents and
packages. Make the GHCR package public if Kasm should pull it without registry
credentials; otherwise configure GHCR credentials in Kasm.

To regenerate metadata locally:

```bash
python3 scripts/generate_forescout_workspaces.py
```

After a Console updates itself from an Enterprise Manager, close the Console
and package the updated installation from inside the Kasm session with:

```bash
package-forescout-console
```

The utility cleans environment-specific and transient data, reads the updated
version, and creates `/home/kasm-user/Downloads/<version>.tar.gz` ready to add
to `console/`. Use a session without Persistent Profile whenever possible.

## Browser launches from Console and SSO

XFCE's Chromium helper and the Chromium desktop URL handlers use
`/usr/local/bin/kasm-open-browser`. This GUI-only launcher disconnects stdin,
stdout, and stderr from the caller. Some Console versions start `xdg-open`
through Java and close its process pipes before Chromium starts; the upstream
Chromium wrapper otherwise receives SIGPIPE, causing XFCE's misleading
“Failed to execute default Web Browser: Input/output error” dialog.

The standard `chromium` and `chromium-browser` commands retain their output for
terminal use. The XFCE helper keeps the `chromium` ID, so existing persistent
profiles using that helper benefit after their container image is updated.
Existing running sessions must be recreated from the updated image. Custom
per-user helper overrides may need to be reset to the Chromium helper.

For a regression check, copy `tests/browser_launch_smoke.py` into a fresh
running Kasm desktop and run it with Python 3 before opening Chromium. It
reproduces the closed-pipe launch and checks exact URL delivery using a
loopback HTTP server; no Enterprise Manager or SSO credentials are needed.

## Customizing Workspace for your Environment

To make it easier for users to use the Forescout Console in your environment, you may wish to utilize the File Mappings feature on the workspace config to update the Console launcher shortcut to autologin to your local Forescout Console instance, create a shortcut to the Web Dashboard, pre-load `local.properties` (to avoid the redundant JRE update check on login and set other preferences) and `login.fingerprint.properties` (to avoid the fingerprint prompt on initial login). 

To map these files, go to Kasm Admin > Workspaces > Workspaces > [The Forescout Console Workspace] > File Mapping > Add File Mapping. Use the following settings for each suggested file mapping below:

### forescout.desktop

This file is used to override the default Forescout Console desktop launcher shortcut with a custom one that autologins to your Forescout Console instance. This also updates the autolaunch of the Console on image creation.
- Enabled: `True`
- Type: `Text`
- Name: `forescout.desktop`
- Description: `Shortcut to open Console with credentials pre-filled`
- Destination Path: `/home/kasm-default-profile/Desktop/forescout.desktop`
- Executable: `True`
- Writable: `False`
- Contents *(Make sure to replace `USERNAME`, `PASSWORD`, and `EM_IP` with your actual credentials and Console IP address)*:
```
[Desktop Entry]
Version=1.0
Type=Application
Terminal=false
Exec=/home/kasm-user/Forescout\ Console/GuiManager/current/Forescout\ Console --user USERNAME --password PASSWORD --host EM_IP
Name=Console
Icon=/home/kasm-user/Forescout Console/GuiManager/current/etc/images/mainwindows/System_Icon_Big.png
Comment=
Path=
StartupNotify=false
```

### webdashboard.desktop

This file is used to create a shortcut on the desktop to go to the Forescout Web Dashboard.
- Enabled: `True`
- Type: `Text`
- Name: `webdashboard.desktop`
- Description: `Shortcut to Forescout Web Dashboard`
- Destination Path: `/home/kasm-default-profile/Desktop/webdashboard.desktop`
- Executable: `True`
- Writable: `False`
- Contents *(Make sure to replace `EM_IP` with your actual Console IP address)*:
```
[Desktop Entry]
Version=1.0
Name=Web Dashboard
GenericName=Web Browser
Comment=Access the Internet
Exec=chromium-browser "https://EM_IP"
Terminal=false
X-MultipleArgs=false
Type=Application
Icon=/home/kasm-user/Forescout Console/GuiManager/current/etc/images/toolbar/ConfigureOver.png
Categories=Network;WebBrowser;
MimeType=text/html;text/xml;application/xhtml+xml;x-scheme-handler/http;x-scheme-handler/https;
StartupWMClass=chromium-browser
StartupNotify=true
```

### local.properties

This file is used the console for various preferences, to avoid the redundant JRE update check on login. Pre-fill with your preferences so the console feels at home, even on a fresh Kasm instance.
- Enabled: `True`
- Type: `Text`
- Name: `local.properties`
- Description: `Customized local.properties`
- Destination Path: `/home/kasm-default-profile/Forescout Console/GuiManager/current/etc/local.properties`
- Executable: `False`
- Writable: `False`
- Contents *(It is recommend to copy the contents from a real console `local.properties` after you use it and login to a real instance and do whatever customizations you want -- policy column customizations, file browser paths, etc.)*:
```
#Site properties.
#Sun Jul 05 12:29:23 EDT 2026
login.parameters.type.method=STANDARD
screen.max=true
fs.java.version.home=jre1.8.0_442-3
```

### login.fingerprint.properties

This file is used by the console to remember what EMs it has already connected to. Pre-fill with your actualy EM Fingerprint to stop the "Do you trust this server" dialog when connecting to your EM with a fresh Kasm instance.
- Enabled: `True`
- Type: `Text`
- Name: `login.fingerprint.properties`
- Description: `Automatically trust Forescout instance Fingerprint`
- Destination Path: `/home/kasm-default-profile/Forescout Console/GuiManager/current/etc/login.fingerprint.properties`
- Executable: `False`
- Writable: `False`
- Contents *(Copy the contents from a real console `login.fingerprint.properties` after you login to your Forescout EM and save the Fingerprint)*:
```
#Sun Jul 05 12:29:01 EDT 2026
192.168.1.100=123ABC321
```
