
# Outlook account creator

Python script that automatically create Outlook account



## Features

- Automated Account Creation
- Auto captcha solve (funcaptcha)
- Checking if email is already taken before creating account
- Randomly generated email and password
- HTTP proxy support
- Error Handling


## Installation

1. Clone outlook-account-creator repository from github:

```bash
  git clone https://github.com/Skuxblan/Outlook-account-creator.git
```

2. Move to project directory: 

```bash
  cd outlook-account-creator
```

3. Install the required dependencies using pip:

```bsah
pip install -r requirements.txt
```
## Usage

1. Open config.json file. It should be looking like that:

``` json
{
    "mode": 0,
    "proxy_host": "",
    "proxy_port": "",
    "username": "",
    "password": "",
    "api_key": "token_here"
}

```
2. Replace `token_here` with actual value. You should register on [Capsolver](https://www.capsolver.com/) and get token from dashboard page. 

**Note** - make sure you have positive balance on the website. If you have never used capsolver you can claim free trial.



## Run the script

```bash
py main.py
```


### (Optional) proxy configuration

Default mode is `0`
which means you won't use any proxy. If you want to use HTTP proxy with that tool you have to set it in the config file. Additionaly you have to change mode value to one of the following:

- `0` value - no proxy
- `1` value - proxy without auth
- `2` value - proxy with login and password auth
## Worth mention

- This script is dedicated for chrome browser
- Make sure you have added chromedriver to your path to avoid issues

## Tips

- If you noticed script detects SMS verification you should change your ip with proxy or wait some time.
- Capsolver sometimes is not able to do captcha correctly, especially while number of images to be processed is above norm (up to 5) you should consider changing your proxy or take a break then. If you want to check what's going on disable headless mode in `main.py` file.


## Contributing

Contributions are always welcome! If you have ideas for new features or you have any troubles feel free to opening issues or create pull requests.

## License

[MIT](https://choosealicense.com/licenses/mit/)


# Disclaimer

This script is provided for educational and informational purposes only. It was created just for fun. The author is not responsible for any misuse or violation of terms of service resulting from the use of this script. Always stick to terms of service of website you're using.
