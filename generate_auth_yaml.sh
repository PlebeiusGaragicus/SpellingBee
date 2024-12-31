#!/bin/bash

# if auth.yaml exists, warn user and exit
if [ -f auth.yaml ]; then
  echo "auth.yaml already exists. Please remove it before running this script."
  exit 1
fi

# ask for a username
echo "Enter your username:"
read username

# ask for a password
# echo "Enter your password:"
# read password # doesn't work when you run script with `sh generate_auth_yaml.sh` use `bash` instead

# python3.11 -c "import streamlit_authenticator as stauth; print(stauth.Hasher(['$password']).generate()[0])"
# import streamlit_authenticator as stauth
# print(stauth.Hasher([input("Enter password: ")]).generate()[0])


cat << EOF > auth.yaml
credentials:
  usernames:
    $username:
      email: $username@plebby.me
      name: $username
      password: typeyourpasswordhereanditwillbehashed
cookie:
  expiry_days: 7
  key: stauth_widget_key
  name: stauthwidget
preauthorized:
  emails:
    - $username@plebby.me
EOF