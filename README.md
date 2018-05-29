# PyInfoNotify
PyInfoNotify is a program written in Python to notify you about anything you can create a provider for, it was written for Linux.

## Installation
You will need Python 3.6 and `pip`, which can be installed on Debian based systems like this:
```
# apt install python3.6 python3-pip
```
After that you need to install some python packages:
```
$ pip3 install certifi lxml notify2 simpleaudio urllib3 bs4
```
Finally download this repository, and run `./pyinfonotify.py`, the first run will create the configuration file.

### Configuration
The configuration is stored in `~/.inforc` in an `ini` format.

It looks somthing like this after the first run:
```ini
[providers]
enabled = 
sound = 

[notifications]
html = False
timeout = 5000

; All provider specific configurations
```

#### Providers
To enable providers, add the name to the `enabled` key. The name is the filename of the provider without the `.py`. Look in the `providers` directory to see which providers exist, `__init__.py` and `provider.py` are not providers.

You can also add the provider name to the `sound` key if you want a notification sound (this requires a `.wav` inside the `resources` directory)


#### Notifications
If you set `html` to `True` the notification will be allowed to use advanced HTML, this will be harder on you computer, but will probably look a lot better. Your notification server also needs to support advanced HTML for this.

`timeout` is how long the notification is visible, in milliseconds.


## Creating providers
To create a new provider, add a new file in the `providers` directory, the name of the file can not contain spaces, or be any of the following:

- `__init__.py`
- `provider.py`
- `providers.py`
- `notifications.py`

Inside the file place the following code as base:
```python
from providers import provider

class Provider(provider.Base):
    def get_config(self):
        return { }


    def init(self):
        self.name = ''
        self.delay = ''

        return True


    def check(self):

```

##### get_config()
The `get_config` function contains the configuration keys and default values of the provider, you can use a `;` to create a comment inside the configuration file.

This dictionary
```python
{
    '; letter': 'A letter to display',
    'letter': 'a'
}
```
will create this in the configuration file
```ini
[letters]
; letter = A letter to display
letter = a
```


##### init()
The `init` function has to contain the name to display (`self.name`) and the time between checks (`self.delay`). The display name can be anything you want and will show up as title of the notification, it is also the filename of the icon and the notification sound of the provider. So setting the name to `Letters` will need a file `Letters.png` for the icon and `Letters.wav` for the notification sound inside the `resources` directory.

The delay is set using a string containing numbers and units, allowed units are:

- `h` (hours)
- `m` (minutes)
- `s` (seconds)
- `ms` (milliseconds)

So a delay like `1h 30m` will make the provider check every 90 minutes.


##### check()
The `check` function is called every time after a delay and when the program starts. Inside the check function you can do whatever you want to create notifications. If you want to get the HTML of a webpage you can use `self.get_html(url)` this will return a BeautifulSoup object so you can go parsing it directly.

You can use `self.data[key]` to get a configuration value from the keys you defined in the `get_config` function. You can also use `self.data['html'] == 'True'` to check if advanced HTML notifications are enabled, simple HTML notifications are allowed to use the following HTML tags:

- `<b>`
- `<i>`
- `<u>`
- `<a href="">`
- `<img src="file://" alt="">`

You can alse call `int(self.data['timeout'])` to get the notification timeout.

After you generated the body of the notification, call `self.notifications.append(body)` to show it to the user. You are not allowed to show a previously shown notification again, unless you call `self.hashes.clear()`.

To print to the terminal, you should use `self.log(message)`.

Any required images or other resources should be placed inside the `resource` directory, they can be accessed using `'file:// ' + self.resource_path + 'image.png'`.


## Provided providers
### NS
A provider to show disruptions, maintenance and alerts from the _Nederlandse Spoorwegen_(_Dutch Railroads_).

Configuration:

- `filter` is used to filter disruptions/maintenance on city.
- `maintenance` will disable maintenance notifications if `False`.
- `alerts` will disable country wide alerts if `False`.


### NOS
A provider to show notifications about _NOS_ livestreams (Dutch news).

Configuration:

- `images` will download and resize images if the livestream update contains one (requires `PIL`).
- `limit` is used to only show the last `n` updates, for often updated livestreams.
- `exclude` is used to disable certain categories of livestreams.


### KNMI
A provider to show warnings about the weather from the _Koninklijk Nederlands Meteorologisch Instituut_(_Royal Netherlands Meteorological Institute_).

Configuration:

- `province` is the province to show warnings for.
