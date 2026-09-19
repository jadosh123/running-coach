from getpass import getpass
from garminconnect import Garmin, GarminConnectAuthenticationError, GarminConnectTooManyRequestsError, GarminConnectConnectionError

TOKEN_DIR = "~/.garminconnect"


def get_client() -> Garmin:
    client = Garmin()
    try:
        client.login(TOKEN_DIR)
    except GarminConnectAuthenticationError:
        raise RuntimeError("Not logged in to Garmin. Run the login command first.")
    return client


def login() -> Garmin:
    client = Garmin(
        input("Garmin Email: "),
        getpass("Garmin password: "),
        prompt_mfa=lambda: input("MFA code: "),
    )
    client.login("~/.garminconnect")
    return client


def main():
    try:
        login()
    except GarminConnectAuthenticationError:
        print("Login failed: check your email, password, and MFA code.")
    except GarminConnectTooManyRequestsError:
        print("Garmin is rate limiting login attempts. Wait a while and try again.")
    except GarminConnectConnectionError:
        print("Could not reach Garmin. Check your connection and try again.")
    else:
        print("Logged in. Tokens saved.")


if __name__ == "__main__":
    main()