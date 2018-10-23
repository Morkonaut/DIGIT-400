def content():
    # CMS Structure: Title, Path, Message
    APP_CONTENT = {
        "Home":[["Welcome","/welcome/","Welcome to my app, you can do many things here!"],
                ["Background","/background/","We had a lot of fun building this app. Learn more about our story."],
                ["Messages","/messages/","Get your messages from the community!"],],
        
        "Profile":[["User Profile","/profile/","Edit your profile here."],
                ["Photo Upload","/upload/","Upload your user profile photo here."],
                ["Terms of Service","/tos/","The legal stuff."],],
        
        "Contact":[["Contact Us","/contact/","Get in touch! We'd love to hear from you!"],],
    }
    return APP_CONTENT