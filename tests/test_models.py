from cfretl.models import one_cfr_model
from cfretl.models import generate_cfr_model


EXPECTED = {
    "models_by_cfr_id": {
        "CFR_ID_1": {
            "feature_1": {"p_given_cfr_acceptance": 0.7, "p_given_cfr_rejection": 0.5}
        },
        "CFR_ID_2": {
            "feature_1": {
                "p_given_cfr_acceptance": 0.49,
                "p_given_cfr_rejection": 0.25,
            },
            "feature_2": {
                "p_given_cfr_acceptance": 0.49,
                "p_given_cfr_rejection": 0.25,
            },
        },
        "CFR_ID_3": {
            "feature_1": {
                "p_given_cfr_acceptance": 0.343,
                "p_given_cfr_rejection": 0.125,
            },
            "feature_2": {
                "p_given_cfr_acceptance": 0.343,
                "p_given_cfr_rejection": 0.125,
            },
            "feature_3": {
                "p_given_cfr_acceptance": 0.343,
                "p_given_cfr_rejection": 0.125,
            },
        },
        "CFR_ID_4": {
            "feature_1": {
                "p_given_cfr_acceptance": 0.2401,
                "p_given_cfr_rejection": 0.0625,
            },
            "feature_2": {
                "p_given_cfr_acceptance": 0.2401,
                "p_given_cfr_rejection": 0.0625,
            },
            "feature_3": {
                "p_given_cfr_acceptance": 0.2401,
                "p_given_cfr_rejection": 0.0625,
            },
            "feature_4": {
                "p_given_cfr_acceptance": 0.2401,
                "p_given_cfr_rejection": 0.0625,
            },
        },
        "prior_cfr": {"p_acceptance": 0.45, "p_rejection": 0.55},
    },
    "version": 123,
}


def test_one_cfr_model():
    snip = one_cfr_model("CFR_ID", "feature_x", 0.1, 0.2)
    assert snip == {
        "CFR_ID": {
            "feature_x": {"p_given_cfr_acceptance": 0.1, "p_given_cfr_rejection": 0.2}
        }
    }


def test_generate_model():

    data = []
    for i in range(1, 5):
        for f_i in range(1, 1 + i):
            rdict = {
                "id": "CFR_ID_%d" % i,
                "feature_id": "feature_%d" % f_i,
                "p0": 0.7 ** i,
                "p1": 0.5 ** i,
            }
            data.append(rdict)

    model = generate_cfr_model(data, 0.45, 0.55, 123)

    assert EXPECTED == model
