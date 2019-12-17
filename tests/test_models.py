import random
from cfretl.models import CFRModel

random.seed(42)


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
    model = CFRModel()
    snip = model.one_cfr("CFR_ID", [0.45, 0.55], [[1, 2, 3], [4, 5, 6]])

    expected = {
        "CFR_ID": {
            "priors": [0.45, 0.55],
            "negProbs": [[1, 2, 3], [4, 5, 6]],
            "delProbs": [[1, 4], [2, 5], [3, 6]],
        }
    }
    assert snip == expected


def test_generate_model():

    model = CFRModel()

    data = []
    for cfr_idx in range(1, 5):
        p = random.random()
        snip = model.one_cfr(
            "CFR_ID_{}".format(cfr_idx),
            [p, 1 - p],
            [
                [1 * cfr_idx, 2 * cfr_idx, 3 * cfr_idx],
                [4 * cfr_idx, 5 * cfr_idx, 6 * cfr_idx],
            ],
        )
        data.append(snip)

    json_out = model.generate_cfr_model(data, 123)
    expected = {
        "version": 123,
        "models_by_cfr_id": {
            "CFR_ID_1": {
                "priors": [0.6394267984578837, 0.36057320154211625],
                "negProbs": [[1, 2, 3], [4, 5, 6]],
                "delProbs": [[1, 4], [2, 5], [3, 6]],
            },
            "CFR_ID_2": {
                "priors": [0.025010755222666936, 0.9749892447773331],
                "negProbs": [[2, 4, 6], [8, 10, 12]],
                "delProbs": [[2, 8], [4, 10], [6, 12]],
            },
            "CFR_ID_3": {
                "priors": [0.27502931836911926, 0.7249706816308807],
                "negProbs": [[3, 6, 9], [12, 15, 18]],
                "delProbs": [[3, 12], [6, 15], [9, 18]],
            },
            "CFR_ID_4": {
                "priors": [0.22321073814882275, 0.7767892618511772],
                "negProbs": [[4, 8, 12], [16, 20, 24]],
                "delProbs": [[4, 16], [8, 20], [12, 24]],
            },
        },
    }

    assert json_out == expected
