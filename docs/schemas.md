The CFR weight vector schema is computed by using the current set of
CFR message IDs as keys and an integer value in a hashmap.

```json
{'BOOKMARK_SYNC_CFR': 10476,
 'CRYPTOMINERS_PROTECTION': 1824,
 'CRYPTOMINERS_PROTECTION_71': 409,
 'FACEBOOK_CONTAINER_3': 12149,
 'FACEBOOK_CONTAINER_3_72': 4506,
 'FINGERPRINTERS_PROTECTION': 4012,
 'FINGERPRINTERS_PROTECTION_71': 3657,
 'GOOGLE_TRANSLATE_3': 2286,
 'GOOGLE_TRANSLATE_3_72': 12066,
 'MILESTONE_MESSAGE': 1679,
 'PDF_URL_FFX_SEND': 11087,
 'PIN_TAB': 12135,
 'PIN_TAB_72': 14617,
 'SAVE_LOGIN': 8935,
 'SAVE_LOGIN_72': 1424,
 'SEND_RECIPE_TAB_CFR': 9674,
 'SEND_TAB_CFR': 6912,
 'SOCIAL_TRACKING_PROTECTION': 520,
 'SOCIAL_TRACKING_PROTECTION_71': 488,
 'WNP_MOMENTS_1': 1535,
 'WNP_MOMENTS_2': 3582,
 'WNP_MOMENTS_SYNC': 3811,
 'YOUTUBE_ENHANCE_3': 8279,
 'YOUTUBE_ENHANCE_3_72': 9863}
```

The JSON schema is computed using https://jsonschema.net/

Note that the schema generated will enforce the length of the vector
as each CFR Message ID a required key in the JSON blob that is
returned.

