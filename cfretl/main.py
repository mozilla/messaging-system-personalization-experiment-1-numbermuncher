import asyncio
from cfretl.asloader import ASLoader
from cfretl.remote_settings import CFRRemoteSettings
import random
import requests

DELAY = 1


def get_mock_vector():
    CFR_IDS = [
        "BOOKMARK_SYNC_CFR",
        "CRYPTOMINERS_PROTECTION",
        "CRYPTOMINERS_PROTECTION_71",
        "FACEBOOK_CONTAINER_3",
        "FACEBOOK_CONTAINER_3_72",
        "FINGERPRINTERS_PROTECTION",
        "FINGERPRINTERS_PROTECTION_71",
        "GOOGLE_TRANSLATE_3",
        "GOOGLE_TRANSLATE_3_72",
        "MILESTONE_MESSAGE",
        "PDF_URL_FFX_SEND",
        "PIN_TAB",
        "PIN_TAB_72",
        "SAVE_LOGIN",
        "SAVE_LOGIN_72",
        "SEND_RECIPE_TAB_CFR",
        "SEND_TAB_CFR",
        "SOCIAL_TRACKING_PROTECTION",
        "SOCIAL_TRACKING_PROTECTION_71",
        "WNP_MOMENTS_1",
        "WNP_MOMENTS_2",
        "WNP_MOMENTS_SYNC",
        "YOUTUBE_ENHANCE_3",
        "YOUTUBE_ENHANCE_3_72",
    ]
    return dict(zip(CFR_IDS, [random.randint(0, 16000) for i in range(len(CFR_IDS))]))


def bootstrap_test(cfr_rs):
    print("Installed CFR Control: {}".format(cfr_rs.clone_to_cfr_control(cfr_data())))
    print(
        "Installed CFR Experimetns: {}".format(
            cfr_rs.clone_to_cfr_experiment(cfr_data())
        )
    )


def cfr_data():
    return requests.get(
        "https://firefox.settings.services.mozilla.com/v1/buckets/main/collections/cfr/records"
    ).json()["data"]


async def compute_models():
    # _ = asyncio.get_running_loop()

    asloader = ASLoader()
    cfr_rs = CFRRemoteSettings()

    # This sets up the test enviroment
    bootstrap_test(cfr_rs)

    while True:
        _ = asloader.compute_vector_weights()  # noqa
        write_status = cfr_rs.write_models(get_mock_vector())
        print("Write status: {}".format(write_status))
        # Wait to run the next batch
        await asyncio.sleep(DELAY)


if __name__ == "__main__":
    asyncio.run(compute_models())
