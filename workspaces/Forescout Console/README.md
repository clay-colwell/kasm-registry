
# Forescout Console Kasm workspace

Add each Linux Forescout Console bundle to `console/` as `<version>.tar.gz`, for
example `8.5.5.tar.gz` or `9.1.6.tar.gz`. The archive must contain one top-level
folder named `Forescout Console`. Console archives use Git LFS because they can
exceed GitHub's normal 100 MB file limit.

On a matching push, GitHub Actions:

1. validates every archive and generates one registry workspace per version;
2. builds an amd64 image for each Kasm/base-image combination;
3. publishes one GHCR repository per Console version, using explicit Kasm tags
   such as `ghcr.io/clay-colwell/forescout-console-8.5.5:1.19.0-rolling-weekly`;
   and
4. commits the generated workspace metadata, which triggers the existing
   registry site deployment.

The same workflow checks the upstream rolling-weekly images every Monday at
03:00 America/New_York. It compares the current base manifest digest with the
digest recorded on the published image and skips unchanged combinations.
An archive-only push builds only the Console versions whose `.tar.gz` files
changed. Changes to shared image inputs rebuild every Console version.

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
