[Skip to main content](https://docs.kasm.com/docs/how-to/workspaces-sessions/container-workspace/customization/building-images#__docusaurus_skipToContent_fallback)

Version: 1.19.0 (latest)

On this page

The ability to create custom [workspaces](https://docs.kasm.com/docs/reference/glossary#workspace) is a powerful feature of the Kasm framework. Administrators may choose to maintain
and automatically deploy always up-to-date Images to the Kasm deployment with no user downtime. See
[Image Maintenance Process](https://docs.kasm.com/docs/how-to/workspaces-sessions/container-workspace/image-maintenance) for more details.

While the build process in this guide is the preferred method for creating robust, sustainable and highly automated images, administrators may also wish to experiment
with the [create-image-from-session](https://docs.kasm.com/docs/how-to/workspaces-sessions/sessions/#create-image-from-session) feature, which provides a quick and convenient way to capture the state of an active session if manual configuration is desired.

Administrators will create Docker Images that import from an existing [Default or Core Docker Image](https://docs.kasm.com/docs/how-to/workspaces-sessions/container-workspace/custom-images) published
by the Kasm Technologies team. The **Core** Docker images contain the minimal set of configurations that is necessary for the Docker images
to work within the platform.

The `kasmweb/core-ubuntu-jammy` image is the preferred core image and is based on Ubuntu 22.04 LTS. Generally speaking most programs that can be installed
on Ubuntu can be installed inside this image. The exception are programs that come delivered as containers themselves
such as [Snaps](https://snapcraft.io/) and some [FlatPaks](https://flatpak.org/).
Administrators will need working knowledge of Docker and scripting to add custom software and configurations to the
Docker images.

A Git repository with several example Dockerfiles that demonstrate how to build full desktop or single application
images is available on [GitHub](https://github.com/kasmtech/workspaces-images).

In this guide we will walk through the basic steps for creating a custom Image.
These steps can be conducted on the server with the Kasm [agent](https://docs.kasm.com/docs/reference/glossary#agent) installed.

Important

The Kasm team publishes new editions of the core image at every release cycle.
The Kasm team also maintains rolling updates for all published images, we would recommend basing custom images
against a rolling tag on a scheduled build so that the custom image will get regular program and security updates.
Be sure to build your image based on the appropriate tag for your deployed Kasm version for example kasmweb/core-ubuntu-jammy:1.19.0-rolling-daily or kasmweb/core-ubuntu-jammy:1.19.0-rolling-weekly

```bash
  FROM kasmweb/core-ubuntu-jammy:1.19.0
```

Note

It is also possible to base a custom Image on any of the default Images published.
See [Default Docker Images](https://docs.kasm.com/docs/how-to/workspaces-sessions/container-workspace/custom-images) for a list.

## Basic Build [​](https://docs.kasm.com/docs/how-to/workspaces-sessions/container-workspace/customization/building-images\#basic-build "Direct link to Basic Build")

tip

If performing a build directly on the Kasm Workspaces server or Agent, disable **Automatically Prune Images** for
the applicable Agent. See [Agent Settings](https://docs.kasm.com/docs/how-to/infra-autoscale/docker-agent) for more details.

1. Below is the baseline `Dockerfile` used to create a custom Kasm Image. There is a pre-defined sections where
customizations are to be added. The statements before and after this section should not be modified.
In this example a single customization is added: an file named **hello.txt** is created on the desktop.

Create a file named `Dockerfile` with the following contents.





```yml


     FROM kasmweb/core-ubuntu-jammy:1.19.0

     USER root



     ENV HOME /home/kasm-default-profile

     ENV STARTUPDIR /dockerstartup

     ENV INST_SCRIPTS $STARTUPDIR/install

     WORKDIR $HOME



     ######### Customize Container Here ###########





     RUN touch $HOME/Desktop/hello.txt





     ######### End Customizations ###########



     RUN chown 1000:0 $HOME

     RUN $STARTUPDIR/set_user_permission.sh $HOME



     ENV HOME /home/kasm-user

     WORKDIR $HOME

     RUN mkdir -p $HOME && chown -R 1000:0 $HOME



     USER 1000
```

2. Build the Image.





```bash
sudo docker build -t sublime-text:example -f Dockerfile .
```

3. Log into the Kasm UI as an administrator and register a new Workspace by selecting the **Workspaces** panel and clicking on **Add Workspace**
(It is also possible using the arrow menu to clone the configuration of an existing workspace)


tip

Kasm Workspaces does not assume the tag `latest` as many other docker tools do. This is because docker images from older versions my not be compatible with newer versions, and reduces the benefit of a `latest` tag.
The Kasm team recommends using a tag that reflects the version of the core image being used as a base. Kasm workspaces expects an explicit tag be specified in the Workspace configuration for _Docker Image_.

4. When finished editing details of the workspace click **Save** to create the new workspace.

![Register New Image](https://docs.kasm.com/assets/images/image_registration-e479f74d5fac0c63c7f0948b7a18d44f.webp)

Register New Image

5. From the Kasm Dashboard click Sublime Text Image.

![New Image Available](<Base64-Image-Removed>)

New Image Available

6. There will be a new pop up in the UI that has a **LAUNCH SESSION** button, click it to launch the Kasm session.

![Launch Session](https://docs.kasm.com/assets/images/launch_image-dc4c7fd300f084cc179a97be9a2f546f.webp)

Launch Session

7. A new session is created with the **hello.txt** file we created.

![Running the custom Image](https://docs.kasm.com/assets/images/hello-5a091e3bbf0fdf0724c0ac6079a6f494.png)

Running the custom Image

## Installing Software [​](https://docs.kasm.com/docs/how-to/workspaces-sessions/container-workspace/customization/building-images\#installing-software "Direct link to Installing Software")

1. Now it's time to do something more useful. We will update the `Dockerfile` to actually install Sublime Text.

Update the `Dockerfile` with the following contents.





```yml
     FROM kasmweb/core-ubuntu-jammy:1.19.0

     USER root



     ENV HOME /home/kasm-default-profile

     ENV STARTUPDIR /dockerstartup

     ENV INST_SCRIPTS $STARTUPDIR/install

     WORKDIR $HOME



     ######### Customize Container Here ###########



     RUN  wget -qO - https://download.sublimetext.com/sublimehq-pub.gpg | apt-key add - \\

         && apt-get update \\

         && apt-get install -y apt-transport-https \\

         && echo "deb https://download.sublimetext.com/ apt/stable/" |  tee /etc/apt/sources.list.d/sublime-text.list \\

         && apt-get update \\

         && apt-get install sublime-text \\

         && cp /usr/share/applications/sublime_text.desktop $HOME/Desktop/ \\

         && chmod +x $HOME/Desktop/sublime_text.desktop \\

         && chown 1000:1000 $HOME/Desktop/sublime_text.desktop





     ######### End Customizations ###########



     RUN chown 1000:0 $HOME

     RUN $STARTUPDIR/set_user_permission.sh $HOME



     ENV HOME /home/kasm-user

     WORKDIR $HOME

     RUN mkdir -p $HOME && chown -R 1000:0 $HOME



     USER 1000
```


Note

Creating desktop icons is a common need. This example highlights how applications , when installed often place a `.desktop` file in `/usr/share/applications`.
This file can often be copied without modification to the desktop `$HOME/Desktop/`. It is important to mark the file as executable and ensure the ownership
is changed to user and group `1000`

**Reference:**

- [https://www.sublimetext.com3/linux\_repositories.html](https://www.sublimetext.com/docs/3/linux_repositories.html)

2. Rebuild the Image and create a new session and verify Sublime Text is installed and an icon is present on the desktop.

![Sublime Text is Installed](https://docs.kasm.com/assets/images/sublime_1-ada433f6157c9de0cc1d886acbebf24e.png)

Sublime Text is Installed

## Custom Startup [​](https://docs.kasm.com/docs/how-to/workspaces-sessions/container-workspace/customization/building-images\#custom-startup "Direct link to Custom Startup")

1. Next we will utilize the `custom_startup.sh` interface point to launch Sublime text when the session starts.
Create the script and mark it executable. This script will run in the standard user (`1000`) context when the
session starts. Utilize the built-in command `/usr/bin/desktop_ready` to ensure Sublime Text starts after the
Kasm desktop environment.

Update the `Dockerfile` with the following contents.





```yml
     FROM kasmweb/core-ubuntu-jammy:1.19.0

     USER root



     ENV HOME /home/kasm-default-profile

     ENV STARTUPDIR /dockerstartup

     ENV INST_SCRIPTS $STARTUPDIR/install

     WORKDIR $HOME



     ######### Customize Container Here ###########



     RUN  wget -qO - https://download.sublimetext.com/sublimehq-pub.gpg | apt-key add - \\

         && apt-get update \\

         && apt-get install -y apt-transport-https \\

         && echo "deb https://download.sublimetext.com/ apt/stable/" |  tee /etc/apt/sources.list.d/sublime-text.list \\

         && apt-get update \\

         && apt-get install sublime-text \\

         && cp /usr/share/applications/sublime_text.desktop $HOME/Desktop/ \\

         && chmod +x $HOME/Desktop/sublime_text.desktop \\

         && chown 1000:1000 $HOME/Desktop/sublime_text.desktop



     RUN echo "/usr/bin/desktop_ready && /opt/sublime_text/sublime_text &" > $STARTUPDIR/custom_startup.sh \\

     && chmod +x $STARTUPDIR/custom_startup.sh





     ######### End Customizations ###########



     RUN chown 1000:0 $HOME

     RUN $STARTUPDIR/set_user_permission.sh $HOME



     ENV HOME /home/kasm-user

     WORKDIR $HOME

     RUN mkdir -p $HOME && chown -R 1000:0 $HOME



     USER 1000
```

2. Rebuild the Image and create a new session. Sublime Text should start automatically.


![Sublime Text Started Automatically](https://docs.kasm.com/assets/images/sublime_2-d962f94245320fd42821e1eab783b527.png)

Sublime Text Started Automatically

## Desktop Background [​](https://docs.kasm.com/docs/how-to/workspaces-sessions/container-workspace/customization/building-images\#desktop-background "Direct link to Desktop Background")

1. The background can be changed by overwriting the `/usr/share/backgrounds/bg_default.png` file.
Update the `Dockerfile` with the following contents.





```yml
     FROM kasmweb/core-ubuntu-jammy:1.19.0

     USER root



     ENV HOME /home/kasm-default-profile

     ENV STARTUPDIR /dockerstartup

     ENV INST_SCRIPTS $STARTUPDIR/install

     WORKDIR $HOME



     ######### Customize Container Here ###########



     RUN  wget -qO - https://download.sublimetext.com/sublimehq-pub.gpg | apt-key add - \\

         && apt-get update \\

         && apt-get install -y apt-transport-https \\

         && echo "deb https://download.sublimetext.com/ apt/stable/" |  tee /etc/apt/sources.list.d/sublime-text.list \\

         && apt-get update \\

         && apt-get install sublime-text \\

         && cp /usr/share/applications/sublime_text.desktop $HOME/Desktop/ \\

         && chmod +x $HOME/Desktop/sublime_text.desktop \\

         && chown 1000:1000 $HOME/Desktop/sublime_text.desktop



     RUN echo "/usr/bin/desktop_ready && /opt/sublime_text/sublime_text &" > $STARTUPDIR/custom_startup.sh \\

     && chmod +x $STARTUPDIR/custom_startup.sh



     RUN wget https://cdn.hipwallpaper.com/i/92/9/0Ts6mr.png -O /usr/share/backgrounds/bg_default.png



     ######### End Customizations ###########



     RUN chown 1000:0 $HOME

     RUN $STARTUPDIR/set_user_permission.sh $HOME



     ENV HOME /home/kasm-user

     WORKDIR $HOME

     RUN mkdir -p $HOME && chown -R 1000:0 $HOME



     USER 1000
```

2. Rebuild the image and create a new session. Sublime Text should start automatically.


![Custom Desktop Background](https://docs.kasm.com/assets/images/background-5aede86dc724201aca6ab6cd5d3d4879.png)

Custom Desktop Background

## Single App Workspace [​](https://docs.kasm.com/docs/how-to/workspaces-sessions/container-workspace/customization/building-images\#single-app-workspace "Direct link to Single App Workspace")

You can also configure a container-based workspace to launch in single-application mode using XFCE. When a Single App workspace is launched, it opens a specific application (for example, Firefox) automatically on session start and only that app is usable. The traditional desktop interface is disabled, preventing users from interacting with panels, menus, or launching additional applications. This is made possible with some XFCE configurations.

We already have some popular applications available as Single App Workspaces in our [official Workspaces registry](https://registry.kasmweb.com/1.1/). Some examples include: Firefox, Chrome, Brave, Slack, Telegram, Zoom, etc.

1. Start by writing a Custom Dockerfile for your Single App Workspace. We recommend you use the `kasmweb/core-ubuntu-jammy` image as the base image when creating a Single App workspace. If you use a different image, you would have to manually load the image with the Single App XFCE config files available on our [Github repo](https://github.com/kasmtech/workspaces-core-images/tree/develop/src/ubuntu/xfce/.config/xfce4/xfconf/single-application-xfce-perchannel-xml)

```yml
  FROM kasmweb/core-ubuntu-jammy:1.19.0-rolling-weekly

  USER root

  ENV HOME /home/kasm-default-profile

  ENV STARTUPDIR /dockerstartup

  ENV INST_SCRIPTS $STARTUPDIR/install

  WORKDIR $HOME

  ######### Customize Container Here ###########

  ######### End Customizations ###########

  RUN chown 1000:0 $HOME

  RUN $STARTUPDIR/set_user_permission.sh $HOME

  ENV HOME /home/kasm-user

  WORKDIR $HOME

  RUN mkdir -p $HOME && chown -R 1000:0 $HOME

  USER 1000
```

2. Set the Single App XFCE config files as your default XFCE config and remove the `xfce4-panel`

```yml
  FROM kasmweb/core-ubuntu-jammy:1.19.0-rolling-weekly

  USER root

  ENV HOME /home/kasm-default-profile

  ENV STARTUPDIR /dockerstartup

  ENV INST_SCRIPTS $STARTUPDIR/install

  WORKDIR $HOME

  ######### Customize Container Here ###########

  ## --> Update the desktop environment to be optimized for a single application

  RUN cp $HOME/.config/xfce4/xfconf/single-application-xfce-perchannel-xml/* $HOME/.config/xfce4/xfconf/xfce-perchannel-xml/

  ## --> Optionally, set a background image

  RUN cp /usr/share/backgrounds/bg_kasm.png /usr/share/backgrounds/bg_default.png

  ## --> Remove the xfce4-panel

  RUN apt-get remove -y xfce4-panel

  ######### End Customizations ###########

  RUN chown 1000:0 $HOME

  RUN $STARTUPDIR/set_user_permission.sh $HOME

  ENV HOME /home/kasm-user

  WORKDIR $HOME

  RUN mkdir -p $HOME && chown -R 1000:0 $HOME

  USER 1000
```

3. Write installation logic as a bash script to install the custom app of your choice. As an example, let’s say you want to install Discord, You can write an installation bash script like this which installs Discord and name it `install_discord.sh` (Another example [here](https://gitlab.com/kasm-technologies/internal/workspaces-images/-/blob/develop/src/ubuntu/install/chromium/install_chromium.sh?ref_type=heads)):

```bash
  #!/usr/bin/env bash

  set -ex

  # Install Discord from deb

  apt-get update

  curl -L -o discord.deb  "https://discord.com/api/download?platform=linux&format=deb"

  apt-get install -y ./discord.deb

  rm discord.deb

  # Default config values

  mkdir -p $HOME/.config/discord/

  echo '{"SKIP_HOST_UPDATE": true}' > $HOME/.config/discord/settings.json

  # Desktop file setup

  sed -i "s@Exec=/usr/share/discord/Discord@Exec=/usr/share/discord/Discord --no-sandbox@g"  /usr/share/applications/discord.desktop

  cp /usr/share/applications/discord.desktop $HOME/Desktop/

  chmod +x $HOME/Desktop/discord.desktop

  # Cleanup

  if [ -z ${SKIP_CLEAN+x} ]; then

      apt-get autoclean

      rm -rf \

          /var/lib/apt/lists/* \

          /var/tmp/* \

          /tmp/*

  fi

  # Cleanup for app layer

  chown -R 1000:0 $HOME

  find /usr/share/ -name "icon-theme.cache" -exec rm -f {} \;
```

4. Also, write a `custom_startup.sh` script that automatically launches your custom application on workspace startup (Another Example [here](https://gitlab.com/kasm-technologies/internal/workspaces-images/-/blob/develop/src/ubuntu/install/chromium/custom_startup.sh?ref_type=heads)):

```bash
  #!/usr/bin/env bash

  set -ex

  START_COMMAND="/usr/share/discord/Discord"

  PGREP="Discord"

  export MAXIMIZE="true"

  export MAXIMIZE_NAME="Discord"

  MAXIMIZE_SCRIPT=$STARTUPDIR/maximize_window.sh

  DEFAULT_ARGS="--no-sandbox"

  ARGS=${APP_ARGS:-$DEFAULT_ARGS}

  options=$(getopt -o gau: -l go,assign,url: -n "$0" -- "$@") || exit

  eval set -- "$options"

  while [[ $1 != -- ]]; do

      case $1 in

          -g|--go) GO='true'; shift 1;;

          -a|--assign) ASSIGN='true'; shift 1;;

          -u|--url) OPT_URL=$2; shift 2;;

          *) echo "bad option: $1" >&2; exit 1;;

      esac

  done

  shift

  # Process non-option arguments.

  for arg; do

      echo "arg! $arg"

  done

  FORCE=$2

  kasm_exec() {

      if [ -n "$OPT_URL" ] ; then

          URL=$OPT_URL

      elif [ -n "$1" ] ; then

          URL=$1

      fi



      # Since we are execing into a container that already has the browser running from startup,

      #  when we don't have a URL to open we want to do nothing. Otherwise a second browser instance would open.

      if [ -n "$URL" ] ; then

          /usr/bin/filter_ready

          /usr/bin/desktop_ready

          bash ${MAXIMIZE_SCRIPT} &

          $START_COMMAND $ARGS $OPT_URL

      else

          echo "No URL specified for exec command. Doing nothing."

      fi

  }

  kasm_startup() {

      if [ -n "$KASM_URL" ] ; then

          URL=$KASM_URL

      elif [ -z "$URL" ] ; then

          URL=$LAUNCH_URL

      fi

      if [ -z "$DISABLE_CUSTOM_STARTUP" ] ||  [ -n "$FORCE" ] ; then

          echo "Entering process startup loop"

          set +x

          while true

          do

              if ! pgrep -x $PGREP > /dev/null

              then

                  /usr/bin/filter_ready

                  /usr/bin/desktop_ready

                  set +e

                  bash ${MAXIMIZE_SCRIPT} &

                  $START_COMMAND $ARGS $URL &

                  set -e

              fi

              sleep 1

          done

          set -x



      fi

  }

  if [ -n "$GO" ] || [ -n "$ASSIGN" ] ; then

      kasm_exec

  else

      kasm_startup

  fi
```

Notice that in the `custom_startup.sh` script above, the `START_COMMAND` contains the command that needs to be executed to start the application. Similarly, `PGREP` contains the name of the application process (it can be a partial name of the process) so that the startup script can automatically check and re-open the application if it crashes or is closed by the user.
Similarly, you can set `MAXIMIZE` to true if you want your application to be automatically maximized. This requires that you also configure the `MAXIMIZE_WINDOW` name to match the window name of your application.

5. Copy both the install script and custom startup script to your image

```yml
  FROM kasmweb/core-ubuntu-jammy:1.19.0-rolling-weekly

  USER root

  ENV HOME /home/kasm-default-profile

  ENV STARTUPDIR /dockerstartup

  ENV INST_SCRIPTS $STARTUPDIR/install

  WORKDIR $HOME

  ######### Customize Container Here ###########

  ## Update the desktop environment to be optimized for a single application

  RUN cp $HOME/.config/xfce4/xfconf/single-application-xfce-perchannel-xml/* $HOME/.config/xfce4/xfconf/xfce-perchannel-xml/

  ## Optionally, set a background image

  RUN cp /usr/share/backgrounds/bg_kasm.png /usr/share/backgrounds/bg_default.png

  ## Remove the xfce4-panel

  RUN apt-get remove -y xfce4-panel

  ## --> Copy installation script

  COPY ./install_discord.sh $INST_SCRIPTS/discord/

  ## --> Run installation script

  RUN bash $INST_SCRIPTS/discord/install_discord.sh  && rm -rf $INST_SCRIPTS/discord/

  ## --> Copy custom_startup.sh script to the startup directory inside the image

  COPY ./custom_startup.sh $STARTUPDIR/custom_startup.sh

  ## --> Make it executable

  RUN chmod +x $STARTUPDIR/custom_startup.sh

  ## --> Set permissions

  RUN chmod 755 $STARTUPDIR/custom_startup.sh

  ######### End Customizations ###########

  RUN chown 1000:0 $HOME

  RUN $STARTUPDIR/set_user_permission.sh $HOME

  ENV HOME /home/kasm-user

  WORKDIR $HOME

  RUN mkdir -p $HOME && chown -R 1000:0 $HOME

  USER 1000
```

The script `$STARTUPDIR/custom_startup.sh` will be automatically executed on the workspace startup, thus launching the application.

6. Build the Image

```bash
  sudo docker build -t my_custom_singleapp_image -f Dockerfile .
```

## Push to Registry [​](https://docs.kasm.com/docs/how-to/workspaces-sessions/container-workspace/customization/building-images\#push-to-registry "Direct link to Push to Registry")

To simplify Image management, it is recommended to utilize a docker container registry.
This example will utilize a container registry that is provided by GitLab.

1. Login to the docker container registry. You will be prompted for a username and password. GitLab provides the ability
to create [Personal Access Tokens](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html)
with permissions that are limited to read and/or write permissions to the registry.





```bash
sudo docker login registry.gitlab.com
```

2. Build the image, using the registry location as part of the image name.





```bash
sudo docker build -t registry.gitlab.com/my-company/my-project/sublime-text:example -f Dockerfile .
```

3. Push the image to the registry





```bash
sudo docker push registry.gitlab.com/my-company/my-project/sublime-text:example
```

4. Register the image in Kasm by creating a new Workspace pointing to the docker image. Enter the gitlab
username in the **Docker Registry Username** field and the Gitlab password or access token under the **Docker Registry Password** field


![Using a Docker Container Registry](https://docs.kasm.com/assets/images/registry_image-34dd2d2e4229048cd2ea7d2b0ad9fea3.webp)

Using a Docker Container Registry

## Custom Launch Forms [​](https://docs.kasm.com/docs/how-to/workspaces-sessions/container-workspace/customization/building-images\#custom-launch-forms "Direct link to Custom Launch Forms")

It is also possible for administrators to present custom forms to users when a workspace is launched. This may
be helpful when creating more advanced turnkey solutions for a given workspace. In the following example, a form element
is presented to get an authentication key for a Tailscale VPN connection. The workspace container will then use this
key to establish the connection.

![Launch Config Form](https://docs.kasm.com/assets/images/launch_config_example_dash-1-ee29f269c9d29336b22f869e11e43db7.png)

Launch Config Form

See [Workspace Launch Forms](https://docs.kasm.com/docs/how-to/workspaces-sessions/container-workspace/workspace-launch-form#launch_form) for more details.

## Understanding `kasm-default-profile` [​](https://docs.kasm.com/docs/how-to/workspaces-sessions/container-workspace/customization/building-images\#understanding-kasm-default-profile "Direct link to understanding-kasm-default-profile")

In the Dockerfile template used above, the pre-customization steps set the `HOME` environment variable to `/home/kasm-default-profile`.

```bash
ENV HOME /home/kasm-default-profile
```

Then in the post-customizations steps, the `HOME` directory is set to `/home/kasm-user` which eventually is the profile directory used when the container starts.

```bash
ENV HOME /home/kasm-user
```

This process is done to support the [Persistent Profiles](https://docs.kasm.com/docs/how-to/data-storage/persistent-profiles) feature. When a container is not using persistent profiles
or the first time a user creates a session when persistent profiles is enabled, the `/home/kasm-user` directory will be empty. When the container starts, if the path
`/home/kasm-user` is empty, it will copy the default profile from `/home/kasm-default-profile` to `/home/kasm-user`. If persistent profiles are enabled, the
`/home/kasm-user` directory will not be empty for the user's next session.

The copy script resides within the Core images and can be adjusted if necessary. It is visible in the [workspaces-core-images Github Repo](https://github.com/kasmtech/workspaces-core-images/blob/develop/src/common/startup_scripts/kasm_default_profile.sh)

## General Docker Images [​](https://docs.kasm.com/docs/how-to/workspaces-sessions/container-workspace/customization/building-images\#general-docker-images "Direct link to General Docker Images")

Kasm Workspaces is intended primarily for UI streaming containers, however, Workspaces can also orchestrate containers using any image. Images that are not based on one of the Kasm maintained [core images](https://github.com/kasmtech/workspaces-core-images) will be incompatible with some features.

- Web Filtering
- URL Categorization
- Connecting to container through the UI

By default, Workspaces applies a restart policy to containers of 'unless-stopped', which means the container is automatically restarted unless it is manually stopped.
This may or may not be desired. To launch containers that perform a task and exit, the default restart policy must be overridden.

Workspaces will also run every container as USER 1000 unless overridden.

In the Workspaces Admin UI, navigate to Workspaces, edit the desired Workspace and in the **Docker Run Config Override (JSON)** field, set the restart policy to 'on-failure' and optionally the container user as shown here

```json
{"restart_policy":{"Name":"on-failure","MaximumRetryCount":5}, "user": "root"}
```

With this policy applied, when a user creates an instance of this image, it will be automatically removed when the container is finished running.

## Routing Image traffic through a VPN [​](https://docs.kasm.com/docs/how-to/workspaces-sessions/container-workspace/customization/building-images\#routing-image-traffic-through-a-vpn "Direct link to Routing Image traffic through a VPN")

In order to route an image's traffic through a sidecar VPN container please checkout [VPN Sidecar Containers](https://docs.kasm.com/docs/how-to/networking/vpn-sidecar).

- [Basic Build](https://docs.kasm.com/docs/how-to/workspaces-sessions/container-workspace/customization/building-images#basic-build)
- [Installing Software](https://docs.kasm.com/docs/how-to/workspaces-sessions/container-workspace/customization/building-images#installing-software)
- [Custom Startup](https://docs.kasm.com/docs/how-to/workspaces-sessions/container-workspace/customization/building-images#custom-startup)
- [Desktop Background](https://docs.kasm.com/docs/how-to/workspaces-sessions/container-workspace/customization/building-images#desktop-background)
- [Single App Workspace](https://docs.kasm.com/docs/how-to/workspaces-sessions/container-workspace/customization/building-images#single-app-workspace)
- [Push to Registry](https://docs.kasm.com/docs/how-to/workspaces-sessions/container-workspace/customization/building-images#push-to-registry)
- [Custom Launch Forms](https://docs.kasm.com/docs/how-to/workspaces-sessions/container-workspace/customization/building-images#custom-launch-forms)
- [Understanding `kasm-default-profile`](https://docs.kasm.com/docs/how-to/workspaces-sessions/container-workspace/customization/building-images#understanding-kasm-default-profile)
- [General Docker Images](https://docs.kasm.com/docs/how-to/workspaces-sessions/container-workspace/customization/building-images#general-docker-images)
- [Routing Image traffic through a VPN](https://docs.kasm.com/docs/how-to/workspaces-sessions/container-workspace/customization/building-images#routing-image-traffic-through-a-vpn)

![Live Chat Button](https://app.customgpt.ai/storage/chat_bot_avatar/RiB7Ja0mgRw0eVtj4sr5iYhGG2YrzTLaDnCU7ZBB.png)