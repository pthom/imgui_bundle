Anything in this folder will be copied to the Bundle Resources folder of the iOS app.


# Note for full screen usage on iOS

The file LaunchScreen.storyboard is a storyboard that is used to display a splash screen while the app is loading.
If used, the application will be full screen, and it will be copied to AppBundle/Resources.
  
Warning: your app may be on top of the iPhone notch. You may want to add a black top margin to your app to hide this.

To use this, you need to uncomment the key "UILaunchStoryboardName" in the Info.plist file.
